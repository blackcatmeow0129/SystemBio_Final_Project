#!/usr/bin/env python3
"""Standalone QSAM reproduction for Figure 4G/H/I/K.

This script reuses the QSAM functions from reproduce_figure4.py and does not
require transcpp. It trains the linear one-hot QSAM model on single-hit data and
evaluates reverse, rearrange, reverse+rearrange, and multi-hit panels.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from reproduce_figure4 import DATASET_SHEETS, fit_qsam, infer_variable_region, log2_ratio, pearson, qsam_predict, read_datasets


PANEL_TO_DATASET = {
    "G": "reverse",
    "H": "rearrange",
    "I": "reverse_rearrange",
    "K": "multi_hit",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mmc4", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "output_qsam")
    args = parser.parse_args()

    datasets = read_datasets(args.mmc4)
    single = datasets["single_hit"]
    offset, length = infer_variable_region(single)
    coefficients, rank = fit_qsam(single, offset, length)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.6), dpi=180)
    for axis, (panel, dataset_name) in zip(axes.flat, PANEL_TO_DATASET.items()):
        records = datasets[dataset_name]
        baseline = float(records[0]["expression"])
        observed = np.array([log2_ratio(float(record["expression"]), baseline) for record in records])
        predicted = np.array([qsam_predict(str(record["sequence"]), offset, length, coefficients) for record in records])
        r_value = pearson(observed, predicted)
        rows.append({"panel": panel, "dataset": dataset_name, "n": len(records), "pearson_r": f"{r_value:.8f}"})
        axis.scatter(observed, predicted, s=7, color="#174b9b", alpha=0.75, linewidths=0)
        axis.axline((0, 0), slope=1, color="#777777", linewidth=0.8)
        axis.set_title(f"Figure 4{panel} QSAM, R={r_value:.2f}", fontsize=9)
        axis.set_xlabel("MPRA log2 activity")
        axis.set_ylabel("QSAM prediction")

    fig.tight_layout()
    fig.savefig(args.out_dir / "Figure4_GHIK_QSAM.png", bbox_inches="tight")
    plt.close(fig)

    with (args.out_dir / "figure4_qsam_metrics.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["panel", "dataset", "n", "pearson_r"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    print(f"QSAM rank: {rank}")
    print(f"Saved: {args.out_dir / 'Figure4_GHIK_QSAM.png'}")


if __name__ == "__main__":
    main()
