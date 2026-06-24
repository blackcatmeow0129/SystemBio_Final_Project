# Figure 패널별 구현 현황

이 파일은 Figure 2A-D, Figure 3A-E, Figure 4A-M, Figure 5A-K가 GitHub 저장소 안에서 어떤 코드와 프로토콜로 재현되는지 확인하기 위한 체크리스트다.

## Figure 2A-D

| 패널 | 구현 코드 | 실행/설명 |
|---|---|---|
| 2A | `figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py` | 7TF self-competition single-hit fitting 결과 시각화 |
| 2B | `figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py` | CREB1-only/best model 비교 패널 |
| 2C | `figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py`, `generate_figure2c_4TF.py` | 7TF 및 4TF 버전 생성 |
| 2D | `figures/Figure2/Figure2D/plot_fig2D_motif_logos.py` | TF PWM motif logo |
| 2A-D combined | `figures/Figure2/Figure2ABCD/combine_figure2_abcd.py` | Figure 2A-D 통합 이미지 |

프로토콜: `protocols/FIGURE2_PROTOCOL_KO.md`

## Figure 3A-E

| 패널 | 구현 코드 | 실행/설명 |
|---|---|---|
| 3A | `figures/Figure3/Figure3A/plot_figure3a.py` | CREB family/non-family TF 비교 |
| 3B | `figures/Figure3/Figure3BC/build_figure3bc.py` | self-competition 없는 single-hit fitting R |
| 3C | `figures/Figure3/Figure3BC/build_figure3bc.py` | 3B 모델을 multi-hit에 forward prediction |
| 3D | `figures/Figure3/Figure3DE/generate_figure3de_xmls.py`, `run_figure3de_local.sh`, `run_figure3de_server.sh`, `run_figure3de_windows.ps1`, `plot_figure3de.py` | self-competition 있는 single-hit fitting R |
| 3E | `figures/Figure3/Figure3DE/generate_figure3e_mh.py`, `run_figure3e_mh.sh`, `run_figure3e_mh_windows.ps1`, `plot_figure3de.py` | 3D 모델을 multi-hit에 forward prediction |

프로토콜: `protocols/FIGURE3_PROTOCOL_KO.md`

## Figure 4A-M

| 패널 | 구현 코드 | 실행/설명 |
|---|---|---|
| 4A | `figures/Figure4/Figure4AK/reproduce_figure4.py` | reverse schematic |
| 4B | `figures/Figure4/Figure4AK/reproduce_figure4.py` | rearrange schematic |
| 4C | `figures/Figure4/Figure4AK/reproduce_figure4.py` | reverse+rearrange schematic |
| 4D | `figures/Figure4/Figure4AK/reproduce_figure4.py` | reverse thermodynamic prediction |
| 4E | `figures/Figure4/Figure4AK/reproduce_figure4.py` | rearrange thermodynamic prediction |
| 4F | `figures/Figure4/Figure4AK/reproduce_figure4.py` | reverse+rearrange thermodynamic prediction |
| 4G | `figures/Figure4/Figure4AK/reproduce_figure4.py`, `generate_figure4k_qsam.py` | reverse QSAM prediction |
| 4H | `figures/Figure4/Figure4AK/reproduce_figure4.py`, `generate_figure4k_qsam.py` | rearrange QSAM prediction |
| 4I | `figures/Figure4/Figure4AK/reproduce_figure4.py`, `generate_figure4k_qsam.py` | reverse+rearrange QSAM prediction |
| 4J | `figures/Figure4/Figure4AK/reproduce_figure4.py` | multi-hit thermodynamic prediction |
| 4K | `figures/Figure4/Figure4AK/reproduce_figure4.py`, `generate_figure4k_qsam.py` | multi-hit QSAM prediction |
| 4L | `figures/Figure4/Figure4LM/train_figure4lm.py` | no-self multi-hit prediction by TF count |
| 4M | `figures/Figure4/Figure4LM/train_figure4lm.py` | self-competition multi-hit prediction by TF count |

프로토콜: `protocols/FIGURE4_PROTOCOL_KO.md`

## Figure 5A-K

| 패널 | 구현 코드 | 실행/설명 |
|---|---|---|
| 5A | `figures/Figure5/plot_figure5.py` | A substitution activity, measured/model |
| 5B | `figures/Figure5/plot_figure5.py` | WT TFBS occupancy track |
| 5C | `figures/Figure5/plot_figure5.py` | CRE1 A-substitution TFBS boxes |
| 5D | `figures/Figure5/plot_figure5.py` | CRE4 A-substitution TFBS boxes |
| 5E | `figures/Figure5/plot_figure5.py` | TF activation coefficients |
| 5F | `figures/Figure5/plot_figure5.py` | A-substitution DDA |
| 5G | `figures/Figure5/plot_figure5.py` | T substitution activity, measured/model |
| 5H | `figures/Figure5/plot_figure5.py` | WT TFBS occupancy track |
| 5I | `figures/Figure5/plot_figure5.py` | CRE1 T-substitution TFBS boxes |
| 5J | `figures/Figure5/plot_figure5.py` | CRE4 T-substitution TFBS boxes |
| 5K | `figures/Figure5/plot_figure5.py` | T-substitution DDA |

프로토콜: `protocols/FIGURE5_PROTOCOL_KO.md`

## 공통 실행 문서

- 전체 순서: `protocols/RUN_ALL_FIGURES_KO.md`
- OS별 설치: `environment/mac/SETUP_MAC.md`, `environment/server/SETUP_SERVER.md`, `environment/windows/SETUP_WINDOWS.md`
- 명령 미리보기/launcher: `run_reproduction.py`
