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
| **4A-K** | Schematics + thermodynamic + QSAM predictions | Windows/Mac/Server | ✅ |
| **4L/M** | Multi-hit prediction by TF count (data-only/full) | Windows/Mac/Server | ✅ |
| **5A-K** | A/T substitution activity, TFBS, coefficients, DDA | Windows/Mac/Server | ✅ |

---

## Repository Structure

```
kang2024-cre-reproduction/
│
├── README.md
├── requirements.txt
├── run_reproduction.py                    # 공통 실행/명령 미리보기 launcher
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
│   │       ├── run_figure3de_windows.ps1                     # Windows: n 선택 실행
│   │       ├── generate_figure3e_mh.py                       # multi-hit XML
│   │       ├── run_figure3e_mh.sh                            # Server: Fig3E
│   │       ├── run_figure3e_mh_windows.ps1                   # Windows: Fig3E
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
    ├── FIGURE4_PROTOCOL_KO.md
    ├── FIGURE5_PROTOCOL_KO.md
    ├── PANEL_COVERAGE_KO.md
    ├── RUN_ALL_FIGURES_KO.md
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
    --forward-results /path/to/forward_results \
    --reverse-results /path/to/reverse_results \
    --supplementary-json /path/to/supplementary.json \
    --multi-hit-fasta /path/to/MRPA_multihit.fa \
    --transcpp /path/to/transcpp \
    --runtime-dir /path/to/transcpp_runtime \
    --output-dir /path/to/figure3bc_output \
    --runs 4 --threads 4 --parallel 4
```

#### Figure 3D/E (Mac + 서버 분담)

```bash
# 1. XML 생성
python3 figures/Figure3/Figure3DE/generate_figure3de_xmls.py \
    --data-dir /path/to/data \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits \
    --num-threads 1

# 2. 로컬 (Mac M1): n1~n4
FITS=~/cre_reproduction/neoParSA/tests/transcpp/fits \
TRANSCPP=~/cre_reproduction/transcpp/transcpp \
PARALLEL=7 TF_COUNTS="1 2 3 4" \
bash figures/Figure3/Figure3DE/run_figure3de_local.sh

# 3. 서버: n5~n7 역순
FITS=~/cre_reproduction/neoParSA/tests/transcpp/fits \
TRANSCPP=~/cre_reproduction/transcpp/transcpp \
PARALLEL=25 TF_COUNTS="7 6 5" \
bash figures/Figure3/Figure3DE/run_figure3de_server.sh

# 4. 로컬 rates → 서버 전송
scp -J jumpserver@서버주소 ~/cre_reproduction/.../fig3de_xmls/*.rates \
    user@server:~/cre_reproduction/.../fig3de_xmls/

# 5. 서버: multi-hit XML 생성 + 실행 (Fig3E)
python3 figures/Figure3/Figure3DE/generate_figure3e_mh.py \
    --data-dir /path/to/data \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits
bash figures/Figure3/Figure3DE/run_figure3e_mh.sh

# 6. 그래프
python3 figures/Figure3/Figure3DE/plot_figure3de.py
```

#### Figure 4A-K (Windows 팀원 완성 / Mac+Server 가능)

```bash
python3 figures/Figure4/Figure4AK/reproduce_figure4.py \
    --best-xml /path/to/best_fit.xml \
    --mmc4 /path/to/mmc4.xlsx \
    --transcpp /path/to/transcpp
```

QSAM만 빠르게 확인:

```bash
python3 figures/Figure4/Figure4AK/generate_figure4k_qsam.py \
    --mmc4 /path/to/mmc4.xlsx
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

#### Figure 5A-K (Windows 팀원 완성 / Mac+Server 가능)

```bash
python3 figures/Figure5/plot_figure5.py \
    --mmc2 /path/to/mmc2.xlsx \
    --mmc3 /path/to/mmc3.xlsx \
    --mmc4 /path/to/mmc4.xlsx
```

패널별 구현 체크리스트는 [`protocols/PANEL_COVERAGE_KO.md`](protocols/PANEL_COVERAGE_KO.md), 전체 실행 순서는 [`protocols/RUN_ALL_FIGURES_KO.md`](protocols/RUN_ALL_FIGURES_KO.md)를 먼저 보세요. 명령만 미리 확인하려면:

```bash
python3 run_reproduction.py --figure all --data-dir /path/to/data --best-xml /path/to/best_fit.xml --dry-run
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

## Fastest Recommended Order in Limited Environments

제한된 환경에서 가장 빨리 결과를 확인하려면, **오래 걸리는 Figure 3 fitting을 마지막으로 미루고** 데이터/기존 rates로 그릴 수 있는 패널부터 확인하는 것을 권장합니다.

### 0. 먼저 준비할 것

| 선행 업무 | 이유 |
|---|---|
| `mmc2.xlsx`, `mmc3.xlsx`, `mmc4.xlsx`를 `data/`에 배치 | 모든 Figure의 공통 입력 |
| Python 패키지 설치 | Figure 2/4 QSAM/5는 Python만으로 상당 부분 확인 가능 |
| transcpp + printRate patch 빌드 | Figure 3 fitting, Figure 4 thermodynamic prediction에 필요 |
| `fits/` 폴더와 `sequences/` 폴더 생성 | transcpp 상대경로 문제 방지 |

### 1. 가장 먼저: Python-only 또는 기존 입력으로 빠르게 확인

```bash
# Figure 2D: PWM motif logo, 빠름
python3 figures/Figure2/Figure2D/plot_fig2D_motif_logos.py

# Figure 4G/H/I/K QSAM만 확인, transcpp 불필요
python3 figures/Figure4/Figure4AK/generate_figure4k_qsam.py \
    --mmc4 data/1-s2.0-S2589004223028249-mmc4.xlsx

# Figure 5A-K: mmc2/3/4만으로 MPRA, PWM 기반 TFBS/DDA 확인 가능
python3 figures/Figure5/plot_figure5.py \
    --mmc2 data/1-s2.0-S2589004223028249-mmc2.xlsx \
    --mmc3 data/1-s2.0-S2589004223028249-mmc3.xlsx \
    --mmc4 data/1-s2.0-S2589004223028249-mmc4.xlsx
```

이 단계는 노트북에서도 빨리 돌릴 수 있다. 단, Figure 5의 lower model activity와 occupancy를 논문처럼 채우려면 `--xml`, `--rates`, `--unfold`를 추가하는 것이 좋다.

### 2. 기존 rates/XML이 있으면 바로 그리기

이미 `best_fit.xml`, `.rates`, Figure 3 결과가 있으면 새 fitting 없이 아래를 먼저 실행한다.

```bash
# Figure 2A-D: 기존 single-hit rates 필요
python3 figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py
python3 figures/Figure2/Figure2ABCD/combine_figure2_abcd.py

# Figure 4A-K: best_fit.xml + transcpp 필요
python3 figures/Figure4/Figure4AK/reproduce_figure4.py \
    --best-xml /path/to/best_fit.xml \
    --mmc4 data/1-s2.0-S2589004223028249-mmc4.xlsx \
    --transcpp /path/to/transcpp

# Figure 4L/M: 기존 Figure 3 rates를 읽는 data-only 모드
python3 figures/Figure4/Figure4LM/train_figure4lm.py \
    --mode data-only \
    --mmc4 data/1-s2.0-S2589004223028249-mmc4.xlsx \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits
```

### 3. 그 다음: Figure 3 중 계산량 작은 것부터

Figure 3은 전체에서 시간이 가장 오래 걸린다. 제한된 환경에서는 아래 순서가 가장 낫다.

| 순서 | 작업 | 권장 환경 | 이유 |
|---:|---|---|---|
| 1 | Figure 3A | 서버 또는 빠른 로컬 | 독립 실행, 결과 확인용 |
| 2 | Figure 3B/C | Windows/서버 | no-self 모델, C는 B 재사용 |
| 3 | Figure 3D n1-n4 | Mac M1/Windows | 상대적으로 작고 병렬 효율 좋음 |
| 4 | Figure 3D n5-n7 | Linux 서버 | TF 수가 커져 오래 걸림 |
| 5 | Figure 3E | Linux 서버 권장 | 722개 multi-hit 예측, Mac M1 segfault 경험 있음 |

```bash
# Figure 3D XML 생성
python3 figures/Figure3/Figure3DE/generate_figure3de_xmls.py \
    --data-dir data \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits \
    --num-threads 1

# Mac/Windows/로컬: n1-n4 먼저
FITS=~/cre_reproduction/neoParSA/tests/transcpp/fits \
TRANSCPP=~/cre_reproduction/transcpp/transcpp \
PARALLEL=7 TF_COUNTS="1 2 3 4" \
bash figures/Figure3/Figure3DE/run_figure3de_local.sh

# 서버: n7부터 역순으로 n5까지
FITS=~/cre_reproduction/neoParSA/tests/transcpp/fits \
TRANSCPP=~/cre_reproduction/transcpp/transcpp \
PARALLEL=25 TF_COUNTS="7 6 5" \
nohup bash figures/Figure3/Figure3DE/run_figure3de_server.sh > fig3de_server.log 2>&1 &
```

### 4. 마지막: multi-hit 예측과 최종 plotting

Figure 3D fitting rates가 모이면 Figure 3E는 새 학습이 아니라 forward prediction이다.

```bash
python3 figures/Figure3/Figure3DE/generate_figure3e_mh.py \
    --data-dir data \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits

bash figures/Figure3/Figure3DE/run_figure3e_mh.sh
python3 figures/Figure3/Figure3DE/plot_figure3de.py
```

### 빠른 판단 기준

| 상황 | 추천 |
|---|---|
| 노트북만 있음 | Figure 2, Figure 4 QSAM, Figure 5부터 확인 |
| transcpp 빌드 전 | `generate_figure4k_qsam.py`, Figure 5 기본 실행부터 |
| 기존 `.rates`가 있음 | 새 fitting보다 plotting/data-only 모드 우선 |
| 서버 시간이 제한됨 | Figure 3D n5-n7과 Figure 3E만 서버에 배정 |
| Figure 하나만 먼저 검증 | Figure 5 또는 Figure 4 QSAM이 가장 빠름 |

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
