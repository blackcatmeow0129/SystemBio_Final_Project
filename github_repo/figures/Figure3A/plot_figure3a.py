"""
Figure 3A 그래프 생성 스크립트
rates 파일이 모두 완료된 후 실행

사용법:
    cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
    python3 /path/to/plot_figure3a.py
"""

import os, re, glob
import numpy as np
import openpyxl
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE  = os.path.expanduser("~/Desktop/SB_final/ScienceDirect_files_26May2026_04-41-20.049")
FITS  = os.path.expanduser("~/cre_reproduction/neoParSA/tests/transcpp/fits")
MMC4  = f"{BASE}/1-s2.0-S2589004223028249-mmc4.xlsx"
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT, exist_ok=True)

NON_FAMILY = ['DLX2','HOXA10','HOXA11','HOXA5','HOXA6','HOXA9',
              'HOXB9','HOXD13','NKX2-2','POU3F2','SOX4','TCF3','YY1','ZIC2']
FAMILY     = ['ATF1','ATF4','ATF7','CREB3','CREB5','CREM']
ALL_TFS    = ['CREB1'] + NON_FAMILY + FAMILY

TF_COLORS  = {
    'CREB1':'#E69F00',
    'DLX2':'#66C2A5','HOXA10':'#3288BD','HOXA11':'#2DC8A8','HOXA5':'#99D594',
    'HOXA6':'#A8DDB5','HOXA9':'#C6DBEF','HOXB9':'#9ECAE1','HOXD13':'#6BAED6',
    'NKX2-2':'#74C476','POU3F2':'#B2E2E2','SOX4':'#66C2A4','TCF3':'#E78AC3',
    'YY1':'#FC8D62','ZIC2':'#8DA0CB',
    'ATF1':'#E41A1C','ATF4':'#FF7F00','ATF7':'#4DAF4A',
    'CREB3':'#984EA3','CREB5':'#A6D854','CREM':'#FFD92F',
}

def load_meas_dict():
    wb   = openpyxl.load_workbook(MMC4)
    rows = list(wb['single-hit'].iter_rows(values_only=True))[1:]
    wt   = next(r[2] for r in rows if 'Promega_0' in str(r[0]) and 'scanmut' not in str(r[0]))
    return {r[0]: np.log2(r[2]/wt) for r in rows if r[0] and r[2] and re.search(r'pos_(\d+)_([ATGC])$', str(r[0]))}

def calc_r(rates_file, meas_dict):
    try:
        with open(rates_file) as f: lines = f.readlines()
        if len(lines) < 2: return None
        header = lines[0].strip().split()
        data   = lines[1].strip().split()
        pred   = {header[i+1]: float(data[i+1]) for i in range(len(header)-1)}
        wt_p   = pred.get('synCRE_Promega_0')
        if not wt_p or wt_p <= 0: return None
        pairs  = [(mv, np.log2(pred[n]/wt_p)) for n,mv in meas_dict.items() if n in pred and pred[n]>0]
        if len(pairs) < 10: return None
        r, _   = stats.pearsonr(*zip(*pairs))
        return r if not np.isnan(r) else None
    except: return None

def main():
    print("=== Figure 3A 그래프 생성 ===")
    meas_dict = load_meas_dict()

    results = {}
    for rates_file in glob.glob(f'{FITS}/fig3a_xmls/*.rates'):
        basename = rates_file.replace('.xml.rates','')
        tf_name  = '_'.join(basename.split('fig3a_m')[-1].split('_')[1:])
        r = calc_r(rates_file, meas_dict)
        if r is not None:
            results.setdefault(tf_name, []).append(r)

    print(f"TF 수: {len(results)}개")
    for tf in ALL_TFS:
        if tf in results:
            print(f"  {tf}: n={len(results[tf])}, mean={np.mean(results[tf]):.3f}")

    baseline_r = max(results.get('CREB1', [0.64]))
    tf_order   = [tf for tf in ALL_TFS if tf in results]
    data_box   = [results[tf] for tf in tf_order]
    n = len(tf_order)

    fig, ax = plt.subplots(figsize=(16, 7))
    ax.set_facecolor('#EBEBEB')
    fig.patch.set_facecolor('white')
    ax.grid(True, color='white', linewidth=1.2, zorder=0)

    bp = ax.boxplot(data_box, patch_artist=True, widths=0.55,
                    medianprops=dict(color='white', linewidth=2.5),
                    whiskerprops=dict(linewidth=1.5, color='gray'),
                    capprops=dict(linewidth=1.5, color='gray'),
                    flierprops=dict(marker='o', markersize=5, markerfacecolor='black', markeredgecolor='black', alpha=0.8),
                    zorder=3)
    for patch, tf in zip(bp['boxes'], tf_order):
        patch.set_facecolor(TF_COLORS.get(tf,'steelblue'))
        patch.set_alpha(0.9); patch.set_edgecolor('gray'); patch.set_linewidth(1.0)

    ax.axhline(baseline_r, color='red', linewidth=2.5, zorder=5)
    ax.annotate('The best CREB1_self model score',
                xy=(1, baseline_r), xytext=(2.5, baseline_r+0.05), fontsize=10,
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5), color='black', zorder=6)

    non_fam_end = 1 + len([t for t in NON_FAMILY if t in results])
    ax.axvline(0.5,               color='black', linestyle='--', linewidth=1.5, alpha=0.8, zorder=4)
    ax.axvline(non_fam_end + 0.5, color='black', linestyle='--', linewidth=1.5, alpha=0.8, zorder=4)
    ax.text((1+non_fam_end)/2+0.5, 0.41, 'non-family TFs', ha='center', fontsize=13, color='#555555', style='italic')
    ax.text((non_fam_end+1+n)/2+0.5, 0.41, 'CREB family TFs', ha='center', fontsize=13, color='#555555', style='italic')

    ax.set_xticks(range(1, n+1))
    ax.set_xticklabels(tf_order, rotation=45, ha='right', fontsize=10)
    ax.set_ylabel("Pearson's R", fontsize=13)
    ax.set_ylim(0.4, 0.9); ax.set_xlim(0, n+1)
    ax.tick_params(axis='both', which='both', length=0)
    for spine in ax.spines.values(): spine.set_visible(False)

    plt.tight_layout()
    out = f"{OUTPUT}/Figure3A.png"
    plt.savefig(out, dpi=150, bbox_inches='tight')
    print(f"✅ 저장: {out}")

if __name__ == '__main__':
    main()
