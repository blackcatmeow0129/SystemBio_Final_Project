#!/usr/bin/env python3
"""Cross-platform launcher for the Kang & Kim CRE figure reproduction code."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(cmd: list[str], cwd: Path | None = None, dry_run: bool = False) -> None:
    display = " ".join(str(part) for part in cmd)
    print(f"\n$ {display}")
    if dry_run:
        return
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def python_cmd() -> str:
    return sys.executable or "python"


def figure2(args: argparse.Namespace) -> None:
    py = python_cmd()
    run([py, "figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py"], dry_run=args.dry_run)
    run([py, "figures/Figure2/Figure2D/plot_fig2D_motif_logos.py"], dry_run=args.dry_run)
    run([py, "figures/Figure2/Figure2ABCD/combine_figure2_abcd.py"], dry_run=args.dry_run)


def figure3(args: argparse.Namespace) -> None:
    py = python_cmd()
    if args.figure3_part in {"a", "all"}:
        run([py, "figures/Figure3/Figure3A/plot_figure3a.py"], dry_run=args.dry_run)
    if args.figure3_part in {"de", "all"}:
        cmd = [
            py,
            "figures/Figure3/Figure3DE/generate_figure3de_xmls.py",
            "--data-dir",
            str(args.data_dir),
            "--fits-dir",
            str(args.fits_dir),
        ]
        run(cmd, dry_run=args.dry_run)
        print("Figure 3D fitting is intentionally not auto-started by this launcher.")
        print("Use the platform script after checking parallelism:")
        print("  mac/server: bash figures/Figure3/Figure3DE/run_figure3de_local.sh")
        print("  windows:    powershell -ExecutionPolicy Bypass -File figures/Figure3/Figure3DE/run_figure3de_windows.ps1")


def figure4(args: argparse.Namespace) -> None:
    py = python_cmd()
    if not args.best_xml:
        raise SystemExit("--best-xml is required for Figure 4A-K")
    run(
        [
            py,
            "figures/Figure4/Figure4AK/reproduce_figure4.py",
            "--best-xml",
            str(args.best_xml),
            "--mmc4",
            str(args.data_dir / "1-s2.0-S2589004223028249-mmc4.xlsx"),
            "--transcpp",
            str(args.transcpp),
        ],
        dry_run=args.dry_run,
    )
    run(
        [
            py,
            "figures/Figure4/Figure4LM/train_figure4lm.py",
            "--mode",
            "data-only",
            "--mmc4",
            str(args.data_dir / "1-s2.0-S2589004223028249-mmc4.xlsx"),
            "--fits-dir",
            str(args.fits_dir),
        ],
        dry_run=args.dry_run,
    )


def figure5(args: argparse.Namespace) -> None:
    py = python_cmd()
    run(
        [
            py,
            "figures/Figure5/plot_figure5.py",
            "--mmc2",
            str(args.data_dir / "1-s2.0-S2589004223028249-mmc2.xlsx"),
            "--mmc3",
            str(args.data_dir / "1-s2.0-S2589004223028249-mmc3.xlsx"),
            "--mmc4",
            str(args.data_dir / "1-s2.0-S2589004223028249-mmc4.xlsx"),
        ],
        dry_run=args.dry_run,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or print commands for Figure 2-5 reproduction.")
    parser.add_argument("--figure", choices=["2", "3", "4", "5", "all"], required=True)
    parser.add_argument("--figure3-part", choices=["a", "bc", "de", "all"], default="all")
    parser.add_argument("--data-dir", type=Path, default=Path(os.environ.get("CRE_DATA_DIR", "data")))
    parser.add_argument("--fits-dir", type=Path, default=Path(os.environ.get("CRE_FITS_DIR", "~/cre_reproduction/neoParSA/tests/transcpp/fits")).expanduser())
    parser.add_argument("--transcpp", type=Path, default=Path(os.environ.get("TRANSCPP", "~/cre_reproduction/transcpp/transcpp")).expanduser())
    parser.add_argument("--best-xml", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them.")
    args = parser.parse_args()

    selected = ["2", "3", "4", "5"] if args.figure == "all" else [args.figure]
    for item in selected:
        {"2": figure2, "3": figure3, "4": figure4, "5": figure5}[item](args)


if __name__ == "__main__":
    main()
