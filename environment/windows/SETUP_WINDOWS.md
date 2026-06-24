# Windows 환경 설정 가이드

> 실제 구현에 사용된 환경: **Windows 11 (팀원 PC)**  
> Figure 2A-D, Figure 3B/C 생성에 사용

---

## 1. MSYS2 설치 (transcpp 빌드용)

1. https://www.msys2.org/ 에서 설치파일 다운로드 후 실행
2. UCRT64 터미널 실행 후:

```bash
pacman -Syu
pacman -S --needed --noconfirm \
  mingw-w64-ucrt-x86_64-cmake \
  mingw-w64-ucrt-x86_64-boost \
  mingw-w64-ucrt-x86_64-libxml2 \
  mingw-w64-ucrt-x86_64-gsl \
  mingw-w64-ucrt-x86_64-gcc \
  git
```

## 2. Python 설치

1. https://www.python.org/downloads/ 에서 Python 3.11 다운로드
2. **"Add Python to PATH"** 체크 후 설치

```powershell
# PowerShell에서
pip install openpyxl numpy scipy matplotlib scikit-learn requests Pillow
```

## 3. transcpp 빌드 (MSYS2 UCRT64 터미널)

```bash
mkdir -p ~/cre_reproduction && cd ~/cre_reproduction

git clone https://github.com/kennethabarr/neoParSA
cd neoParSA && mkdir -p build && cd build
cmake .. -G "MinGW Makefiles" -DCMAKE_POLICY_VERSION_MINIMUM=3.5
mingw32-make parsa -j4
cd ~/cre_reproduction

git clone https://github.com/kennethabarr/transcpp
cd transcpp
# Makefile에서 PARSA_ROOT 경로 수정 필요 (절대경로로)
mingw32-make transcpp
```

## 4. printRate 패치 적용 (필수!)

`transcpp/src/main/transcpp.cpp` 파일에서  
`fly_sa->writeResult();` 바로 다음에 추가:

```cpp
ofstream ratefile((xmlname+".rates").c_str());
embryo.printRate(ratefile, false);
ratefile.close();
```

재컴파일 후 `transcpp.exe` 생성 확인.

## 5. 데이터 파일 저장 경로

```
C:\Users\사용자명\Desktop\DATA\
├── 1-s2.0-S2589004223028249-mmc2.xlsx
├── 1-s2.0-S2589004223028249-mmc3.xlsx
└── 1-s2.0-S2589004223028249-mmc4.xlsx
```

## 6. Figure별 실행 방법

### Figure 2A-C (Windows 팀원 실행 ✅)

필요 파일 구조:
```
작업폴더/
├── model_input/
│   ├── expression/
│   │   └── single_hit_expression.csv      ← mmc4에서 변환
│   └── predictions/
│       ├── 7TF_self_single_hit_fixed_rates.tsv   ← transcpp 출력
│       └── CREB1_only_single_hit_rates.tsv        ← transcpp 출력
└── figures/
    └── (출력 폴더)
```

```powershell
# PowerShell에서
cd C:\작업폴더
python plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py
```

### Figure 2D (Windows ✅)

```powershell
# mmc3.xlsx가 같은 폴더에 있어야 함
python plot_fig2D_motif_logos.py
```

### Figure 2A-D 합치기 (Windows ✅)

```powershell
# Figure2ABC와 Figure2D 먼저 생성 후
python combine_figure2_abcd.py
```

`combine_figure2_abcd.py`에서 경로 수정 필요:
```python
# 본인 환경에 맞게 수정
DESKTOP_FIGURES = Path(r"C:\Users\사용자명\Desktop\figures")
ABC_PATH = DESKTOP_FIGURES / "Figure2ABC_7TF_self_with_CREB1_BM_v15.png"
```

### Figure 3B/C (Windows ✅)

```powershell
python build_figure3bc.py ^
    --transcpp C:\경로\transcpp.exe ^
    --mmc4 C:\경로\mmc4.xlsx ^
    --runs 4 ^
    --parallel 4
```

### Figure 4D-K (Windows ✅)

```powershell
python reproduce_figure4.py ^
    --best-xml C:\경로\best_fit.xml ^
    --mmc4 C:\경로\mmc4.xlsx ^
    --transcpp C:\경로\transcpp.exe
```

### Figure 4L/M — data-only (Windows ✅)

```powershell
python train_figure4lm.py ^
    --mode data-only ^
    --mmc4 C:\경로\mmc4.xlsx
```

### Figure 5 (Windows ✅)

```powershell
python plot_figure5.py ^
    --mmc2 C:\경로\mmc2.xlsx ^
    --mmc3 C:\경로\mmc3.xlsx ^
    --mmc4 C:\경로\mmc4.xlsx
```

## Windows에서 실행 가능 여부 요약

| Figure | Windows | 비고 |
|---|---|---|
| Figure 2A-D | ✅ 팀원 완성 | 경로 수정 필요 |
| Figure 3A | ⚠️ 가능 (느림) | 서버 권장 |
| Figure 3B/C | ✅ 팀원 완성 | |
| Figure 3D/E | ⚠️ 가능 (매우 느림) | Mac+서버 권장 |
| Figure 3E | ✅ | segfault 없음 |
| Figure 4D-K | ✅ | |
| Figure 4L/M | ✅ (data-only) | |
| Figure 5 | ✅ | |

## 주의사항

- 경로 구분자: Windows는 `\`, Python 코드에서는 `Path()` 또는 `/` 사용
- 긴 경로 문제: Windows 설정 → 긴 경로 허용 활성화 권장
- MSYS2 터미널과 PowerShell을 혼용하지 말 것
