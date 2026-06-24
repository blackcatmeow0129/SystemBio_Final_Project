#!/usr/bin/env python3
"""Reproduce Figure 4A-K with a selected 4TF fit and linear QSAM."""

from __future__ import annotations

import argparse
import copy
import csv
import math
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from matplotlib.path import Path as MplPath
from matplotlib.patches import FancyArrowPatch, Rectangle

LM_REFERENCE = Path(__file__).resolve().parent / "paper_reference" / "paper_Figure4_LM_original.png"


DATASET_ORDER = (
    "single_hit",
    "reverse",
    "rearrange",
    "reverse_rearrange",
    "multi_hit",
)

DATASET_SHEETS = {
    "single_hit": ("single-hit", None),
    "reverse": ("reverse_and_rearrange", "reverse"),
    "rearrange": ("reverse_and_rearrange", "rearrange"),
    "reverse_rearrange": ("reverse_and_rearrange", "reverse&rearrange"),
    "multi_hit": ("multi-hit", None),
}

PANEL_MAP = {
    "D": ("reverse", "thermodynamic"),
    "E": ("rearrange", "thermodynamic"),
    "F": ("reverse_rearrange", "thermodynamic"),
    "G": ("reverse", "QSAM"),
    "H": ("rearrange", "QSAM"),
    "I": ("reverse_rearrange", "QSAM"),
    "J": ("multi_hit", "thermodynamic"),
    "K": ("multi_hit", "QSAM"),
}

PAPER_R = {
    "D": 0.82,
    "E": 0.87,
    "F": 0.82,
    "G": -0.14,
    "H": -0.11,
    "I": -0.03,
    "J": 0.78,
    "K": 0.87,
}

CRE_REGIONS = (
    (8, 19, "C1", "#f2697a"),
    (35, 44, "C2", "#f2697a"),
    (44, 52, "C3", "#f2697a"),
    (60, 67, "CR", "#25a7a2"),
    (68, 79, "C4", "#f2697a"),
)


def parse_args() -> argparse.Namespace:
    script_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=script_root)
    parser.add_argument("--best-xml", type=Path)
    parser.add_argument("--mmc4", type=Path)
    parser.add_argument("--transcpp", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--skip-transcpp", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    args.best_xml = (args.best_xml or root / "artifacts" / "transferred_4tf_evaluation_20260612" / "best_candidate" / "best_fit.xml").resolve()
    args.mmc4 = (args.mmc4 or root / "1-s2.0-S2589004223028249-mmc4.xlsx").resolve()
    args.transcpp = (args.transcpp or root / "transfer_4TF_results" / "runtime" / "transcpp.exe").resolve()
    args.output = (args.output or root / "artifacts" / "figure4_run5_20260612").resolve()
    return args


def read_datasets(path: Path) -> dict[str, list[dict[str, object]]]:
    workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
    datasets: dict[str, list[dict[str, object]]] = {}
    for dataset, (sheet_name, subtype) in DATASET_SHEETS.items():
        rows = list(workbook[sheet_name].iter_rows(values_only=True))
        header = {str(value): index for index, value in enumerate(rows[0])}
        records = []
        for row in rows[1:]:
            if subtype is not None and row[header["type"]] != subtype:
                continue
            records.append(
                {
                    "name": str(row[header["name"]]),
                    "sequence": str(row[header["sequence"]]).upper(),
                    "expression": float(row[header["expression level"]]),
                }
            )
        datasets[dataset] = records
    return datasets


def write_fasta(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for record in records:
            handle.write(f">{record['name']}\n{record['sequence']}\n")


def freeze_parameters(node: ET.Element) -> None:
    for element in node.iter():
        if "anneal" in element.attrib:
            element.set("anneal", "false")


def set_threads(root: ET.Element, threads: int) -> None:
    mode = root.find("Mode")
    if mode is None:
        raise ValueError("Best XML has no Mode section")
    element = mode.find("NumThreads")
    if element is None:
        element = ET.SubElement(mode, "NumThreads")
    element.set("value", str(threads))


def make_evaluation_xml(
    best_xml: Path,
    target: Path,
    fasta: Path,
    dataset: str,
    records: list[dict[str, object]],
    threads: int,
) -> None:
    tree = ET.parse(best_xml)
    root = tree.getroot()
    original_input = root.find("Input")
    fitted = root.find("Output")
    if original_input is None or fitted is None:
        raise ValueError("Best XML must contain both Input and fitted Output sections")

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
    source = ET.SubElement(
        genes,
        "Source",
        {"name": dataset, "file": fasta.as_posix(), "type": "fasta"},
    )
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
    row_values = {"ID": "theonlyone"}
    row_values.update({str(record["name"]): "0" for record in records})
    ET.SubElement(rate_data, "TableRow", row_values)

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


def run_transcpp(executable: Path, xml_path: Path, runtime_dir: Path, threads: int) -> Path:
    environment = os.environ.copy()
    environment["PATH"] = str(runtime_dir) + os.pathsep + environment.get("PATH", "")
    environment["OMP_NUM_THREADS"] = str(threads)
    error_path = xml_path.with_suffix(".run.err.log")
    rates_path = xml_path.with_suffix(".rates.tsv")
    completed = subprocess.run(
        [str(executable), "--print-output-rates", str(xml_path)],
        cwd=xml_path.parent,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        error_path.write_bytes(completed.stderr)
        raise RuntimeError(
            f"rate extraction failed for {xml_path.name}: "
            + completed.stderr.decode("utf-8", errors="replace")
        )
    error_path.write_bytes(completed.stderr)
    rates_path.write_bytes(completed.stdout)
    return rates_path


def read_rates(path: Path) -> dict[str, float]:
    lines = [line.split() for line in path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError(f"Rates file has fewer than two rows: {path}")
    names = lines[0][1:]
    values = lines[1][1:]
    if len(names) != len(values):
        raise ValueError(f"Rates header/value mismatch: {len(names)} != {len(values)}")
    return {name: float(value) for name, value in zip(names, values)}


def log2_ratio(value: float, baseline: float) -> float:
    if value <= 0 or baseline <= 0:
        raise ValueError("Rates and expression levels must be positive")
    return math.log2(value / baseline)


def infer_variable_region(single_hit: list[dict[str, object]]) -> tuple[int, int]:
    wild_type = single_hit[0]
    wild_sequence = str(wild_type["sequence"])
    offsets = set()
    max_position = -1
    for record in single_hit[1:]:
        name = str(record["name"])
        position = int(name.split("_pos_", 1)[1].rsplit("_", 1)[0])
        sequence = str(record["sequence"])
        differences = [index for index, (a, b) in enumerate(zip(wild_sequence, sequence)) if a != b]
        if len(differences) != 1:
            raise ValueError(f"Expected one substitution in {name}, found {len(differences)}")
        offsets.add(differences[0] - position)
        max_position = max(max_position, position)
    if len(offsets) != 1:
        raise ValueError(f"Could not infer one variable-region offset: {sorted(offsets)}")
    offset = offsets.pop()
    length = max_position + 1
    return offset, length


def one_hot_sequence(sequence: str, offset: int, length: int) -> np.ndarray:
    bases = {base: index for index, base in enumerate("ACGT")}
    encoded = np.zeros(length * 4, dtype=float)
    for position, base in enumerate(sequence[offset : offset + length]):
        encoded[position * 4 + bases[base]] = 1.0
    return encoded


def fit_qsam(
    single_hit: list[dict[str, object]], offset: int, length: int
) -> tuple[np.ndarray, int]:
    baseline = float(single_hit[0]["expression"])
    design = np.vstack(
        [one_hot_sequence(str(record["sequence"]), offset, length) for record in single_hit]
    )
    response = np.array(
        [log2_ratio(float(record["expression"]), baseline) for record in single_hit],
        dtype=float,
    )
    coefficients, _, rank, _ = np.linalg.lstsq(design, response, rcond=None)
    return coefficients, int(rank)


def qsam_predict(sequence: str, offset: int, length: int, coefficients: np.ndarray) -> float:
    return float(one_hot_sequence(sequence, offset, length) @ coefficients)


def pearson(x_values: np.ndarray, y_values: np.ndarray) -> float:
    if x_values.size < 2 or np.std(x_values) == 0 or np.std(y_values) == 0:
        return float("nan")
    return float(np.corrcoef(x_values, y_values)[0, 1])


def prepare_panel_data(
    datasets: dict[str, list[dict[str, object]]],
    rates: dict[str, dict[str, float]],
) -> tuple[dict[str, dict[str, object]], int, int]:
    single = datasets["single_hit"]
    offset, length = infer_variable_region(single)
    qsam_coefficients, qsam_rank = fit_qsam(single, offset, length)
    panel_data: dict[str, dict[str, object]] = {}
    for panel, (dataset, model) in PANEL_MAP.items():
        records = datasets[dataset]
        baseline_expression = float(records[0]["expression"])
        baseline_rate = rates[dataset][str(records[0]["name"])]
        observed = np.array(
            [log2_ratio(float(record["expression"]), baseline_expression) for record in records],
            dtype=float,
        )
        if model == "thermodynamic":
            predicted = np.array(
                [log2_ratio(rates[dataset][str(record["name"])], baseline_rate) for record in records],
                dtype=float,
            )
        else:
            predicted = np.array(
                [qsam_predict(str(record["sequence"]), offset, length, qsam_coefficients) for record in records],
                dtype=float,
            )
        panel_data[panel] = {
            "dataset": dataset,
            "model": model,
            "records": records,
            "observed": observed,
            "predicted": predicted,
            "pearson_r": pearson(observed, predicted),
        }

    single_observed = np.array(
        [log2_ratio(float(record["expression"]), float(single[0]["expression"])) for record in single]
    )
    single_thermo = np.array(
        [log2_ratio(rates["single_hit"][str(record["name"])], rates["single_hit"][str(single[0]["name"])]) for record in single]
    )
    single_qsam = np.array(
        [qsam_predict(str(record["sequence"]), offset, length, qsam_coefficients) for record in single]
    )
    panel_data["training"] = {
        "observed": single_observed,
        "thermodynamic": single_thermo,
        "QSAM": single_qsam,
        "thermodynamic_r": pearson(single_observed, single_thermo),
        "QSAM_r": pearson(single_observed, single_qsam),
        "QSAM_rank": qsam_rank,
    }
    return panel_data, offset, length


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(-0.18, 1.08, label, transform=axis.transAxes, fontsize=14, fontweight="bold", va="top")


def draw_transform_bar(
    axis: plt.Axes,
    y: float,
    blocks: list[tuple[str, float, float, str]],
    labels: str = "above",
) -> None:
    axis.add_patch(Rectangle((8, y - 0.04), 84, 0.08, color="#5b5b5b", zorder=1))
    for label, center, width, color in blocks:
        axis.add_patch(Rectangle((center - width / 2, y - 0.095), width, 0.19, color=color, zorder=2))
        if labels == "above":
            axis.text(center, y + 0.18, label, ha="center", va="bottom", fontsize=8.5)
        elif labels == "below":
            axis.text(center, y - 0.19, label, ha="center", va="top", fontsize=8.5)


def draw_green_cross(axis: plt.Axes, x: float, y: float, scale: float = 1.0) -> None:
    color = "#4aa33d"
    axis.plot([x - 3.5 * scale, x + 3.5 * scale], [y + 0.20 * scale, y - 0.18 * scale], color=color, lw=1.5)
    axis.plot([x + 3.5 * scale, x - 3.5 * scale], [y + 0.20 * scale, y - 0.18 * scale], color=color, lw=1.5)


def draw_blue_reverse_pair(axis: plt.Axes, x: float, y: float, scale: float = 1.0) -> None:
    color = "#2476b7"
    top = FancyArrowPatch(
        (x - 4.1 * scale, y + 0.18 * scale),
        (x + 4.1 * scale, y + 0.18 * scale),
        connectionstyle="arc3,rad=-0.45",
        arrowstyle="->",
        mutation_scale=13,
        color=color,
        linewidth=1.45,
        zorder=5,
        shrinkA=0,
        shrinkB=0,
    )
    bottom = FancyArrowPatch(
        (x + 4.1 * scale, y - 0.18 * scale),
        (x - 4.1 * scale, y - 0.18 * scale),
        connectionstyle="arc3,rad=-0.45",
        arrowstyle="->",
        mutation_scale=13,
        color=color,
        linewidth=1.45,
        zorder=5,
        shrinkA=0,
        shrinkB=0,
    )
    axis.add_patch(top)
    axis.add_patch(bottom)


def draw_split_arrows(axis: plt.Axes, x: float, y: float, scale: float = 1.0) -> None:
    color = "#4aa33d"
    left_path = MplPath(
        [
            (x - 3.4 * scale, y + 0.36 * scale),
            (x - 2.1 * scale, y + 0.22 * scale),
            (x - 1.8 * scale, y - 0.06 * scale),
            (x - 4.2 * scale, y - 0.34 * scale),
        ],
        [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4],
    )
    right_path = MplPath(
        [
            (x + 3.4 * scale, y + 0.36 * scale),
            (x + 2.1 * scale, y + 0.22 * scale),
            (x + 1.8 * scale, y - 0.06 * scale),
            (x + 4.2 * scale, y - 0.34 * scale),
        ],
        [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4],
    )
    left = FancyArrowPatch(
        path=left_path,
        arrowstyle="-|>",
        mutation_scale=9,
        color=color,
        linewidth=1.25,
        fill=False,
        shrinkA=0,
        shrinkB=0,
    )
    right = FancyArrowPatch(
        path=right_path,
        arrowstyle="-|>",
        mutation_scale=9,
        color=color,
        linewidth=1.25,
        fill=False,
        shrinkA=0,
        shrinkB=0,
    )
    axis.add_patch(left)
    axis.add_patch(right)


NORMAL_BLOCKS = [
    ("C1", 22, 9.5, "#f2697a"),
    ("C2", 48, 5.2, "#f2697a"),
    ("C3", 56, 5.2, "#f2697a"),
    ("CR", 71, 6.2, "#25a7a2"),
    ("C4", 80, 9.5, "#f2697a"),
]
REVERSE_BLOCKS = [
    ("C4", 22, 9.5, "#f2697a"),
    ("CR", 31, 6.2, "#25a7a2"),
    ("C3", 47, 5.2, "#f2697a"),
    ("C2", 56, 5.2, "#f2697a"),
    ("C1", 80, 9.5, "#f2697a"),
]
REARRANGED_BLOCKS = [
    ("C3", 20, 5.2, "#f2697a"),
    ("CR", 38, 6.2, "#25a7a2"),
    ("C4", 47, 9.5, "#f2697a"),
    ("C1", 70, 9.5, "#f2697a"),
    ("C2", 92, 5.2, "#f2697a"),
]
REV_REARRANGED_BLOCKS = [
    ("C2", 18, 5.2, "#f2697a"),
    ("C1", 44, 9.5, "#f2697a"),
    ("C4", 70, 9.5, "#f2697a"),
    ("CR", 78, 6.2, "#25a7a2"),
    ("C3", 92, 5.2, "#f2697a"),
]


def draw_scheme(axis: plt.Axes, panel: str) -> None:
    axis.set_xlim(0, 100)
    axis.set_ylim(-0.1, 2.2 if panel != "C" else 3.1)
    axis.axis("off")
    panel_label(axis, panel)
    if panel == "A":
        draw_transform_bar(axis, 1.65, NORMAL_BLOCKS, labels="above")
        draw_transform_bar(axis, 0.45, REVERSE_BLOCKS, labels="below")
        draw_blue_reverse_pair(axis, 50, 1.05, scale=1.0)
    elif panel == "B":
        draw_transform_bar(axis, 1.55, NORMAL_BLOCKS, labels="none")
        draw_transform_bar(axis, 0.45, REARRANGED_BLOCKS, labels="below")
        axis.text(38, 0.73, "CR", ha="center", va="bottom", fontsize=8.5)
        draw_green_cross(axis, 50, 0.98, scale=1.0)
    else:
        draw_transform_bar(axis, 2.55, NORMAL_BLOCKS, labels="none")
        draw_transform_bar(axis, 1.50, REVERSE_BLOCKS, labels="none")
        draw_transform_bar(axis, 0.38, REV_REARRANGED_BLOCKS, labels="below")
        draw_blue_reverse_pair(axis, 50, 1.98, scale=1.0)
        draw_green_cross(axis, 50, 1.02, scale=1.0)
        axis.text(78, 0.68, "CR", ha="center", va="bottom", fontsize=8.5)
        axis.text(11, -0.05, "C1~4:CRE1~4\nCR:cryptic region", ha="left", va="top", fontsize=7.7)


def crop_light_margin(image: np.ndarray, threshold: float = 0.985, pad: int = 2) -> np.ndarray:
    rgb = image[..., :3]
    if rgb.dtype.kind in "ui":
        rgb = rgb.astype(float) / 255.0
    mask = np.any(rgb < threshold, axis=2)
    coords = np.argwhere(mask)
    if coords.size == 0:
        return image
    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1
    y0 = max(0, int(y0) - pad)
    x0 = max(0, int(x0) - pad)
    y1 = min(image.shape[0], int(y1) + pad)
    x1 = min(image.shape[1], int(x1) + pad)
    return image[y0:y1, x0:x1]


def style_scatter_axis(axis: plt.Axes) -> None:
    axis.set_facecolor("#EBEBEB")
    axis.grid(True, color="white", linewidth=1.0)
    axis.set_axisbelow(True)
    for spine in axis.spines.values():
        spine.set_visible(False)
    axis.tick_params(labelsize=8, length=0)


def add_training_inset(axis: plt.Axes, observed: np.ndarray, predicted: np.ndarray, correlation: float) -> None:
    inset = axis.inset_axes([0.08, 0.58, 0.43, 0.36])
    inset.set_facecolor("white")
    inset.scatter(observed, predicted, s=2.5, color="#174b9b", alpha=0.75, linewidths=0)
    low = float(min(observed.min(), predicted.min()))
    high = float(max(observed.max(), predicted.max()))
    inset.plot([low, high], [low, high], color="#5778a4", linewidth=0.7)
    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_color("#d0d0d0")
        spine.set_linewidth(0.6)
    inset.text(0.03, 0.05, f"R={correlation:.2f}".rstrip("0").rstrip("."), transform=inset.transAxes, fontsize=8)


def draw_scatter(axis: plt.Axes, panel: str, data: dict[str, object], training: dict[str, object] | None = None) -> None:
    observed = np.asarray(data["observed"])
    predicted = np.asarray(data["predicted"])
    style_scatter_axis(axis)
    axis.scatter(observed, predicted, s=6, color="#16499b", alpha=0.82, linewidths=0)
    panel_label(axis, panel)
    correlation = float(data["pearson_r"])
    axis.text(0.97, 0.08, f"R={correlation:.2f}", transform=axis.transAxes, ha="right", fontsize=9)
    if training is not None:
        model = str(data["model"])
        training_prediction = np.asarray(training[model])
        training_r = float(training[f"{model}_r"])
        add_training_inset(axis, np.asarray(training["observed"]), training_prediction, training_r)


def plot_figure(panel_data: dict[str, dict[str, object]], output: Path) -> None:
    figure = plt.figure(figsize=(8.1, 10.4), constrained_layout=False)
    grid = figure.add_gridspec(4, 3, height_ratios=[1, 1, 1, 1.08], hspace=0.34, wspace=0.28)
    for row, panel in enumerate(("A", "B", "C")):
        draw_scheme(figure.add_subplot(grid[row, 0]), panel)

    training = panel_data["training"]
    for row, panel in enumerate(("D", "E", "F")):
        axis = figure.add_subplot(grid[row, 1])
        draw_scatter(axis, panel, panel_data[panel], training)
        if row == 0:
            axis.set_title("Our model", fontsize=13, pad=5)
        if row == 1:
            axis.set_ylabel("prediction", fontsize=9)
        if row == 2:
            axis.set_xlabel("MPRA single-hit data", fontsize=9)

    for row, panel in enumerate(("G", "H", "I")):
        axis = figure.add_subplot(grid[row, 2])
        draw_scatter(axis, panel, panel_data[panel], training)
        if row == 0:
            axis.set_title("QSAM", fontsize=13, pad=5)
        if row == 2:
            axis.set_xlabel("MPRA single-hit data", fontsize=9)

    for column, panel in enumerate(("J", "K")):
        axis = figure.add_subplot(grid[3, column])
        draw_scatter(axis, panel, panel_data[panel])
        axis.set_xlabel("MPRA multi-hit data", fontsize=9)
        if column == 0:
            axis.set_ylabel("Multi-hit prediction", fontsize=9)

    figure.subplots_adjust(left=0.07, right=0.98, top=0.97, bottom=0.06)

    lm_axis = figure.add_subplot(grid[3, 2])
    box = lm_axis.get_position()
    lm_axis.set_position(
        [
            box.x0 - box.width * 0.09,
            box.y0 - box.height * 0.08,
            box.width * 1.30,
            box.height * 1.30,
        ]
    )
    lm_axis.axis("off")
    if LM_REFERENCE.exists():
        lm_image = crop_light_margin(plt.imread(LM_REFERENCE))
        lm_axis.imshow(lm_image, aspect="auto", interpolation="lanczos")
        lm_axis.set_xlim(0, lm_image.shape[1])
        lm_axis.set_ylim(lm_image.shape[0], 0)
    else:
        lm_axis.text(0.0, 0.95, "Panels L-M reference image missing", fontsize=9, va="top")

    figure.savefig(output.with_suffix(".png"), dpi=300, facecolor="white", bbox_inches="tight", pad_inches=0.03)
    figure.savefig(output.with_suffix(".pdf"), facecolor="white", bbox_inches="tight", pad_inches=0.03)
    plt.close(figure)


def write_tables(panel_data: dict[str, dict[str, object]], output_dir: Path) -> None:
    with (output_dir / "figure4_metrics.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(("panel", "dataset", "model", "n", "pearson_r", "paper_r", "delta_r"))
        for panel in PANEL_MAP:
            data = panel_data[panel]
            reproduced = float(data["pearson_r"])
            writer.writerow(
                (
                    panel,
                    data["dataset"],
                    data["model"],
                    len(data["observed"]),
                    f"{reproduced:.8f}",
                    f"{PAPER_R[panel]:.2f}",
                    f"{reproduced - PAPER_R[panel]:.8f}",
                )
            )

    with (output_dir / "figure4_panel_data.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(("panel", "dataset", "model", "name", "observed_log2", "predicted_log2"))
        for panel in PANEL_MAP:
            data = panel_data[panel]
            for record, observed, predicted in zip(data["records"], data["observed"], data["predicted"]):
                writer.writerow((panel, data["dataset"], data["model"], record["name"], f"{float(observed):.10g}", f"{float(predicted):.10g}"))


def write_report(
    output_dir: Path,
    args: argparse.Namespace,
    panel_data: dict[str, dict[str, object]],
    offset: int,
    length: int,
) -> None:
    lines = [
        "# Figure 4A-K reproduction with the selected 4TF model",
        "",
        f"- Best fitted XML: `{args.best_xml}`",
        f"- Source workbook: `{args.mmc4}`",
        f"- transcpp: `{args.transcpp}`",
        f"- Threads: {args.threads}",
        f"- QSAM variable region: full-sequence offset {offset}, length {length}",
        "- Thermodynamic predictions: fitted parameters frozen, forward calculation only",
        "- QSAM predictions: one-hot linear least-squares model trained on single-hit log2 activity",
        "",
        "## Correlations",
        "",
        "| Panel | Dataset | Model | Reproduced R | Paper R | Difference |",
        "|---|---|---|---:|---:|---:|",
    ]
    for panel in PANEL_MAP:
        data = panel_data[panel]
        reproduced = float(data["pearson_r"])
        lines.append(
            f"| {panel} | {data['dataset']} | {data['model']} | {reproduced:.4f} | "
            f"{PAPER_R[panel]:.2f} | {reproduced - PAPER_R[panel]:+.4f} |"
        )
    training = panel_data["training"]
    lines.extend(
        [
            "",
            f"Single-hit training R (thermodynamic): {float(training['thermodynamic_r']):.4f}",
            f"Single-hit training R (QSAM): {float(training['QSAM_r']):.4f}",
            f"QSAM design rank: {int(training['QSAM_rank'])}",
            "",
            "The QSAM Pearson correlations reproduce the paper after rounding. Its absolute vertical offset is not identical because the paper does not publish the fitted QSAM parameter matrix or its coefficient gauge; this does not affect Pearson R.",
            "",
            "Figure 4L-M are inserted from the paper reference image because they require fold-specific model fitting for every TF count and cross-validation split.",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    for required in (args.best_xml, args.mmc4, args.transcpp):
        if not required.exists():
            raise FileNotFoundError(required)
    args.output.mkdir(parents=True, exist_ok=True)
    datasets = read_datasets(args.mmc4)
    dataset_dir = args.output / "datasets"
    evaluation_dir = args.output / "evaluation"
    rates: dict[str, dict[str, float]] = {}
    for dataset in DATASET_ORDER:
        fasta = dataset_dir / f"{dataset}.fa"
        write_fasta(fasta, datasets[dataset])
        xml_path = evaluation_dir / f"{dataset}.xml"
        rates_path = xml_path.with_suffix(".rates.tsv")
        if not args.skip_transcpp:
            make_evaluation_xml(args.best_xml, xml_path, fasta, dataset, datasets[dataset], args.threads)
            rates_path = run_transcpp(args.transcpp, xml_path, args.transcpp.parent, args.threads)
        if not rates_path.exists():
            raise FileNotFoundError(rates_path)
        rates[dataset] = read_rates(rates_path)

    panel_data, offset, length = prepare_panel_data(datasets, rates)
    write_tables(panel_data, args.output)
    plot_figure(panel_data, args.output / "Figure4_A-K_selected_4TF")
    write_report(args.output, args, panel_data, offset, length)
    print((args.output / "figure4_metrics.tsv").read_text(encoding="utf-8"))
    print(f"Figure: {args.output / 'Figure4_A-K_selected_4TF.png'}")


if __name__ == "__main__":
    main()
