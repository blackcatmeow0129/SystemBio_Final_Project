# Figure 2-5 전체 재현 실행 순서

이 문서는 저장소를 처음 받은 사람이 Mac, Linux 서버, Windows에서 같은 순서로 Figure 2A-D, Figure 3A-E, Figure 4A-M, Figure 5A-K를 재현하기 위한 최소 실행 순서다.

## 0. 공통 준비

1. `data/` 또는 원하는 데이터 폴더에 아래 파일을 둔다.

| 파일 | 용도 |
|---|---|
| `1-s2.0-S2589004223028249-mmc2.xlsx` | 모델 파라미터 |
| `1-s2.0-S2589004223028249-mmc3.xlsx` | TF PWM |
| `1-s2.0-S2589004223028249-mmc4.xlsx` | MPRA 서열/발현량 |

2. Python 환경을 만든다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. transcpp는 `environment/`의 운영체제별 문서를 따라 빌드한다.

## 1. Figure 2A-D

```bash
python figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py
python figures/Figure2/Figure2D/plot_fig2D_motif_logos.py
python figures/Figure2/Figure2ABCD/combine_figure2_abcd.py
```

입력 rates 파일은 Figure 2 스크립트의 `model_input/` 구조에 맞춘다. Windows에서 만든 rates도 Mac/Linux에서 그대로 사용할 수 있다.

## 2. Figure 3A-E

Figure 3은 계산량이 크므로 보통 Mac/Windows는 n1-n4, 서버는 n5-n7 및 multi-hit을 맡긴다.

```bash
python figures/Figure3/Figure3A/plot_figure3a.py
```

Figure 3B/C는 완료된 no-self fitting 결과 두 묶음과 multi-hit FASTA가 필요하다.

```bash
python figures/Figure3/Figure3BC/build_figure3bc.py \
  --forward-results /path/to/forward_results \
  --reverse-results /path/to/reverse_results \
  --supplementary-json /path/to/supplementary.json \
  --multi-hit-fasta /path/to/MRPA_multihit.fa \
  --transcpp /path/to/transcpp \
  --runtime-dir /path/to/transcpp_runtime \
  --output-dir /path/to/figure3bc_output \
  --runs 4 --threads 4 --parallel 4
```

Figure 3D XML 생성:

```bash
python figures/Figure3/Figure3DE/generate_figure3de_xmls.py \
  --data-dir /path/to/data \
  --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits \
  --num-threads 1
```

Mac/Linux:

```bash
FITS=~/cre_reproduction/neoParSA/tests/transcpp/fits \
TRANSCPP=~/cre_reproduction/transcpp/transcpp \
PARALLEL=7 TF_COUNTS="1 2 3 4" \
bash figures/Figure3/Figure3DE/run_figure3de_local.sh
```

Linux 서버:

```bash
FITS=~/cre_reproduction/neoParSA/tests/transcpp/fits \
TRANSCPP=~/cre_reproduction/transcpp/transcpp \
PARALLEL=25 TF_COUNTS="7 6 5" \
nohup bash figures/Figure3/Figure3DE/run_figure3de_server.sh > fig3de_server.log 2>&1 &
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File figures\Figure3\Figure3DE\run_figure3de_windows.ps1 `
  -Fits "$HOME\cre_reproduction\neoParSA\tests\transcpp\fits" `
  -Transcpp "$HOME\cre_reproduction\transcpp\transcpp.exe" `
  -Parallel 6 `
  -TfCounts 1,2,3,4
```

Figure 3E multi-hit XML과 실행:

```bash
python figures/Figure3/Figure3DE/generate_figure3e_mh.py \
  --data-dir /path/to/data \
  --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits

bash figures/Figure3/Figure3DE/run_figure3e_mh.sh
python figures/Figure3/Figure3DE/plot_figure3de.py
```

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File figures\Figure3\Figure3DE\run_figure3e_mh_windows.ps1
```

## 3. Figure 4A-M

Figure 4A-K:

```bash
python figures/Figure4/Figure4AK/reproduce_figure4.py \
  --best-xml /path/to/best_fit.xml \
  --mmc4 /path/to/data/1-s2.0-S2589004223028249-mmc4.xlsx \
  --transcpp /path/to/transcpp
```

Figure 4G/H/I/K QSAM만 빠르게 확인:

```bash
python figures/Figure4/Figure4AK/generate_figure4k_qsam.py \
  --mmc4 /path/to/data/1-s2.0-S2589004223028249-mmc4.xlsx
```

Figure 4L/M:

```bash
python figures/Figure4/Figure4LM/train_figure4lm.py \
  --mode data-only \
  --mmc4 /path/to/data/1-s2.0-S2589004223028249-mmc4.xlsx \
  --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits
```

## 4. Figure 5A-K

```bash
python figures/Figure5/plot_figure5.py \
  --mmc2 /path/to/data/1-s2.0-S2589004223028249-mmc2.xlsx \
  --mmc3 /path/to/data/1-s2.0-S2589004223028249-mmc3.xlsx \
  --mmc4 /path/to/data/1-s2.0-S2589004223028249-mmc4.xlsx
```

`--xml`, `--rates`, `--unfold`를 같이 주면 모델 예측, TFBS occupancy, DDA 패널까지 논문형 layout으로 채워진다.

## 5. 명령 미리보기

전체 명령을 실행하지 않고 확인하려면:

```bash
python run_reproduction.py --figure all --data-dir /path/to/data --best-xml /path/to/best_fit.xml --dry-run
```
