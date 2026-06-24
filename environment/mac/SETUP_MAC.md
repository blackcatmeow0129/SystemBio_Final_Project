# Mac M1 환경 설정 가이드

> 실제 구현에 사용된 환경: **Mac Pro M1 (8코어)**

---

## 1. 사전 요구사항

```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 의존성 설치
brew install libxml2 boost cmake git python3
```

## 2. Python 패키지 설치

```bash
pip3 install openpyxl numpy scipy matplotlib scikit-learn requests Pillow
```

## 3. transcpp 빌드

```bash
mkdir -p ~/cre_reproduction && cd ~/cre_reproduction

# neoParSA 빌드
git clone https://github.com/kennethabarr/neoParSA
cd neoParSA && mkdir -p build && cd build
cmake .. -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make parsa -j4
cd ~/cre_reproduction

# transcpp 빌드
git clone https://github.com/kennethabarr/transcpp
cd transcpp
sed -i '' "s|PARSA_ROOT ?=.*|PARSA_ROOT ?=$HOME/cre_reproduction/neoParSA|g" Makefile
make XML_CFLAGS="$(xml2-config --cflags)" \
     XML_LIBS="$(xml2-config --libs)" \
     BOOST_DIR=$(brew --prefix boost)/include \
     CXXFLAGS="-std=c++17" transcpp

# 테스트
~/cre_reproduction/transcpp/transcpp 2>&1 | head -3
```

## 4. printRate 패치 적용 (필수!)

```bash
cd ~/cre_reproduction/transcpp

# transcpp.cpp 열기
open src/main/transcpp.cpp
```

`fly_sa->writeResult();` 바로 다음 줄에 추가:
```cpp
ofstream ratefile((xmlname+".rates").c_str());
embryo.printRate(ratefile, false);
ratefile.close();
```

재컴파일:
```bash
make XML_CFLAGS="$(xml2-config --cflags)" \
     XML_LIBS="$(xml2-config --libs)" \
     BOOST_DIR=$(brew --prefix boost)/include \
     CXXFLAGS="-std=c++17" transcpp
```

## 5. 작업 폴더 생성

```bash
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/sequences
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3a_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3b_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_mh_xmls
```

## 6. 데이터 파일 저장 경로

```
~/Desktop/SB_final/ScienceDirect_files_26May2026_04-41-20.049/
├── 1-s2.0-S2589004223028249-mmc2.xlsx
├── 1-s2.0-S2589004223028249-mmc3.xlsx
└── 1-s2.0-S2589004223028249-mmc4.xlsx
```

## 7. Figure별 실행 방법

### Figure 2C (Mac에서 실행 가능 ✅)
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 /path/to/figures/Figure2/Figure2ABC/generate_figure2c_4TF.py
```

### Figure 2A-D (Windows 팀원 환경에서 생성, Mac에서도 가능)
```bash
# 필요 파일 구조 생성
mkdir -p model_input/expression model_input/predictions figures

# 실행
python3 figures/Figure2/Figure2ABC/plot_fig2ABC_7TF_self_with_CREB1_BM_v15.py
python3 figures/Figure2/Figure2D/plot_fig2D_motif_logos.py
python3 figures/Figure2/Figure2ABCD/combine_figure2_abcd.py
```

### Figure 3A (서버 권장, Mac에서도 가능 - 느림)
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 /path/to/figures/Figure3/Figure3A/plot_figure3a.py
```

### Figure 3D/E — Mac 담당: n1~n4 ✅
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 /path/to/figures/Figure3/Figure3DE/generate_figure3de_xmls.py
bash /path/to/figures/Figure3/Figure3DE/run_figure3de_local.sh
```

> ⚠️ **Figure 3E (multi-hit 예측)은 Mac에서 segfault 발생 → 서버에서 실행**

### Figure 4D-K (Mac에서 실행 가능 ✅)
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 /path/to/figures/Figure4/Figure4AK/reproduce_figure4.py \
    --best-xml fig3de_xmls/fig3de_n4_m5_CREB1_CREB3_CREM_ATF1.xml \
    --mmc4 ~/Desktop/SB_final/.../mmc4.xlsx \
    --transcpp ~/cre_reproduction/transcpp/transcpp
```

### Figure 4L/M (data-only 모드 - Mac ✅)
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
python3 /path/to/figures/Figure4/Figure4LM/train_figure4lm.py \
    --mode data-only \
    --mmc4 ~/Desktop/SB_final/.../mmc4.xlsx
```

### Figure 5 (Mac에서 실행 가능 ✅)
```bash
python3 /path/to/figures/Figure5/plot_figure5.py \
    --mmc2 ~/Desktop/SB_final/.../mmc2.xlsx \
    --mmc3 ~/Desktop/SB_final/.../mmc3.xlsx \
    --mmc4 ~/Desktop/SB_final/.../mmc4.xlsx
```

## Mac에서 실행 가능 여부 요약

| Figure | Mac M1 | 비고 |
|---|---|---|
| Figure 2A-D | ✅ | Windows 스크립트 경로 수정 필요 |
| Figure 3A | ✅ (느림) | 서버 권장 |
| Figure 3B/C | ✅ | 팀원 스크립트 |
| Figure 3D (n1-4) | ✅ | Mac 담당 |
| Figure 3D (n5-7) | ⚠️ 매우 느림 | 서버 권장 |
| Figure 3E | ❌ segfault | 서버 필수 |
| Figure 4D-K | ✅ | |
| Figure 4L/M | ✅ (data-only) | |
| Figure 5 | ✅ | |
