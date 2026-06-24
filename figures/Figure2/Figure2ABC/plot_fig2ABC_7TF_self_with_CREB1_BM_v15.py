#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
plot_fig2ABC_7TF_self_with_CREB1_BM_v5.py

More polished Figure 2A-C style plot. v7 fixes Panel A strand sequence labeling.

Main panel:
  B = measured MPRA single-hit activity
  C = 7TF_self prediction

Inset in each C panel:
  B.M = CREB1-only fitted baseline prediction

Inputs:
  model_input/expression/single_hit_expression.csv
  model_input/predictions/7TF_self_single_hit_fixed_rates.tsv
  model_input/predictions/CREB1_only_single_hit_rates.tsv

Outputs:
  figures/Figure2ABC_7TF_self_with_CREB1_BM_v5.png
  figures/Figure2ABC_7TF_self_with_CREB1_BM_v5.pdf
  figures/Figure2ABC_7TF_self_with_CREB1_BM_v5_values.csv
"""

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle, Polygon
from matplotlib.ticker import MultipleLocator

EXPR_FILE = "model_input/expression/single_hit_expression.csv"
PRED_FILE_MAIN = "model_input/predictions/7TF_self_single_hit_fixed_rates.tsv"
PRED_FILE_BM = "model_input/predictions/CREB1_only_single_hit_rates.tsv"

OUT_DIR = "figures"
os.makedirs(OUT_DIR, exist_ok=True)

BASES = ["A", "C", "G", "T"]

REGIONS = [
    {"name": "CRE1",    "start": 11, "end": 18, "kind": "cre"},
    {"name": "CRE2",    "start": 35, "end": 40, "kind": "cre"},
    {"name": "CRE3",    "start": 47, "end": 53, "kind": "cre"},
    {"name": "cryptic", "start": 63, "end": 66, "kind": "cryptic"},
    {"name": "CRE4",    "start": 69, "end": 76, "kind": "cre"},
]

WT_ENHANCER = "GCACCAGACAGTGACGTCAGCTGCCAGATCCCATGGCCGTCATACTGTGACGTCTTTCAGACACCCCATTGACGTCAATGGGAGAAC"


def comp_base(b):
    return {"A": "T", "C": "G", "G": "C", "T": "A"}[b]


def parse_variant_name(name):
    m = re.search(r"pos_(\d+)_([ACGT])", str(name))
    if m:
        return int(m.group(1)), m.group(2)
    return None, None


def load_measured():
    df = pd.read_csv(EXPR_FILE)
    df = df[df["name"] != "synCRE_Promega_0"].copy()
    df[["position", "base"]] = df["name"].apply(lambda x: pd.Series(parse_variant_name(x)))
    df = df.dropna(subset=["position", "base"]).copy()
    df["position"] = df["position"].astype(int)

    if "delta_activity_log2_vs_100" not in df.columns:
        df["delta_activity_log2_vs_100"] = np.log2(df["expression level"] / 100.0)

    return df[["name", "position", "base", "delta_activity_log2_vs_100"]].rename(
        columns={"delta_activity_log2_vs_100": "measured_delta"}
    )


def load_prediction(pred_file):
    pred = pd.read_csv(pred_file, sep=r"\s+", engine="python")
    pred.columns = ["name", "predicted_expression"]

    wt_rows = pred[pred["name"].isin(["synCRE_Promega_0", "synCRE_Promega_0_WT"])]
    if len(wt_rows) == 0:
        raise ValueError(f"Cannot find WT row in {pred_file}")

    wt_pred = float(wt_rows.iloc[0]["predicted_expression"])
    pred["predicted_delta"] = np.log2(pred["predicted_expression"] / wt_pred)

    pred[["position", "base"]] = pred["name"].apply(lambda x: pd.Series(parse_variant_name(x)))
    pred = pred.dropna(subset=["position", "base"]).copy()
    pred["position"] = pred["position"].astype(int)

    return pred[["name", "position", "base", "predicted_delta"]]


def region_color(region):
    if region["kind"] == "cre":
        return "#f4a6a6", "#de3a3a", "#6f2020"
    return "#b6bbff", "#4c63ff", "#28308c"


def add_region_shading(ax):
    for r in REGIONS:
        face, _, _ = region_color(r)
        ax.axvspan(r["start"] - 0.5, r["end"] + 0.5, color=face, alpha=0.40, linewidth=0, zorder=0)


def draw_arrow(ax, x0, y0, x1, y1, color):
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(arrowstyle="->", color=color, lw=1.45),
        zorder=7,
    )


def draw_sequence(ax, y, seq, fontsize=7.6, color="#303030"):
    for i, ch in enumerate(seq):
        ax.text(i, y, ch, family="monospace", fontsize=fontsize,
                ha="center", va="center", color=color, zorder=3)


def draw_motif_box(ax, y, region, sequence_for_this_strand):
    face, edge, txt_color = region_color(region)
    x0 = region["start"]
    width = region["end"] - region["start"] + 1

    rect = Rectangle(
        (x0 - 0.50, y - 0.066),
        width,
        0.132,
        facecolor="none",
        edgecolor=edge,
        lw=1.05,
        alpha=1.0,
        zorder=4,
    )
    ax.add_patch(rect)

    motif = sequence_for_this_strand[region["start"]:region["end"] + 1]
    for j, ch in enumerate(motif):
        ax.text(x0 + j, y, ch, family="monospace", fontsize=7.55,
                ha="center", va="center", color=txt_color, zorder=5)


def draw_panel_a(ax):
    ax.set_xlim(-2, 89)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Panel A label is placed later in figure coordinates for left-side alignment with B.

    # Slightly large, but closer to original than previous overly enlarged version
    ax.text(-1.55, 0.69, "5′", fontsize=9.2, ha="right", va="center", color="#333333")
    ax.text(87.75, 0.69, "3′", fontsize=9.2, ha="left", va="center", color="#333333")
    ax.text(-1.55, 0.50, "3′", fontsize=9.2, ha="right", va="center", color="#333333")
    ax.text(87.75, 0.50, "5′", fontsize=9.2, ha="left", va="center", color="#333333")

    draw_sequence(ax, 0.69, WT_ENHANCER, fontsize=7.4)
    bottom_seq = "".join(comp_base(b) for b in WT_ENHANCER)
    draw_sequence(ax, 0.50, bottom_seq, fontsize=7.4)

    for r in REGIONS:
        draw_motif_box(ax, 0.69, r, WT_ENHANCER)
        draw_motif_box(ax, 0.50, r, bottom_seq)
        xm = (r["start"] + r["end"]) / 2
        ax.text(xm, 0.89, r["name"], fontsize=9.6, ha="center", va="center")
        ax.text(xm, 0.315, f"{r['start']}-{r['end']}", fontsize=7.0,
                ha="center", va="center", color="#303030")


def add_ribbons_only_to_B(fig, axA, axBtop):
    # v14: connect each CRE/cryptic box to its corresponding x-range in the first B panel,
    # instead of simply tapering straight downward to a single narrow foot.
    overlay = fig.add_axes([0, 0, 1, 1], zorder=2.8)
    overlay.set_axis_off()
    overlay.patch.set_alpha(0)

    xlimA = axA.get_xlim()
    ylimA = axA.get_ylim()
    xlimB = axBtop.get_xlim()
    ylimB = axBtop.get_ylim()

    posA = axA.get_position()
    posB = axBtop.get_position()

    def xfig_from_axA(x):
        frac = (x - xlimA[0]) / (xlimA[1] - xlimA[0])
        return posA.x0 + frac * posA.width

    def yfig_from_axA(y):
        frac = (y - ylimA[0]) / (ylimA[1] - ylimA[0])
        return posA.y0 + frac * posA.height

    def xfig_from_axB(x):
        frac = (x - xlimB[0]) / (xlimB[1] - xlimB[0])
        return posB.x0 + frac * posB.width

    def yfig_from_axB(y):
        frac = (y - ylimB[0]) / (ylimB[1] - ylimB[0])
        return posB.y0 + frac * posB.height

    # Start from the bottom edge of the lower motif boxes in panel A
    y_top = yfig_from_axA(0.43)
    # Land on the top edge of the first B panel
    y_bottom = yfig_from_axB(2.22)

    for r in REGIONS:
        face, _, _ = region_color(r)

        # top ribbon width = motif box width in panel A
        x0_top = xfig_from_axA(r["start"] - 0.45)
        x1_top = xfig_from_axA(r["end"] + 0.45)

        # bottom ribbon width = corresponding highlighted region width in panel B
        x0_bottom = xfig_from_axB(r["start"] - 0.5)
        x1_bottom = xfig_from_axB(r["end"] + 0.5)

        poly = Polygon(
            [
                (x0_top, y_top),
                (x1_top, y_top),
                (x1_bottom, y_bottom),
                (x0_bottom, y_bottom),
            ],
            closed=True,
            transform=fig.transFigure,
            facecolor=face,
            edgecolor="none",
            alpha=0.24,
            zorder=2.8,
            clip_on=False,
        )
        overlay.add_patch(poly)


def draw_bars(ax, data, value_col, base, color, show_xlabel=False):
    sub = data[data["base"] == base].sort_values("position")
    add_region_shading(ax)
    ax.bar(sub["position"], sub[value_col], width=0.54,
           color=color, edgecolor=color, linewidth=0, zorder=3)
    ax.axhline(0, color="black", linewidth=0.75, zorder=4)

    ax.set_xlim(-1, 87)
    ax.set_ylim(-2.25, 2.25)
    ax.set_yticks([-2, -1, 0, 1, 2])

    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(0.5))

    ax.set_facecolor("#fcfcfc")
    ax.grid(which="major", axis="both", color="#dddddd", lw=0.9, zorder=1)
    ax.grid(which="minor", axis="both", color="#f0f0f0", lw=0.6, zorder=1)

    ax.text(0.03, 0.80, "→ " + base, transform=ax.transAxes,
            fontsize=9.5, fontweight="bold", zorder=7)

    if show_xlabel:
        ax.set_xlabel("position", fontsize=10)
    else:
        ax.tick_params(axis="x", labelbottom=False)

    ax.tick_params(axis="both", labelsize=8.3, length=3)
    for spine in ax.spines.values():
        spine.set_linewidth(0.95)
        spine.set_color("#444444")


def add_b_annotations(ax, base):
    # green arrow: left-effect region
    draw_arrow(ax, 8.1, -1.35, 13.0, -0.79, "#2ca02c")

    # asterisk near cryptic-positive region (visible in A/G/T panels in the paper)
    if base in ["A", "G", "T"]:
        ax.text(65.0, 0.99, "*", fontsize=14, ha="center",
                va="center", color="black", zorder=7)

    # red arrows: one near the cryptic-adjacent dip, one near the CRE4 dip
    draw_arrow(ax, 57.6, -1.02, 60.7, -0.54, "#df3b3b")
    draw_arrow(ax, 80.0, -1.22, 77.1, -0.69, "#df3b3b")


def add_baseline_inset(ax, bm_pred, base):
    sub = bm_pred[bm_pred["base"] == base].sort_values("position")

    inset = ax.inset_axes([0.025, 0.065, 0.31, 0.165])
    inset.bar(sub["position"], sub["predicted_delta"], width=0.44,
              color="#ff0000", linewidth=0)
    inset.axhline(0, color="black", lw=0.42)
    inset.set_xlim(-1, 87)
    inset.set_ylim(-2.2, 2.2)
    inset.set_xticks([])
    inset.set_yticks([])
    inset.set_facecolor("white")

    for spine in inset.spines.values():
        spine.set_linewidth(0.65)
        spine.set_color("#444444")

    inset.text(0.02, 0.06, "B.M", transform=inset.transAxes,
               fontsize=5.2, va="bottom", color="#333333")


def per_base_stats(merged, base):
    sub = merged[merged["base"] == base]
    r = sub["measured_delta"].corr(sub["predicted_delta"])
    r2 = r * r
    rmse = np.sqrt(np.mean((sub["measured_delta"] - sub["predicted_delta"]) ** 2))
    return r, r2, rmse


def main():
    for required in [EXPR_FILE, PRED_FILE_MAIN, PRED_FILE_BM]:
        if not os.path.exists(required):
            raise FileNotFoundError(f"Missing required file: {required}")

    measured = load_measured()
    pred_main = load_prediction(PRED_FILE_MAIN)
    pred_bm = load_prediction(PRED_FILE_BM)

    merged = measured.merge(
        pred_main[["name", "position", "base", "predicted_delta"]],
        on=["name", "position", "base"],
        how="inner"
    )

    out_csv = f"{OUT_DIR}/Figure2ABC_7TF_self_with_CREB1_BM_v15_values.csv"
    merged.to_csv(out_csv, index=False)

    # Slightly less tall A panel; more paper-like layout
    fig = plt.figure(figsize=(8.85, 6.8))
    gs = GridSpec(
        nrows=5,
        ncols=2,
        height_ratios=[0.84, 1, 1, 1, 1],
        width_ratios=[1, 1],
        hspace=0.26,
        wspace=0.22,
    )

    axA = fig.add_subplot(gs[0, :])
    draw_panel_a(axA)

    axesB = []
    axesC = []

    for i, base in enumerate(BASES):
        axB = fig.add_subplot(gs[i + 1, 0])
        axC = fig.add_subplot(gs[i + 1, 1])
        axesB.append(axB)
        axesC.append(axC)

        draw_bars(axB, measured, "measured_delta", base, "#0000ff", show_xlabel=(i == 3))
        draw_bars(axC, merged, "predicted_delta", base, "#ff0000", show_xlabel=(i == 3))

        add_b_annotations(axB, base)
        add_baseline_inset(axC, pred_bm, base)

        r, r2, rmse = per_base_stats(merged, base)
        axC.text(
            0.35, 0.86,
            f"R={r:.2f}   R²={r2:.2f}   rmse={rmse:.2f}",
            transform=axC.transAxes,
            fontsize=8.2,
            ha="left",
            va="center",
            zorder=7,
        )

    axesB[0].set_title("Measured mRNA", fontsize=10.7, pad=6)
    axesC[0].set_title("7 CREB family model", fontsize=10.7, pad=6)

    # Align A, B, and Δactivity(log2) on the same left guide line.
    x_left_guide = axesB[0].get_position().x0 - 0.060

    fig.text(x_left_guide, axA.get_position().y1 - 0.012, "A",
             fontsize=12, fontweight="bold", ha="left", va="top")
    fig.text(x_left_guide, axesB[0].get_position().y1 + 0.002, "B",
             fontsize=12, fontweight="bold", ha="left", va="bottom")
    fig.text(axesC[0].get_position().x0 - 0.020, axesC[0].get_position().y1 + 0.002, "C",
             fontsize=12, fontweight="bold", ha="left", va="bottom")

    fig.text(x_left_guide, 0.38, "Δactivity(log2)", rotation="vertical",
             fontsize=11, va="center", ha="center")
    fig.text(0.506, 0.39, "VS", fontsize=11, ha="center", va="center")

    add_ribbons_only_to_B(fig, axA, axesB[0])

    axA.set_zorder(5)
    for ax in axesB + axesC:
        ax.set_zorder(5)
        ax.patch.set_alpha(1)

    out_png = f"{OUT_DIR}/Figure2ABC_7TF_self_with_CREB1_BM_v15.png"
    out_pdf = f"{OUT_DIR}/Figure2ABC_7TF_self_with_CREB1_BM_v15.pdf"

    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.savefig(out_pdf, bbox_inches="tight")
    plt.close()

    print("DONE")
    print(out_png)
    print(out_pdf)
    print(out_csv)


if __name__ == "__main__":
    main()
