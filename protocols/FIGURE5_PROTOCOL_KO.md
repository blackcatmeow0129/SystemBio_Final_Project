# Figure 5A-K 재현 프로토콜

## 패널 구성

| 패널 | 내용 | 구현 |
|---|---|---|
| 5A | A substitution measured/model activity | `plot_figure5.py` |
| 5B | WT TFBS occupancy track | `plot_figure5.py` |
| 5C-D | CRE1/CRE4 A substitution site boxes | `plot_figure5.py` |
| 5E | TF activation coefficients | `plot_figure5.py` |
| 5F | A substitution DDA | `plot_figure5.py` |
| 5G | T substitution measured/model activity | `plot_figure5.py` |
| 5H | WT TFBS occupancy track | `plot_figure5.py` |
| 5I-J | CRE1/CRE4 T substitution site boxes | `plot_figure5.py` |
| 5K | T substitution DDA | `plot_figure5.py` |

## 최소 실행

```bash
python figures/Figure5/plot_figure5.py \
  --mmc2 /path/to/1-s2.0-S2589004223028249-mmc2.xlsx \
  --mmc3 /path/to/1-s2.0-S2589004223028249-mmc3.xlsx \
  --mmc4 /path/to/1-s2.0-S2589004223028249-mmc4.xlsx
```

## 모델 예측과 occupancy까지 포함

```bash
python figures/Figure5/plot_figure5.py \
  --mmc2 /path/to/1-s2.0-S2589004223028249-mmc2.xlsx \
  --mmc3 /path/to/1-s2.0-S2589004223028249-mmc3.xlsx \
  --mmc4 /path/to/1-s2.0-S2589004223028249-mmc4.xlsx \
  --xml /path/to/best_fit.xml \
  --rates /path/to/best_fit.output.rates \
  --unfold /path/to/unfold_or_unfold.exe
```

출력:

- `results/Figure5_paper_detail_refined.png`
- `results/Figure5_paper_detail_refined.pdf`
- `results/panel_data_refined/activity_A.tsv`
- `results/panel_data_refined/activity_T.tsv`
- `results/panel_data_refined/DDA_A.tsv`
- `results/panel_data_refined/DDA_T.tsv`
- `results/panel_data_refined/summary_metrics.json`
