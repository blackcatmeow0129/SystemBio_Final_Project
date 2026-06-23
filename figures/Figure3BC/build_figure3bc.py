from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


EXPECTED_COMBINATIONS = {1: 7, 2: 21, 3: 35, 4: 35, 5: 21, 6: 7, 7: 1}
COLORS = {
    1: "#9DB8DE",
    2: "#E87513",
    3: "#4169A1",
    4: "#70AD47",
    5: "#00A6C6",
    6: "#8C8C8C",
    7: "#8064A2",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge Figure 3 no-self fits and reproduce panels B/C")
    parser.add_argument("--forward-results", type=Path, required=True)
    parser.add_argument("--reverse-results", type=Path, required=True)
    parser.add_argument("--supplementary-json", type=Path, required=True)
    parser.add_argument("--multi-hit-fasta", type=Path, required=True)
    parser.add_argument("--transcpp", type=Path, required=True)
    parser.add_argument("--runtime-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--runs", type=int, default=4)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--parallel", type=int, default=4)
    return parser.parse_args()


def read_summary(results_dir: Path) -> list[dict[str, str]]:
    path = results_dir / "summary.tsv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def run_dir(results_dir: Path, row: dict[str, str]) -> Path:
    return (
        results_dir
        / f"{int(row['tf_count'])}TF"
        / row["combination"]
        / f"run_{int(row['run']):02d}_seed_{int(row['seed'])}"
    )


def valid_candidates(results_dir: Path, source: str, runs: int) -> tuple[dict[int, dict[int, dict]], list[str]]:
    grouped: dict[int, dict[int, dict]] = defaultdict(dict)
    problems: list[str] = []
    for row in read_summary(results_dir):
        if row.get("status") != "completed":
            continue
        run = int(row["run"])
        if run > runs:
            continue
        index = int(row["combination_index"])
        directory = run_dir(results_dir, row)
        fit_xml = directory / "fit.xml"
        rates = directory / "fit.output.rates"
        if not fit_xml.exists() or not rates.exists():
            problems.append(f"{source}: missing fit.xml/rates for combination {index}, run {run}")
            continue
        try:
            has_output = ET.parse(fit_xml).getroot().find("Output") is not None
        except Exception as exc:
            problems.append(f"{source}: invalid fit.xml for combination {index}, run {run}: {exc}")
            continue
        if not has_output:
            problems.append(f"{source}: fit.xml has no Output for combination {index}, run {run}")
            continue
        grouped[index][run] = {
            "source": source,
            "results_dir": str(results_dir),
            "combination_index": index,
            "tf_count": int(row["tf_count"]),
            "combination": row["combination"],
            "run": run,
            "seed": int(row["seed"]),
            "final_score": row.get("final_score", ""),
            "elapsed": row.get("elapsed", ""),
            "fit_xml": fit_xml,
            "single_hit_rates": rates,
        }
    return grouped, problems


def select_runs(forward: dict[int, dict[int, dict]], reverse: dict[int, dict[int, dict]], runs: int) -> tuple[list[dict], list[str]]:
    selected: list[dict] = []
    notes: list[str] = []
    wanted = set(range(1, runs + 1))
    for index in range(1, 128):
        forward_runs = forward.get(index, {})
        reverse_runs = reverse.get(index, {})
        if set(forward_runs) >= wanted:
            chosen = forward_runs
            source_note = "forward"
        elif set(reverse_runs) >= wanted:
            chosen = reverse_runs
            source_note = "reverse"
        else:
            chosen = {}
            for run in range(1, runs + 1):
                if run in forward_runs:
                    chosen[run] = forward_runs[run]
                elif run in reverse_runs:
                    chosen[run] = reverse_runs[run]
            source_note = "mixed"
        if set(chosen) != wanted:
            missing = sorted(wanted - set(chosen))
            raise RuntimeError(f"Combination {index} is missing completed runs: {missing}")
        identities = {(item["tf_count"], item["combination"]) for item in chosen.values()}
        if len(identities) != 1:
            raise RuntimeError(f"Combination {index} has inconsistent TF identities: {sorted(identities)}")
        selected.extend(chosen[run] for run in range(1, runs + 1))
        notes.append(f"{index}\t{source_note}\t{','.join(str(run) for run in sorted(chosen))}")

    if len(selected) != 127 * runs:
        raise RuntimeError(f"Expected {127 * runs} selected runs, found {len(selected)}")
    combination_counts = Counter(item["tf_count"] for item in selected[::runs])
    if dict(sorted(combination_counts.items())) != EXPECTED_COMBINATIONS:
        raise RuntimeError(f"Unexpected combination counts: {dict(sorted(combination_counts.items()))}")
    return selected, notes


def read_rates(path: Path) -> dict[str, float]:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        text = raw.decode("utf-16")
    else:
        text = raw.decode("utf-8", errors="replace")
    rows = [line.split() for line in text.splitlines() if line.strip()]
    if len(rows) < 2:
        raise ValueError(f"Rates file has fewer than two rows: {path}")
    names = rows[0][1:]
    values = rows[1][1:]
    if len(names) != len(values):
        raise ValueError(f"Rates header/value mismatch in {path}: {len(names)} != {len(values)}")
    return {name: float(value) for name, value in zip(names, values)}


def read_single_observed(path: Path) -> dict[str, float]:
    root = ET.parse(path).getroot()
    row = root.find("./Input/RateData/TableRow")
    if row is None:
        raise ValueError(f"Input/RateData/TableRow missing: {path}")
    return {name: float(value) for name, value in row.attrib.items() if name != "ID"}


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Pearson inputs must have equal length >= 2")
    mean_x = statistics.fmean(x)
    mean_y = statistics.fmean(y)
    dx = [value - mean_x for value in x]
    dy = [value - mean_y for value in y]
    denominator = math.sqrt(sum(value * value for value in dx) * sum(value * value for value in dy))
    if denominator == 0:
        return float("nan")
    return sum(a * b for a, b in zip(dx, dy)) / denominator


def log2_values(values: list[float]) -> list[float]:
    if any(value <= 0 for value in values):
        raise ValueError("Correlation input contains a non-positive value")
    return [math.log2(value) for value in values]


def compute_single_hit(item: dict) -> float:
    observed = read_single_observed(item["fit_xml"])
    predicted = read_rates(item["single_hit_rates"])
    names = [name for name in observed if not name.startswith("synCRE_Promega_0")]
    if len(names) != 260:
        raise ValueError(f"Expected 260 published substitutions, found {len(names)} in {item['fit_xml']}")
    missing = [name for name in names if name not in predicted]
    if missing:
        raise ValueError(f"Single-hit predictions missing {len(missing)} records")
    return pearson(log2_values([observed[name] for name in names]), log2_values([predicted[name] for name in names]))


def read_multi_hit_records(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["multiHit"]
    header = {str(value): index for index, value in enumerate(rows[0])}
    records = [
        {
            "name": str(row[header["name"]]),
            "sequence": str(row[header["sequence"]]).upper(),
            "expression": float(row[header["expression level"]]),
        }
        for row in rows[1:]
    ]
    if len(records) != 722:
        raise ValueError(f"Expected WT plus 721 multi-hit variants, found {len(records)}")
    return records


def read_fasta_names(path: Path) -> list[str]:
    return [line[1:].strip() for line in path.read_text(encoding="ascii").splitlines() if line.startswith(">")]


def freeze_parameters(node: ET.Element) -> None:
    for element in node.iter():
        if "anneal" in element.attrib:
            element.set("anneal", "false")


def set_threads(root: ET.Element, threads: int) -> None:
    mode = root.find("Mode")
    if mode is None:
        raise ValueError("Mode section missing")
    node = mode.find("NumThreads")
    if node is None:
        node = ET.SubElement(mode, "NumThreads")
    node.set("value", str(threads))


def make_multi_hit_xml(fit_xml: Path, target: Path, fasta: Path, records: list[dict[str, object]], threads: int) -> None:
    tree = ET.parse(fit_xml)
    root = tree.getroot()
    original_input = root.find("Input")
    fitted = root.find("Output")
    if original_input is None or fitted is None:
        raise ValueError(f"Completed fit lacks Input/Output: {fit_xml}")

    new_input = copy.deepcopy(fitted)
    new_input.tag = "Input"
    freeze_parameters(new_input)
    if new_input.find("ScaleFactors") is None:
        scale_factors = original_input.find("ScaleFactors")
        if scale_factors is not None:
            new_input.append(copy.deepcopy(scale_factors))

    genes = new_input.find("Genes")
    if genes is None:
        genes = ET.SubElement(new_input, "Genes")
    else:
        genes.clear()
    source = ET.SubElement(genes, "Source", {"name": "multi_hit", "file": fasta.as_posix(), "type": "fasta"})
    for record in records:
        name = str(record["name"])
        ET.SubElement(
            source,
            "Gene",
            {
                "name": name,
                "header": name,
                "left_bound": "-235",
                "right_bound": "-38",
                "TSS": "-1",
                "promoter": "basic",
            },
        )

    rate_data = new_input.find("RateData")
    if rate_data is None:
        rate_data = ET.SubElement(new_input, "RateData")
    rate_data.clear()
    rate_data.attrib.update({"row": "ID", "col": "gene"})
    table_values = {"ID": "theonlyone"}
    table_values.update({str(record["name"]): "0" for record in records})
    ET.SubElement(rate_data, "TableRow", table_values)

    new_output = copy.deepcopy(new_input)
    new_output.tag = "Output"
    root.remove(original_input)
    root.remove(fitted)
    root.append(new_input)
    root.append(new_output)
    set_threads(root, threads)
    try:
        ET.indent(tree, space="  ")
    except AttributeError:
        pass
    target.parent.mkdir(parents=True, exist_ok=True)
    tree.write(target, encoding="utf-8", xml_declaration=True)


def multi_hit_rate_path(output_dir: Path, item: dict) -> Path:
    safe_combo = item["combination"]
    return output_dir / "multi_hit_rates" / f"{item['tf_count']}TF" / safe_combo / f"run_{item['run']:02d}.rates.tsv"


def predict_multi_hit(
    item: dict,
    output_dir: Path,
    records: list[dict[str, object]],
    fasta: Path,
    transcpp: Path,
    runtime_dir: Path,
    threads: int,
) -> tuple[Path, bool]:
    rates_path = multi_hit_rate_path(output_dir, item)
    if rates_path.exists():
        rates = read_rates(rates_path)
        if len(rates) == len(records):
            return rates_path, True

    work_dir = output_dir / "multi_hit_work"
    work_dir.mkdir(parents=True, exist_ok=True)
    xml_path = work_dir / f"combination_{item['combination_index']:03d}_run_{item['run']:02d}.xml"
    make_multi_hit_xml(item["fit_xml"], xml_path, fasta, records, threads)
    environment = os.environ.copy()
    environment["PATH"] = str(runtime_dir) + os.pathsep + environment.get("PATH", "")
    environment["OMP_NUM_THREADS"] = str(threads)
    completed = subprocess.run(
        [str(transcpp), "--print-output-rates", str(xml_path)],
        cwd=work_dir,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        error_path = xml_path.with_suffix(".stderr.log")
        error_path.write_bytes(completed.stderr)
        raise RuntimeError(f"transcpp failed for combination {item['combination_index']} run {item['run']}: {error_path}")
    rates_path.parent.mkdir(parents=True, exist_ok=True)
    rates_path.write_bytes(completed.stdout)
    xml_path.unlink(missing_ok=True)
    parsed = read_rates(rates_path)
    if len(parsed) != len(records):
        raise ValueError(f"Expected {len(records)} multi-hit predictions, found {len(parsed)} in {rates_path}")
    return rates_path, False


def compute_multi_hit(records: list[dict[str, object]], rates_path: Path) -> float:
    predicted = read_rates(rates_path)
    names = [str(record["name"]) for record in records]
    missing = [name for name in names if name not in predicted]
    if missing:
        raise ValueError(f"Multi-hit predictions missing {len(missing)} records")
    baseline_expression = float(records[0]["expression"])
    baseline_rate = predicted[names[0]]
    observed = [math.log2(float(record["expression"]) / baseline_expression) for record in records]
    estimated = [math.log2(predicted[name] / baseline_rate) for name in names]
    return pearson(observed, estimated)


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def quartile_outliers(values: list[float]) -> list[float]:
    if len(values) < 4:
        return []
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    iqr = q3 - q1
    return [value for value in values if value < q1 - 1.5 * iqr or value > q3 + 1.5 * iqr]


def draw_panel(axis: plt.Axes, rows: list[dict], metric: str, label: str) -> None:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[int(row["tf_count"])].append(float(row[metric]))
    data = [grouped[size] for size in range(1, 8)]
    boxplot = axis.boxplot(
        data,
        positions=list(range(1, 8)),
        widths=0.58,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "white", "linewidth": 2.0},
        whiskerprops={"linewidth": 1.25},
        capprops={"linewidth": 1.25},
    )
    for size, box in enumerate(boxplot["boxes"], start=1):
        box.set_facecolor(COLORS[size])
        box.set_edgecolor(COLORS[size])
        box.set_alpha(0.96)
    for index, size in enumerate(range(1, 8)):
        color = COLORS[size]
        for whisker in boxplot["whiskers"][2 * index : 2 * index + 2]:
            whisker.set_color(color)
        for cap in boxplot["caps"][2 * index : 2 * index + 2]:
            cap.set_color(color)
        outliers = quartile_outliers(grouped[size])
        if outliers:
            axis.scatter([size] * len(outliers), outliers, s=14, color=color, edgecolors="none", zorder=4)
        axis.scatter(size, statistics.fmean(grouped[size]), s=19, color="black", zorder=5)
    axis.set_xlim(0.5, 7.5)
    axis.set_ylim(-0.4, 1.05)
    axis.set_xticks(range(1, 8))
    axis.set_xlabel("number of TFs", fontsize=12)
    axis.set_ylabel("Pearson's R", fontsize=12)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(False)
    axis.text(-0.12, 1.02, label, transform=axis.transAxes, fontsize=19, fontweight="bold")


def save_figures(output_dir: Path, rows: list[dict]) -> None:
    for metric, label, name in (
        ("single_hit_r", "B", "Figure3B"),
        ("multi_hit_r", "C", "Figure3C"),
    ):
        figure, axis = plt.subplots(figsize=(6.5, 5.4), dpi=180)
        draw_panel(axis, rows, metric, label)
        figure.tight_layout()
        for suffix in ("png", "pdf", "svg"):
            figure.savefig(output_dir / f"{name}.{suffix}", dpi=300 if suffix == "png" else None, bbox_inches="tight", facecolor="white")
        plt.close(figure)

    figure, axes = plt.subplots(1, 2, figsize=(12.4, 5.3), dpi=180)
    draw_panel(axes[0], rows, "single_hit_r", "B")
    draw_panel(axes[1], rows, "multi_hit_r", "C")
    figure.subplots_adjust(left=0.07, right=0.99, top=0.96, bottom=0.14, wspace=0.30)
    for suffix in ("png", "pdf", "svg"):
        figure.savefig(output_dir / f"Figure3_BC.{suffix}", dpi=300 if suffix == "png" else None, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def summarize(rows: list[dict], metric: str, panel: str) -> list[dict]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[int(row["tf_count"])].append(float(row[metric]))
    output = []
    for size in range(1, 8):
        values = grouped[size]
        q1, median, q3 = statistics.quantiles(values, n=4, method="inclusive")
        output.append(
            {
                "panel": panel,
                "tf_count": size,
                "n_runs": len(values),
                "mean_r": f"{statistics.fmean(values):.10f}",
                "median_r": f"{median:.10f}",
                "q1_r": f"{q1:.10f}",
                "q3_r": f"{q3:.10f}",
                "min_r": f"{min(values):.10f}",
                "max_r": f"{max(values):.10f}",
            }
        )
    return output


def main() -> None:
    args = parse_args()
    args.forward_results = args.forward_results.resolve()
    args.reverse_results = args.reverse_results.resolve()
    args.supplementary_json = args.supplementary_json.resolve()
    args.multi_hit_fasta = args.multi_hit_fasta.resolve()
    args.transcpp = args.transcpp.resolve()
    args.runtime_dir = args.runtime_dir.resolve()
    args.output_dir = args.output_dir.resolve()
    for path in (
        args.forward_results,
        args.reverse_results,
        args.supplementary_json,
        args.multi_hit_fasta,
        args.transcpp,
        args.runtime_dir,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    forward, forward_problems = valid_candidates(args.forward_results, "forward", args.runs)
    reverse, reverse_problems = valid_candidates(args.reverse_results, "reverse", args.runs)
    selected, selection_notes = select_runs(forward, reverse, args.runs)

    source_counts = Counter(item["source"] for item in selected)
    print(f"Selected fits: {len(selected)}; sources={dict(source_counts)}")

    for item in selected:
        item["single_hit_r"] = compute_single_hit(item)

    records = read_multi_hit_records(args.supplementary_json)
    fasta_names = read_fasta_names(args.multi_hit_fasta)
    record_names = [str(record["name"]) for record in records]
    if fasta_names != record_names:
        raise RuntimeError("multi_hit.fa record order/names differ from official mmc4 multi-hit sheet")

    completed_count = 0
    cached_count = 0
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        future_map = {
            executor.submit(
                predict_multi_hit,
                item,
                args.output_dir,
                records,
                args.multi_hit_fasta.resolve(),
                args.transcpp.resolve(),
                args.runtime_dir.resolve(),
                args.threads,
            ): item
            for item in selected
        }
        for future in as_completed(future_map):
            item = future_map[future]
            rates_path, cached = future.result()
            item["multi_hit_rates"] = rates_path
            item["multi_hit_r"] = compute_multi_hit(records, rates_path)
            completed_count += 1
            cached_count += int(cached)
            if completed_count % 25 == 0 or completed_count == len(selected):
                print(f"Multi-hit predictions: {completed_count}/{len(selected)} (cached={cached_count})", flush=True)

    rows = sorted(selected, key=lambda item: (item["combination_index"], item["run"]))
    correlation_rows = []
    for item in rows:
        correlation_rows.append(
            {
                **item,
                "single_hit_r": f"{float(item['single_hit_r']):.10f}",
                "multi_hit_r": f"{float(item['multi_hit_r']):.10f}",
                "fit_xml": str(item["fit_xml"]),
                "single_hit_rates": str(item["single_hit_rates"]),
                "multi_hit_rates": str(item["multi_hit_rates"]),
            }
        )
    fields = [
        "combination_index",
        "tf_count",
        "combination",
        "run",
        "seed",
        "source",
        "final_score",
        "elapsed",
        "single_hit_r",
        "multi_hit_r",
        "fit_xml",
        "single_hit_rates",
        "multi_hit_rates",
    ]
    write_tsv(args.output_dir / "Figure3BC_run_correlations.tsv", correlation_rows, fields)

    summary_rows = summarize(rows, "single_hit_r", "B") + summarize(rows, "multi_hit_r", "C")
    write_tsv(
        args.output_dir / "Figure3BC_group_statistics.tsv",
        summary_rows,
        ["panel", "tf_count", "n_runs", "mean_r", "median_r", "q1_r", "q3_r", "min_r", "max_r"],
    )

    manifest_rows = [
        {
            "combination_index": item["combination_index"],
            "tf_count": item["tf_count"],
            "combination": item["combination"],
            "run": item["run"],
            "seed": item["seed"],
            "source": item["source"],
            "fit_xml": str(item["fit_xml"]),
            "single_hit_rates": str(item["single_hit_rates"]),
        }
        for item in rows
    ]
    write_tsv(
        args.output_dir / "selected_fit_manifest.tsv",
        manifest_rows,
        ["combination_index", "tf_count", "combination", "run", "seed", "source", "fit_xml", "single_hit_rates"],
    )
    (args.output_dir / "combination_source_selection.tsv").write_text(
        "combination_index\tsource\truns\n" + "\n".join(selection_notes) + "\n", encoding="utf-8"
    )

    save_figures(args.output_dir, rows)

    by_tf = {size: EXPECTED_COMBINATIONS[size] * args.runs for size in range(1, 8)}
    report = [
        "# Figure 3B/3C merged reproduction",
        "",
        f"- Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Forward results: `{args.forward_results}`",
        f"- Reverse results: `{args.reverse_results}`",
        f"- Selected completed fits: {len(rows)} (127 TF combinations x {args.runs} runs)",
        f"- Selected source counts: {dict(source_counts)}",
        f"- Expected runs by TF count: {by_tf}",
        f"- Forward audit problems ignored after fallback: {len(forward_problems)}",
        f"- Reverse audit problems ignored after fallback: {len(reverse_problems)}",
        f"- Multi-hit records: {len(records)} (WT + {len(records) - 1} filtered multi-hit variants)",
        f"- Multi-hit forward workers: {args.parallel} processes x {args.threads} OpenMP threads",
        "",
        "## Methods",
        "",
        "- Figure 3B: Pearson correlation between log2 fitted rate and log2 experimental expression for the 260 published single-hit substitutions; WT excluded.",
        "- Figure 3C: the same fitted parameters were frozen and applied to the official mmc4 multi-hit sequences; Pearson correlation used log2 ratios relative to WT and includes WT, matching the existing Figure 4 multi-hit calculation.",
        "- No multi-hit fitting or scrambling was performed.",
        "- For a TF combination completed by both laptops, the forward-laptop set was selected when all runs 1-4 were available; otherwise the reverse-laptop set filled the combination.",
        "",
        "## Reproduction limitations",
        "",
        "- The paper trained 8 starts per TF combination; this reproduction uses 4 starts because of the submission deadline.",
        "- The paper's exact random seeds and initial parameter vectors were not published.",
        "- Official Table S3 omits C1T, so Figure 3B uses the 260 available single-hit substitutions.",
        "",
        "## Outputs",
        "",
        "- Figure3B.png/pdf/svg",
        "- Figure3C.png/pdf/svg",
        "- Figure3_BC.png/pdf/svg",
        "- Figure3BC_run_correlations.tsv",
        "- Figure3BC_group_statistics.tsv",
        "- selected_fit_manifest.tsv",
        "- combination_source_selection.tsv",
    ]
    if forward_problems or reverse_problems:
        report.extend(["", "## Audit notes", ""])
        report.extend(f"- {problem}" for problem in forward_problems + reverse_problems)
    (args.output_dir / "README.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Outputs: {args.output_dir}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
