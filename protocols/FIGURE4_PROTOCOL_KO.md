# Figure 4A-M 재현 프로토콜

## 패널 구성

| 패널 | 구현 파일 | 설명 |
|---|---|---|
| 4A-C | `figures/Figure4/Figure4AK/reproduce_figure4.py` | reverse/rearrange/reverse+rearrange 구조 schematic |
| 4D-F | `reproduce_figure4.py` | thermodynamic model prediction |
| 4G-I | `reproduce_figure4.py`, `generate_figure4k_qsam.py` | QSAM prediction |
| 4J | `reproduce_figure4.py` | multi-hit thermodynamic prediction |
| 4K | `reproduce_figure4.py`, `generate_figure4k_qsam.py` | multi-hit QSAM prediction |
| 4L-M | `figures/Figure4/Figure4LM/train_figure4lm.py` | TF 수별 multi-hit 예측 R |

## Figure 4A-K

```bash
python figures/Figure4/Figure4AK/reproduce_figure4.py \
  --best-xml /path/to/best_fit.xml \
  --mmc4 /path/to/1-s2.0-S2589004223028249-mmc4.xlsx \
  --transcpp /path/to/transcpp \
  --threads 14
```

출력:

- `Figure4_A-K_selected_4TF.png`
- `Figure4_A-K_selected_4TF.pdf`
- `figure4_metrics.tsv`
- `figure4_panel_data.tsv`

## QSAM 단독 확인

transcpp 없이 Figure 4G/H/I/K만 확인할 때:

```bash
python figures/Figure4/Figure4AK/generate_figure4k_qsam.py \
  --mmc4 /path/to/1-s2.0-S2589004223028249-mmc4.xlsx
```

## Figure 4L/M

기존 Figure 3B/D/E rates를 사용하는 빠른 모드:

```bash
python figures/Figure4/Figure4LM/train_figure4lm.py \
  --mode data-only \
  --mmc4 /path/to/1-s2.0-S2589004223028249-mmc4.xlsx \
  --fits-dir /path/to/neoParSA/tests/transcpp/fits
```

새로 학습하는 full 모드는 계산량이 매우 크다.

```bash
python figures/Figure4/Figure4LM/train_figure4lm.py \
  --mode full \
  --mmc4 /path/to/1-s2.0-S2589004223028249-mmc4.xlsx \
  --transcpp /path/to/transcpp
```
