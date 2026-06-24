#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plot_fig2D_motif_logos.py

Draw Figure 2D-like motif logos from mmc3.xlsx.

Run:
  source venv/bin/activate
  python plot_fig2D_motif_logos.py

Output:
  figures/Figure2D_motif_logos.png
  figures/Figure2D_motif_logos.pdf
  figures/Figure2D_pwm_probability_tables.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D
from matplotlib.font_manager import FontProperties


INPUT_XLSX = "1-s2.0-S2589004223028249-mmc3.xlsx"
OUT_DIR = "figures"

TF_ORDER = ["CREB1", "CREB3", "CREB5", "CREM", "ATF1", "ATF4", "ATF7"]
BASES = ["A", "C", "G", "T"]
BASE_COLORS = {
    "A": "#2ca25f",
    "C": "#3182bd",
    "G": "#f0ad00",
    "T": "#d62728",
}

os.makedirs(OUT_DIR, exist_ok=True)


def parse_mmc3_pwms(path):
    df = pd.read_excel(path, header=None)
    pwms = {}

    i = 0
    while i < len(df):
        row = df.iloc[i]

        if isinstance(row.iloc[1], str) and row.iloc[1].strip() == "A" and pd.notna(row.iloc[0]):
            tf_name = str(row.iloc[0]).strip()
            pwm_by_base = {}

            ok = True
            for offset, base in enumerate(BASES):
                r = df.iloc[i + offset]
                if str(r.iloc[1]).strip() != base:
                    ok = False
                    break

                vals = [float(v) for v in r.iloc[2:].tolist() if pd.notna(v)]
                pwm_by_base[base] = vals

            if ok:
                lengths = [len(pwm_by_base[b]) for b in BASES]
                if len(set(lengths)) != 1:
                    raise ValueError(f"Length mismatch in {tf_name}: {lengths}")

                pwms[tf_name] = pwm_by_base
                i += 5
            else:
                i += 1
        else:
            i += 1

    return pwms


def pssm_to_prob(pwm_by_base):
    mat = np.array([pwm_by_base[b] for b in BASES], dtype=float)
    exp_mat = np.exp(mat - mat.max(axis=0, keepdims=True))
    prob = exp_mat / exp_mat.sum(axis=0, keepdims=True)
    return prob


def info_heights(prob):
    eps = 1e-12
    entropy = -np.sum(prob * np.log2(prob + eps), axis=0)
    info = 2.0 - entropy
    heights = prob * info
    return heights


def draw_letter(ax, letter, x, y, height, width=0.9):
    if height <= 0:
        return

    fp = FontProperties(family="DejaVu Sans", weight="bold")
    tp = TextPath((0, 0), letter, size=1, prop=fp)
    bb = tp.get_extents()

    sx = width / bb.width
    sy = height / bb.height

    trans = (
        Affine2D()
        .translate(-bb.xmin, -bb.ymin)
        .scale(sx, sy)
        .translate(x - width / 2, y)
        + ax.transData
    )
    patch = PathPatch(tp, transform=trans, linewidth=0, facecolor=BASE_COLORS[letter])
    ax.add_patch(patch)


def draw_logo(ax, tf_name, pwm_by_base):
    prob = pssm_to_prob(pwm_by_base)
    heights = info_heights(prob)
    length = prob.shape[1]

    for pos in range(length):
        order = np.argsort(heights[:, pos])
        y = 0.0
        for idx in order:
            h = float(heights[idx, pos])
            if h > 0.01:
                draw_letter(ax, BASES[idx], pos + 1, y, h)
                y += h

    ax.set_xlim(0.5, length + 0.5)
    ax.set_ylim(0, 2.0)
    ax.set_xticks([])
    ax.set_yticks([0, 1, 2])
    ax.tick_params(axis="y", labelsize=8, length=2)
    ax.set_ylabel(tf_name, rotation=0, labelpad=28, va="center", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main():
    pwms = parse_mmc3_pwms(INPUT_XLSX)

    missing = [tf for tf in TF_ORDER if tf not in pwms]
    if missing:
        raise ValueError(f"Missing TF PWM in mmc3: {missing}")

    rows = []
    for tf in TF_ORDER:
        prob = pssm_to_prob(pwms[tf])
        for pos in range(prob.shape[1]):
            for base_i, base in enumerate(BASES):
                rows.append({
                    "TF": tf,
                    "position": pos + 1,
                    "base": base,
                    "probability": prob[base_i, pos],
                    "raw_score": pwms[tf][base][pos],
                })

    pd.DataFrame(rows).to_csv(f"{OUT_DIR}/Figure2D_pwm_probability_tables.csv", index=False)

    fig, axes = plt.subplots(
        nrows=len(TF_ORDER),
        ncols=1,
        figsize=(7.5, 8.5),
        sharex=False
    )

    for ax, tf in zip(axes, TF_ORDER):
        draw_logo(ax, tf, pwms[tf])

    axes[-1].set_xlabel("PWM position", fontsize=10)
    fig.text(0.02, 0.5, "bits", va="center", rotation="vertical", fontsize=10)
    fig.text(0.018, 0.982, "D", fontsize=11, fontweight="bold", ha="left", va="top")

    plt.tight_layout(rect=[0.05, 0.03, 1, 0.97])
    plt.savefig(f"{OUT_DIR}/Figure2D_motif_logos.png", dpi=300)
    plt.savefig(f"{OUT_DIR}/Figure2D_motif_logos.pdf")
    plt.close()

    print("DONE")
    print(f"{OUT_DIR}/Figure2D_motif_logos.png")
    print(f"{OUT_DIR}/Figure2D_motif_logos.pdf")
    print(f"{OUT_DIR}/Figure2D_pwm_probability_tables.csv")


if __name__ == "__main__":
    main()
