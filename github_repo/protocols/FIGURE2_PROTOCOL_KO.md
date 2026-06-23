# Figure 2 상세 재현 프로토콜 및 인수인계 문서

- 작성 시각: **2026-06-14 KST (UTC+09:00)**
- 대상 논문: *Deep molecular learning of transcriptional control of a synthetic CRE enhancer and its variants* (Kang & Kim, iScience 2024)
- 재현 패널: **Figure 2C**
- 환경: Mac Pro M1 (로컬), Ubuntu 22.04 (서버 bds1)

---

## 1. 문서 목적

이 문서는 Figure 2C를 재현하기 위해 수행한 모든 준비, 모델 선택, fitting, 결과 분석 과정을 정리한 인수인계 문서다.

누군가 이 문서를 전달받았을 때 다음 사항을 확인할 수 있도록 작성했다.

1. Figure 2C가 무엇을 의미하는가
2. 어떤 데이터와 프로그램을 사용했는가
3. 4TF self-competition 모델이란 무엇인가
4. mmc2 파라미터를 어떻게 사용했는가
5. 최종 수치와 그림이 어떤 파일에 저장됐는가
6. 논문 재현과 다른 점 및 한계가 무엇인가

---

## 2. 논문 Figure 2C의 의미

Figure 2C는 **7개 ATF/CREB family TF를 모두 포함한 7TF 모델(self-competition 포함)** 의 fitting 결과를 보여준다.

구체적으로:

- X축: enhancer 위치 (0~86, 87bp)
- Y축: Δactivity (log2 기준)
- 상단 패널: MPRA 실험 데이터 (측정값)
- 하단 패널: 7TF self-competition 모델의 fitting 결과

4가지 치환 방향(→A, →C, →G, →T)에 대해 각각 패널이 있으며, Figure 2C는 실험 데이터와 모델 예측값의 일치를 보여주는 핵심 검증 Figure다.

---

## 3. 사용한 핵심 데이터와 프로그램

### 공식 보충자료

| 자료 | 경로 | 역할 |
|---|---|---|
| `mmc2.xlsx` | `/Users/hyunlee/Desktop/SB_final/.../1-s2.0-S2589004223028249-mmc2.xlsx` | 모델 파라미터 (4TF_self, 7TF_self 등) |
| `mmc3.xlsx` | 동일 폴더 | ATF/CREB family TF PWM |
| `mmc4.xlsx` | 동일 폴더 | single-hit 서열 및 실험 발현값 |

서버 경로:
```
~/System_Biology_AS/1-s2.0-S2589004223028249-mmc2.xlsx
~/System_Biology_AS/1-s2.0-S2589004223028249-mmc3.xlsx
~/System_Biology_AS/1-s2.0-S2589004223028249-mmc4.xlsx
```

### 실행 프로그램

```
~/cre_reproduction/transcpp/transcpp  (로컬 및 서버 모두 컴파일 완료)
```

transcpp는 열역학 모델 fitting 프로그램으로 Kenneth Barr가 개발했다.

GitHub:
- `https://github.com/kennethabarr/transcpp`
- `https://github.com/kennethabarr/neoParSA`

서버 컴파일 명령:
```bash
make XML_CFLAGS="`/usr/bin/xml2-config --cflags`" \
     XML_LIBS="`/usr/bin/xml2-config --libs`" \
     BOOST_DIR=/home/hdhyun/miniconda3/include \
     CXXFLAGS="-std=c++17 -DU_SHOW_CPLUSPLUS_API=0" transcpp
```

### printRate 기능 추가

기본 transcpp는 rates 파일을 자동으로 저장하지 않는다. 다음 코드를 `src/main/transcpp.cpp`에 추가했다:

```cpp
ofstream ratefile((xmlname+".rates").c_str());
embryo.printRate(ratefile, false);
ratefile.close();
```

이 수정이 없으면 fitting 완료 후 rates 파일이 생성되지 않는다.

---

## 4. Figure 2C에 사용된 모델

### 모델 종류

논문은 여러 모델을 비교하는데, Figure 2C는 **7 CREB family model (SelfCompetition=true)** 을 사용한다.

mmc2.xlsx에서:
- 시트: `7TF_self`
- 사용 모델: Model 1~8 중 best model

### 4TF self-competition 모델 (Model 5)

우리 재현에서는 논문의 핵심 모델인 **4TF_self Model 5** 를 주로 사용했다.

| TF | coef | kmax | lambda | threshold |
|---|---|---|---|---|
| CREB1 | 0.92 | 2.22 | 0.9 | -0.71 |
| CREM | 17.5 | 0.06 | 4.94 | 10.43 |
| ATF1 | 0.16 | 0.04 | 3.68 | 3.04 |
| ATF7 | 0.01 | 3.76 | 4.58 | 6.96 |

공통 파라미터:
- Theta: 5.06
- Rmax: 200
- SelfCompetition: true
- Seed: 5

---

## 5. CRE enhancer 구조

87bp synthetic CRE enhancer의 구조:

```
5'-GCACCAGACAGTGACGTCAGCTGCCAGATCCCATGGCCGTCATACTGTGACGTCTTTCAGACACCCCATTGACGTCAATGGGAGAAC-3'
```

주요 위치 (87bp 기준, 0-indexed):

| 위치 | 이름 |
|---|---|
| 8-19 | CRE1 (full CRE: TGACGTCA) |
| 35-44 | CRE2 (half CRE: CGTCA) |
| 44-52 | CRE3 (half CRE: CGTCA) |
| 60-68 | cryptic region |
| 67-79 | CRE4 (full CRE: TGACGTCA) |

transcpp 입력 서열은 upstream 20bp + 87bp enhancer + downstream 90bp = **197bp** 를 사용한다. 실험 발현량은 WT 대비 100을 곱해서 사용한다.

---

## 6. mmc4 데이터 구조

### single-hit 시트

- 총 261개 (87bp × 3 치환 = 261, 단 C1T 누락으로 260개)
- gene name 형식: `scanmut_single_pos_{position}_{base}`
- WT: `synCRE_Promega_0`
- 발현량 기준: WT = 100

### mmc4 시트별 구성

| 시트 | 내용 | 개수 |
|---|---|---|
| `single-hit` | 단일 치환 변이 | 261개 |
| `multi-hit` | 다중 치환 변이 | 722개 |
| `reverse_and_rearrange` | 역방향/재배열 서열 | 783개 |
| `5bp_10bp_insertion` | 삽입 변이 | 322개 |
| `8bp_complement_transition_trans` | 기타 변이 | 237개 |

---

## 7. PWM 데이터 처리

### mmc3.xlsx에서 PWM 읽기

시트명: `시트1`

읽는 방법:
```python
wb3 = openpyxl.load_workbook('mmc3.xlsx')
ws3 = wb3["시트1"]
family_pwms = {}
skip = {"Source: Cis-BP","Source: Weirauch14","Source: Jolma_367",
        "Source: Jolma_371","Source: Jolma_353","Source: Jolma_354",
        "Source: Badis09, Zhao and Stormo 11"}
current_tf = None
current_rows = {"A":[],"C":[],"G":[],"T":[]}
for row in ws3.iter_rows(values_only=True):
    if row[0] and row[0] not in skip:
        if current_tf:
            family_pwms[current_tf] = current_rows
        current_tf = row[0]
        current_rows = {"A":[],"C":[],"G":[],"T":[]}
    if row[1] in ("A","C","G","T"):
        current_rows[row[1]] = [v for v in row[2:] if v is not None]
if current_tf:
    family_pwms[current_tf] = current_rows
```

포함 TF: ATF1, ATF4, ATF7, CREB1, CREB3, CREB5, CREM

### non-family TF PWM

JASPAR에서 다운로드한 14개 non-family TF PWM은 캐시 파일로 저장돼 있다:
```
~/cre_reproduction/neoParSA/tests/transcpp/fits/non_family_pwms.pkl
```

14개 TF: DLX2, HOXA10, HOXA11, HOXA5, HOXA6, HOXA9, HOXB9, HOXD13, NKX2-2, POU3F2, SOX4, TCF3, YY1, ZIC2

---

## 8. Figure 2C 재현 방법

### 전체 흐름

```
mmc2 파라미터 (7TF_self Model) → XML 생성 → transcpp fitting
    ↓
rates 파일 생성 → Δactivity 계산 → Figure 2C 그리기
```

### XML 생성 핵심 구조

```xml
<?xml version="1.0" encoding="utf-8"?>
<Root>
  <annealer_input init_T="100000" lambda="0.0001" init_loop="100000"/>
  <Mode>
    <SelfCompetition value="true"/>
    <NumThreads value="4"/>
    <Seed value="5"/>
    <GCcontent value="0.534"/>
  </Mode>
  <Input>
    <TFs>
      <TF name="CREB1" bsize="14" include="true">
        <kmax value="2.22" anneal="false"/>
        <threshold value="-0.71" anneal="false"/>
        <lambda value="0.9" anneal="false"/>
        <Coefficients>
          <coef value="0.92" anneal="false"/>
        </Coefficients>
        <PWM type="PSSM">
          <base>A C G T</base>
          <position>...</position>
        </PWM>
      </TF>
      <!-- CREM, ATF1, ATF7 동일 구조 -->
    </TFs>
    <Genes>
      <Source name="MRPA" file="sequences/MRPA_baseM.fa" type="fasta">
        <!-- 261개 Gene 목록 -->
      </Source>
    </Genes>
    <RateData row="ID" col="gene">
      <TableRow ID="theonlyone" scanmut_single_pos_0_A="105.0" .../>
    </RateData>
    <TFData row="ID" col="TF">
      <TableRow ID="theonlyone" CREB1="100" CREM="100" ATF1="100" ATF7="100"/>
    </TFData>
  </Input>
</Root>
```

### FASTA 파일 생성

single-hit 197bp 서열 FASTA:
```
~/cre_reproduction/neoParSA/tests/transcpp/fits/sequences/MRPA_baseM.fa
```

형식:
```
>synCRE_Promega_0
CCTAACTGGCCGCTTCACTGGCACCAGACAGTGACGTCAGCTGCCAGATCCCATGGCCGT
CATACTGTGACGTCTTTCAGACACCCCATTGACGTCAATGGGAGAACGGTACCTGAGCTC
GCTAGCCTCGAGGATATCAAGATCTGGCCTCGGCGGCCAAGCTTAGACACTAGAGGGTAT
ATAATGGAAGCTCGACT
>scanmut_single_pos_0_A
...
```

---

## 9. Δactivity 계산 방법

Figure 2C에서 Δactivity는 다음과 같이 계산한다:

```python
Δactivity = log2(variant_expression / WT_expression)
```

실험 데이터:
```python
wt_expr = next(r[2] for r in rows if 'Promega_0' in r[0] and 'scanmut' not in r[0])
delta_measured = np.log2(variant_expr / wt_expr)
```

모델 예측:
```python
wt_pred = pred_vals['synCRE_Promega_0']
delta_predicted = np.log2(variant_pred / wt_pred)
```

---

## 10. 재현 결과

### Figure 2C 성능 지표

| 지표 | 우리 결과 | 논문 목표 |
|---|---|---|
| Pearson R | **0.801** | ~0.88 |
| RMSE | **0.291** | ~0.20 |

우리는 mmc2의 기존 파라미터를 anneal=false로 그대로 사용했다. 논문처럼 새로 최적화하면 더 높은 R을 얻을 수 있다.

### 최종 그래프

파일: `/mnt/user-data/outputs/figure2c_model5.png`

그래프 구성:
- 4개 패널: →A, →C, →G, →T 치환
- 각 패널: X축 = enhancer position (0~86), Y축 = Δactivity
- 파란 막대: 실험 데이터 (MPRA)
- 빨간 막대: 모델 예측값
- 하단 패널 오른쪽: 4TF 모델 R값 표시

---

## 11. Figure 2C 그리기 코드 요약

```python
import numpy as np, openpyxl, re
from scipy import stats
import matplotlib.pyplot as plt

# 1. mmc4에서 실험 데이터 로딩
wb = openpyxl.load_workbook('mmc4.xlsx')
rows = list(wb['single-hit'].iter_rows(values_only=True))[1:]
wt_expr = next(r[2] for r in rows if 'Promega_0' in r[0] and 'scanmut' not in r[0])

# 2. rates 파일에서 예측값 로딩
with open('fig2c_model5.xml.rates') as f:
    lines = f.readlines()
header = lines[0].strip().split()
data   = lines[1].strip().split()
pred_vals = {header[i+1]: float(data[i+1]) for i in range(len(header)-1)}
wt_pred = pred_vals['synCRE_Promega_0']

# 3. 치환별 Δactivity 계산
# 위치별, 치환 염기별로 분류
for base in ['A', 'C', 'G', 'T']:
    measured_by_pos = {}
    predicted_by_pos = {}
    for r in rows:
        name = r[0]
        m = re.search(r'pos_(\d+)_([ATGC])$', name)
        if m and m.group(2) == base:
            pos = int(m.group(1))
            measured_by_pos[pos]  = np.log2(r[2] / wt_expr)
            predicted_by_pos[pos] = np.log2(pred_vals.get(name, wt_pred) / wt_pred)
    # 4개 패널에 막대 그래프 그리기
    ...
```

---

## 12. 작업 폴더 구조

```
~/cre_reproduction/
├── transcpp/                    # transcpp 소스 및 실행파일
│   └── transcpp                 # 컴파일된 실행파일
├── neoParSA/
│   └── tests/transcpp/fits/
│       ├── sequences/
│       │   └── MRPA_baseM.fa    # single-hit 197bp FASTA
│       ├── fig2c_xmls/          # Figure 2C용 XML (선택적)
│       ├── non_family_pwms.pkl  # JASPAR PWM 캐시
│       └── *.xml.rates          # transcpp 출력 rates 파일
~/System_Biology_AS/
├── mmc2.xlsx
├── mmc3.xlsx
└── mmc4.xlsx
```

---

## 13. XML anneal 설정의 의미

Figure 2C 재현에서 두 가지 방식을 사용할 수 있다.

### 방식 1: anneal=false (mmc2 파라미터 그대로 사용)

```xml
<kmax value="2.22" anneal="false"/>
```

- mmc2에서 가져온 파라미터를 변경하지 않고 예측만 수행
- 빠름 (수초~수분)
- 우리 재현에서 R=0.801 달성

### 방식 2: anneal=true (새로 최적화)

```xml
<kmax value="2.22" lim_low="1e-06" lim_high="4.0" anneal="true"/>
```

- 파라미터를 simulated annealing으로 재최적화
- 오래 걸림 (수십분~수시간)
- 더 높은 R 기대

Figure 2C 논문 재현에는 anneal=false로도 충분히 트렌드를 보여줄 수 있다.

---

## 14. 논문과 다른 점 및 재현 한계

### 1. 모델 종류

논문 Figure 2C는 7TF self-competition 모델을 사용한다. 우리는 4TF self-competition 모델(CREB1, CREM, ATF1, ATF7)을 주로 사용했다.

### 2. Pearson R 차이

- 논문: R~0.88 (7TF), R~0.93 (최고 모델)
- 우리: R=0.801 (4TF, anneal=false)

차이 원인:
- TF 수 차이 (4TF vs 7TF)
- 최적화 여부 (anneal=false vs 재최적화)
- 논문의 정확한 seed/초기값 미공개

### 3. PWM 선택

논문은 고성능 HT-SELEX 및 PBM 기반 PWM만 사용했다. 우리는 논문 방식과 동일하게 mmc3에서 직접 읽어 사용했다.

### 4. C1T 누락

mmc4 single-hit 시트에 C1T 치환이 없다. 공식 자료의 261개 중 260개만 사용했다 (C1T 누락).

---

## 15. 보고서에 사용할 수 있는 방법 설명

한국어:

> 공개된 mmc2의 4TF self-competition 모델 파라미터(CREB1, CREM, ATF1, ATF7)를 사용하여 열역학 모델 프로그램 transcpp로 single-hit MPRA 데이터에 대한 발현량을 예측하였다. 예측 발현량과 실험 발현량 모두 WT 대비 log2 비율(Δactivity)로 변환한 후 Pearson 상관계수를 계산하였다. 87개 enhancer 위치에서의 4가지 치환(→A, →C, →G, →T)에 대한 실험 결과와 모델 예측값을 위치별 막대 그래프로 시각화하였다 (Pearson R = 0.80).

영어:

> We used the published 4TF self-competition model parameters (CREB1, CREM, ATF1, ATF7) from Table S1 (mmc2) to predict expression rates for the single-hit MPRA dataset using the transcpp thermodynamic model program. Both predicted and experimental expression values were converted to log2 ratios relative to WT (Δactivity). Pearson correlation was calculated between experimental and predicted Δactivities. Positional bar plots were generated for all four substitution types (→A, →C, →G, →T) across the 87 bp enhancer (Pearson R = 0.80).

---

## 16. 현재 상태 요약

2026-06-14 현재 Figure 2C 재현 완료.

```
모델: 4TF self-competition (CREB1, CREM, ATF1, ATF7)
파라미터: mmc2 Model 5 (anneal=false)
결과: Pearson R = 0.801, RMSE = 0.291
논문 목표: R ~0.88 (7TF), R ~0.93 (최고)
상태: 부분 재현 완료 (트렌드 일치)
```

최종 그림은 다음 경로에 저장:
```
/mnt/user-data/outputs/figure2c_model5.png
```

---

## 부록: transcpp XML 전체 예시

4TF Model 5 기준 XML 최소 구조:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Root>
  <annealer_input init_T="100000" lambda="0.0001" init_loop="100000"/>
  <move interval="100" gain="3"/>
  <count_criterion freeze_crit="10" freeze_cnt="5"/>
  <mix adaptcoef="10"/>
  <lam tau="100" memLength_mean=".200" memLength_sd="100" criterion="10" freeze_cnt="5"/>
  <Mode>
    <Verbose value="1"/>
    <ScoreFunction value="sse"/>
    <GCcontent value="0.534"/>
    <NumThreads value="4"/>
    <SelfCompetition value="true"/>
    <Precision value="8"/>
    <Seed value="5"/>
  </Mode>
  <Input>
    <Distances>
      <Distance name="Quenching" distfunc="Trapezoid">
        <A value="100" lim_low="50" lim_high="100" anneal="false" move="Quenching"/>
        <B value="50" lim_low="50" lim_high="50" anneal="false" move="Quenching"/>
      </Distance>
    </Distances>
    <Promoters>
      <Promoter name="basic" function="Arrhenius2">
        <Q value="1" lim_low="1" lim_high="1" anneal="false" move="Promoter"/>
        <Rmax value="200" lim_low="200" lim_high="200" anneal="false" move="Promoter"/>
        <Theta value="5.06" lim_low="5" lim_high="20" anneal="false" move="Promoter"/>
      </Promoter>
    </Promoters>
    <TFs>
      <TF name="CREB1" bsize="14" include="true">
        <kmax value="2.22" lim_low="1e-06" lim_high="4.0" anneal="false" move="Kmax"/>
        <threshold value="-0.71" lim_low="-5" lim_high="15.0" anneal="false" move="Sites"/>
        <lambda value="0.9" lim_low="0.5" lim_high="5.0" anneal="false" move="Lambda"/>
        <Coefficients>
          <coef value="0.92" lim_low="0.0001" lim_high="20.0" anneal="false" move="Promoter"/>
        </Coefficients>
        <PWM type="PSSM">
          <base>A C G T</base>
          <!-- mmc3에서 읽은 PWM position 값들 -->
        </PWM>
      </TF>
      <!-- CREM, ATF1, ATF7 동일 구조 -->
    </TFs>
    <Interactions/>
    <Genes>
      <Source name="MRPA" file="sequences/MRPA_baseM.fa" type="fasta">
        <!-- 261개 Gene 요소 -->
        <Gene name="synCRE_Promega_0" header="synCRE_Promega_0"
              left_bound="-235" right_bound="-38" TSS="-1" promoter="basic"/>
        <Gene name="scanmut_single_pos_0_A" .../>
        <!-- ... -->
      </Source>
    </Genes>
    <ScaleFactors>
      <ScaleFactor name="default">
        <A value="1" lim_low="1" lim_high="1" anneal="false"/>
        <B value="0" lim_low="0" lim_high="0" anneal="false"/>
      </ScaleFactor>
    </ScaleFactors>
    <RateData row="ID" col="gene">
      <TableRow ID="theonlyone"
                synCRE_Promega_0="100.0"
                scanmut_single_pos_0_A="105.0"
                <!-- ... 전체 261개 -->/>
    </RateData>
    <TFData row="ID" col="TF">
      <TableRow ID="theonlyone" CREB1="100" CREM="100" ATF1="100" ATF7="100"/>
    </TFData>
  </Input>
</Root>
```
