# Kang & Kim 2024 (iScience) — CRE Enhancer Reproduction

> **Paper**: Deep molecular learning of transcriptional control of a synthetic CRE enhancer and its variants  
> **Authors**: Chan-Koo Kang, Ah-Ram Kim | **Journal**: iScience 27, 108747 (2024)  
> **DOI**: https://doi.org/10.1016/j.isci.2023.108747

---

## Reproduced Figures

| Figure | Description | Platform Used | Status |
|---|---|---|---|
| **2A-C** | 7TF self-competition model, single-hit fitting | Windows | ✅ |
| **2D** | TF PWM motif logos | Windows | ✅ |
| **3A** | R by TF type (non-family vs CREB family) | Server | ✅ |
| **3B** | Without self-competition, fitting R by # TFs | Windows + Server | ✅ |
| **3C** | Without self-competition, multi-hit prediction R | Windows + Server | ✅ |
| **3D** | With self-competition, fitting R by # TFs | Mac (n1-4) + Server (n5-7) | ✅ |
| **3E** | With self-competition, multi-hit prediction R | Server | ✅ |
| **4D-K** | Thermodynamic + QSAM predictions | Windows | ✅ |
| **4L/M** | Multi-hit prediction by TF count (data-only) | — | ✅ |
| **5A/E/G** | Δactivity bar plots + TF activation coefficients | Windows | ✅ |

---

## Repository Structure

```
kang2024-cre-reproduction/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── README.md                          # 데이터 다운로드 안내
│
├── environment/
│   ├── mac/
│   │   └── SETUP_MAC.md                   # Mac M1 환경 설정
│   ├── windows/
│   │   └── SETUP_WINDOWS.md               # Windows 환경 설정
│   └── server/
│       └── SETUP_SERVER.md                # Linux 서버 환경 설정
│
├── figures/
│   ├── Figure2/
│   │   ├── Figure2ABC/
│   │   │   ├── plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py   # 팀원 완성 (Windows)
│   │   │   └── generate_figure2c_4TF.py                      # 4TF 버전 (Mac/Server)
│   │   ├── Figure2D/
│   │   │   └── plot_fig2D_motif_logos.py                     # 팀원 완성 (Windows)
│   │   └── Figure2ABCD/
│   │       └── combine_figure2_abcd.py                       # A-D 합치기 (Windows)
│   │
│   ├── Figure3/
│   │   ├── Figure3A/
│   │   │   └── plot_figure3a.py
│   │   ├── Figure3BC/
│   │   │   ├── build_figure3bc.py                            # 팀원 완성
│   │   │   └── selected_fit_manifest.tsv
│   │   └── Figure3DE/
│   │       ├── generate_figure3de_xmls.py                    # XML 생성
│   │       ├── run_figure3de_local.sh                        # Mac: n1-4
│   │       ├── run_figure3de_server.sh                       # Server: n5-7
│   │       ├── generate_figure3e_mh.py                       # multi-hit XML
│   │       ├── run_figure3e_mh.sh                            # Server: Fig3E
│   │       └── plot_figure3de.py                             # 그래프 생성
│   │
│   ├── Figure4/
│   │   ├── Figure4AK/
│   │   │   ├── reproduce_figure4.py                          # 팀원 완성 (Fig4A-K)
│   │   │   └── generate_figure4k_qsam.py                     # QSAM (standalone)
│   │   └── Figure4LM/
│   │       └── train_figure4lm.py                            # 4L/M (data-only + full)
│   │
│   └── Figure5/
│       └── plot_figure5.py                                   # 팀원 완성
│
└── protocols/
    ├── FIGURE2_PROTOCOL_KO.md
    ├── FIGURE3_PROTOCOL_KO.md
    └── TIPS_AND_TROUBLESHOOTING.md
```

---

## Quick Start

### Step 1 — 데이터 다운로드

[https://doi.org/10.1016/j.isci.2023.108747](https://doi.org/10.1016/j.isci.2023.108747) 접속 →  
Supplementary information → 아래 3개 파일 다운로드 → `data/` 폴더에 저장

| 파일 | 내용 |
|---|---|
| `mmc2.xlsx` | 모델 파라미터 (4TF_self, 7TF, 7TF_self) |
| `mmc3.xlsx` | TF PWM |
| `mmc4.xlsx` | 서열 + 발현량 |

### Step 2 — 환경 설정

환경에 맞는 가이드를 따라 설치:

| 환경 | 가이드 |
|---|---|
| 🍎 Mac M1 | [`environment/mac/SETUP_MAC.md`](environment/mac/SETUP_MAC.md) |
| 🪟 Windows | [`environment/windows/SETUP_WINDOWS.md`](environment/windows/SETUP_WINDOWS.md) |
| 🖥️ Linux Server | [`environment/server/SETUP_SERVER.md`](environment/server/SETUP_SERVER.md) |

```bash
# Python 패키지 (공통)
pip install -r requirements.txt
```

### Step 3 — Figure별 실행

#### Figure 2 (Windows 권장 / Mac 가능)

```bash
# Figure 2A-C: 7TF self-competition 모델
cd 작업폴더
python3 figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py

# Figure 2D: PWM motif logos
python3 figures/Figure2/Figure2D/plot_fig2D_motif_logos.py

# Figure 2A-D 합치기
python3 figures/Figure2/Figure2ABCD/combine_figure2_abcd.py
```

필요 입력 파일:
```
model_input/expression/single_hit_expression.csv        ← mmc4 single-hit 시트
model_input/predictions/7TF_self_single_hit_fixed_rates.tsv  ← transcpp 출력
model_input/predictions/CREB1_only_single_hit_rates.tsv      ← transcpp 출력
```

#### Figure 3A (서버 권장)

```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 figures/Figure3/Figure3A/plot_figure3a.py
# rates 파일 완료 후: python3 plot_figure3a.py
```

#### Figure 3B/C (팀원 스크립트)

```bash
python3 figures/Figure3/Figure3BC/build_figure3bc.py \
    --transcpp /path/to/transcpp \
    --mmc4 /path/to/mmc4.xlsx \
    --runs 4 --parallel 4
```

#### Figure 3D/E (Mac + 서버 분담)

```bash
# 1. XML 생성
python3 figures/Figure3/Figure3DE/generate_figure3de_xmls.py

# 2. 로컬 (Mac M1): n1~n4
bash figures/Figure3/Figure3DE/run_figure3de_local.sh

# 3. 서버: n5~n7 역순
bash figures/Figure3/Figure3DE/run_figure3de_server.sh

# 4. 로컬 rates → 서버 전송
scp -J jumpserver@서버주소 ~/cre_reproduction/.../fig3de_xmls/*.rates \
    user@server:~/cre_reproduction/.../fig3de_xmls/

# 5. 서버: multi-hit XML 생성 + 실행 (Fig3E)
python3 figures/Figure3/Figure3DE/generate_figure3e_mh.py
bash figures/Figure3/Figure3DE/run_figure3e_mh.sh

# 6. 그래프
python3 figures/Figure3/Figure3DE/plot_figure3de.py
```

#### Figure 4D-K (Windows 팀원 완성 / Mac+Server 가능)

```bash
python3 figures/Figure4/Figure4AK/reproduce_figure4.py \
    --best-xml /path/to/best_fit.xml \
    --mmc4 /path/to/mmc4.xlsx \
    --transcpp /path/to/transcpp
```

#### Figure 4L/M

```bash
# data-only 모드 (기존 rates 파일 사용, 빠름)
python3 figures/Figure4/Figure4LM/train_figure4lm.py \
    --mode data-only \
    --mmc4 /path/to/mmc4.xlsx

# full 모드 (transcpp 새로 학습, 매우 오래 걸림)
python3 figures/Figure4/Figure4LM/train_figure4lm.py \
    --mode full \
    --mmc4 /path/to/mmc4.xlsx \
    --transcpp /path/to/transcpp
```

#### Figure 5 (Windows 팀원 완성 / Mac+Server 가능)

```bash
python3 figures/Figure5/plot_figure5.py \
    --mmc2 /path/to/mmc2.xlsx \
    --mmc3 /path/to/mmc3.xlsx \
    --mmc4 /path/to/mmc4.xlsx
```

---

## Platform Guide Summary

| Figure | 🍎 Mac M1 | 🪟 Windows | 🖥️ Server |
|---|---|---|---|
| 2A-C | ✅ (4TF 버전) | ✅ 팀원 완성 | ✅ |
| 2D | ✅ | ✅ 팀원 완성 | ✅ |
| 3A | ⚠️ 느림 | ⚠️ | ✅ 권장 |
| 3B/C | ✅ | ✅ 팀원 완성 | ✅ 권장 |
| 3D (n1-4) | ✅ 담당 | ✅ | ✅ |
| 3D (n5-7) | ⚠️ 매우 느림 | ⚠️ | ✅ 권장 |
| 3E | ❌ segfault | ✅ | ✅ 필수 |
| 4D-K | ✅ | ✅ 팀원 완성 | ✅ |
| 4L/M | ✅ data-only | ✅ | ✅ |
| 5 | ✅ | ✅ 팀원 완성 | ✅ |

---

## Key Notes

1. **transcpp는 `fits/` 폴더에서 실행** — FASTA 상대경로 문제
2. **Mac M1은 multi-hit 722개에서 segfault** — Figure 3E는 서버 필수
3. **NumThreads=1 + 병렬 프로세스 수로 제어** — 서버에서 25개 권장
4. **nohup 스크립트를 먼저 kill** — `pkill -9 -f run_fig3` → `pkill -9 -f transcpp`
5. **FASTA는 60자 줄바꿈 형식**
6. **Figure 3C/E는 3B/D를 재활용** — 추가 학습 불필요

---

## Citation

```bibtex
@article{kang2024deep,
  title={Deep molecular learning of transcriptional control of a synthetic CRE enhancer and its variants},
  author={Kang, Chan-Koo and Kim, Ah-Ram},
  journal={iScience},
  volume={27},
  number={1},
  pages={108747},
  year={2024},
  publisher={Elsevier},
  doi={10.1016/j.isci.2023.108747}
}
```
