#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Combine Figure 2A-C and a compact Figure 2D motif-logo column."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.patches import PathPatch
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
from PIL import Image, ImageChops

from plot_fig2D_motif_logos import (
    BASES,
    BASE_COLORS,
    INPUT_XLSX,
    TF_ORDER,
    info_heights,
    parse_mmc3_pwms,
    pssm_to_prob,
)


ROOT = Path(__file__).resolve().parent
DESKTOP_FIGURES = Path(r"C:\Users\LIME\Desktop\figuer5\figures")
ABC_PATH = DESKTOP_FIGURES / "Figure2ABC_7TF_self_with_CREB1_BM_v15.png"
OUT_PNG = DESKTOP_FIGURES / "Figure2ABCD_combined_paper_style.png"
OUT_PDF = DESKTOP_FIGURES / "Figure2ABCD_combined_paper_style.pdf"


def crop_white(image: Image.Image, threshold: int = 12, pad: int = 8) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, "white")
    diff = ImageChops.difference(rgb, background)
    mask = diff.point(lambda x: 0 if x < threshold else 255)
    bbox = mask.getbbox()
    if bbox is None:
        return image
    left = max(0, bbox[0] - pad)
    upper = max(0, bbox[1] - pad)
    right = min(image.width, bbox[2] + pad)
    lower = min(image.height, bbox[3] + pad)
    return image.crop((left, upper, right, lower))


def draw_letter(ax, letter: str, x: float, y: float, height: float, width: float = 0.82) -> None:
    if height <= 0:
        return
    font = FontProperties(family="DejaVu Sans", weight="bold")
    path = TextPath((0, 0), letter, size=1, prop=font)
    bbox = path.get_extents()
    transform = (
        Affine2D()
        .translate(-bbox.xmin, -bbox.ymin)
        .scale(width / bbox.width, height / bbox.height)
        .translate(x - width / 2, y)
        + ax.transData
    )
    ax.add_patch(PathPatch(path, transform=transform, linewidth=0, facecolor=BASE_COLORS[letter]))


def draw_logo_compact(ax, tf_name: str, pwm_by_base: dict[str, list[float]]) -> None:
    probabilities = pssm_to_prob(pwm_by_base)
    heights = info_heights(probabilities)
    length = probabilities.shape[1]

    for pos in range(length):
        order = np.argsort(heights[:, pos])
        y = 0.0
        for idx in order:
            height = float(heights[idx, pos])
            if height > 0.01:
                draw_letter(ax, BASES[idx], pos + 1, y, height)
                y += height

    ax.set_xlim(0.5, length + 0.5)
    ax.set_ylim(0, 2.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_ylabel(tf_name, rotation=0, labelpad=10, va="center", fontsize=8.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)


def render_panel_d(height_px: int, dpi: int = 300) -> Image.Image:
    pwms = parse_mmc3_pwms(ROOT / INPUT_XLSX)
    width_in = 1.55
    height_in = height_px / dpi
    fig, axes = plt.subplots(
        nrows=len(TF_ORDER),
        ncols=1,
        figsize=(width_in, height_in),
        dpi=dpi,
    )
    for ax, tf_name in zip(axes, TF_ORDER):
        draw_logo_compact(ax, tf_name, pwms[tf_name])

    fig.text(0.01, 0.985, "D", fontsize=8.6, fontweight="bold", ha="left", va="top")
    fig.text(0.04, 0.50, "Bits", rotation="vertical", fontsize=8.4, ha="center", va="center")
    fig.subplots_adjust(left=0.31, right=0.98, top=0.965, bottom=0.035, hspace=0.44)

    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, facecolor="white")
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("RGBA")


def main() -> None:
    if not ABC_PATH.exists():
        raise FileNotFoundError(ABC_PATH)

    abc = crop_white(Image.open(ABC_PATH).convert("RGBA"), pad=10)
    panel_d = render_panel_d(abc.height)

    gap = 28
    margin = 10
    canvas = Image.new("RGBA", (abc.width + gap + panel_d.width + margin, abc.height), "white")
    canvas.alpha_composite(abc, (0, 0))
    canvas.alpha_composite(panel_d, (abc.width + gap, 0))

    rgb = canvas.convert("RGB")
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT_PNG, dpi=(300, 300))
    rgb.save(OUT_PDF, "PDF", resolution=300.0)
    print("DONE")
    print(OUT_PNG)
    print(OUT_PDF)


if __name__ == "__main__":
    main()
