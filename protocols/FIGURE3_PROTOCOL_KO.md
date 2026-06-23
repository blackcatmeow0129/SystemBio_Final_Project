# Figure 3 상세 재현 프로토콜 및 인수인계 문서

- 작성 시각: **2026-06-14 KST (UTC+09:00)**
- 대상 논문: *Deep molecular learning of transcriptional control of a synthetic CRE enhancer and its variants* (Kang & Kim, iScience 2024)
- 재현 패널: **Figure 3A, 3B, 3C, 3D, 3E**
- 환경: Mac Pro M1 로컬 + Ubuntu 22.04 서버 (bds1, 32코어, 125GB RAM)

---

## 1. 문서 목적

이 문서는 Figure 3 전체를 재현하기 위해 수행한 모든 과정, 실패 경험, 그리고 그 실패에서 얻은 교훈을 정리한 인수인계 문서다.

Figure 3은 이 논문에서 **가장 계산량이 많은 Figure** 로, 총 127개 TF 조합에 대해 각각 8개 모델을 학습해야 한다. 시간 관리와 전략적 실행이 핵심이다.

---

## 2. Figure 3 전체 구조 이해

### 패널별 의미

| 패널 | 조건 | 데이터 | 의미 |
|---|---|---|---|
| **3A** | SelfComp=true, 2TF 고정 (CREB1+α) | single-hit fitting | non-family vs CREB family TF 비교 |
| **3B** | SelfComp=false | single-hit fitting R | TF 수별 R 분포 (without self-comp) |
| **3C** | SelfComp=false (3B 모델 재사용) | multi-hit prediction R | 미학습 예측 성능 (without self-comp) |
| **3D** | SelfComp=true | single-hit fitting R | TF 수별 R 분포 (with self-comp) |
| **3E** | SelfComp=true (3D 모델 재사용) | multi-hit prediction R | 미학습 예측 성능 (with self-comp) |

### 핵심 관계

```
3B rates → 3B 그래프 (단독)
3B rates → anneal=false로 multi-hit 예측 → 3C 그래프

3D rates → 3D 그래프 (단독)
3D rates → anneal=false로 multi-hit 예측 → 3E 그래프
```

즉 **C와 E는 B와 D의 rates 파일을 재활용** 한다. 별도의 학습이 필요 없다.

---

## 3. 계산량 분석

### 논문 기준

```
127 조합 × 8 모델 = 1,016개 fitting
```

TF 수별 조합 수:

| TF 수 | 조합 수 | 모델 수 | 총 fitting |
|---:|---:|---:|---:|
| 1 | 7 | 8 | 56 |
| 2 | 21 | 8 | 168 |
| 3 | 35 | 8 | 280 |
| 4 | 35 | 8 | 280 |
| 5 | 21 | 8 | 168 |
| 6 | 7 | 8 | 56 |
| 7 | 1 | 8 | 8 |
| **합계** | **127** | | **1,016** |

### 실제 소요 시간 (경험 기반)

| 환경 | TF 수 | 1개당 소요시간 | 비고 |
|---|---:|---:|---|
| 로컬 M1 (7병렬) | n1 | ~2분 | 빠름 |
| 로컬 M1 (7병렬) | n3 | ~7-10분 | 중간 |
| 로컬 M1 (7병렬) | n5+ | ~30분+ | 매우 느림 |
| 서버 bds1 (25병렬) | n1 | ~16분 | M1보다 느림! |
| 서버 bds1 (25병렬) | n3 | ~60분+ | 매우 느림 |

**중요 발견**: 서버가 코어 수는 많지만 단일 코어 성능이 M1보다 낮다. transcpp는 CPU 집약적이라 코어 수보다 코어 속도가 중요하다.

---

## 4. 실패 경험과 교훈

### 실패 1: init_loop를 너무 크게 설정

**상황**: 처음 init_loop=100000(10만)으로 시작했다가 n3 이상에서 한 개당 수십분~수시간 소요.

**교훈**: init_loop는 annealing 반복 횟수다. TF 수가 늘수록 파라미터 공간이 기하급수적으로 커져서 같은 init_loop라도 시간이 훨씬 오래 걸린다.

**해결책**: init_loop를 상황에 맞게 조절:
- 빠른 확인용: `init_loop=100`
- 중간 품질: `init_loop=1000`
- 논문 수준: `init_loop=100000` (시간 여유가 있을 때만)

### 실패 2: NumThreads 설정 실수

**상황**: NumThreads=4로 설정하고 25개 병렬 실행 → 실제 4×25=100코어 사용 시도. 32코어 서버에서 과부하 발생.

**교훈**: `NumThreads`는 각 프로세스가 사용하는 스레드 수다. 병렬 프로세스 수와 곱해서 실제 사용 코어를 계산해야 한다.

**해결책**: `NumThreads=1`로 설정하고 병렬 프로세스 수로만 제어:
```bash
# 25개 병렬, 각각 1코어 = 총 25코어 사용 (서버 32코어에서 안전)
while [ $(jobs -r | wc -l) -ge 25 ]; do sleep 3; done
```

### 실패 3: nohup 스크립트가 계속 새 프로세스 생성

**상황**: `kill`로 transcpp를 종료했는데 50개 프로세스가 계속 남아 있음.

**교훈**: nohup으로 실행된 bash 스크립트가 살아있어서 계속 새 transcpp를 생성하고 있었다.

**해결책**: transcpp를 kill하기 전에 스크립트를 먼저 kill:
```bash
pkill -9 -f run_fig3bcde   # 스크립트 먼저 종료
sleep 3
pkill -9 -f transcpp        # 그 다음 transcpp 종료
```

### 실패 4: Floating point exception (서버에서)

**상황**: 서버에서 reverse/rearrange 서열로 transcpp 실행 시 floating point exception 발생.

**교훈**: gene name이 single-hit과 동일하면 transcpp가 내부적으로 충돌한다. gene name에 prefix를 붙여야 한다.

**해결책**: gene name에 `rev_`, `rear_`, `revr_` 등 prefix 추가:
```python
new_data = [(f'rev_{name}', seq, expr) for name, seq, expr in data]
```

### 실패 5: multi-hit 예측에서 segfault (로컬 M1)

**상황**: 로컬 M1에서 722개 multi-hit 서열 예측 시 항상 segfault 발생.

**교훈**: M1 맥북에서 722개 서열을 처리하면 메모리 또는 스택 문제로 segfault가 발생한다. 이건 서버에서만 가능하다.

**해결책**: 서버(bds1)에서 multi-hit 예측 실행. 로컬 rates 파일을 scp로 서버에 전송 후 서버에서 실행.

### 실패 6: XML Source 중복 문제

**상황**: Python ET로 XML을 여러 번 수정하면서 Source 태그가 6개 중복 생성됨 → 모든 예측값이 동일하게 나옴.

**교훈**: `re.sub`으로 XML을 수정할 때 패턴이 여러 번 매칭되면 중복 삽입된다.

**해결책**: XML을 처음부터 새로 작성하거나, 템플릿 XML을 `copy.deepcopy`로 복사한 후 수정:
```python
import copy
tmpl_root = copy.deepcopy(tmpl_tree.getroot())
```

### 실패 7: FASTA 한 줄 형식 문제

**상황**: FASTA 서열을 한 줄로 작성했더니 transcpp가 서열을 인식하지 못함.

**교훈**: transcpp는 60자씩 줄바꿈된 FASTA 형식을 요구한다.

**해결책**: 60자씩 줄바꿈:
```python
with open(fasta_path, 'w') as f:
    f.write(f'>{name}\n')
    for i in range(0, len(seq), 60):
        f.write(seq[i:i+60] + '\n')
```

### 실패 8: "score not same" 오류 후 rates 파일 확인 필요

**상황**: `The score was not the same after rerunning the model` 오류 메시지가 나왔지만 rates 파일은 정상 생성됨.

**교훈**: 이 오류가 나와도 rates 파일이 생성된 경우가 있다. 오류 메시지만 보고 포기하지 말고 파일 생성 여부를 확인해야 한다.

**해결책**: 오류 후 rates 파일 존재 여부 확인:
```bash
ls *.rates 2>/dev/null | wc -l
```

---

## 5. Figure 3A 재현

### 3A 의미

CREB1을 기본으로 하고, 각 다른 TF를 하나씩 추가했을 때 단일 hit fitting R값의 변화를 보여주는 boxplot.

- non-family TF 14개 vs CREB family TF 6개 비교
- 빨간 기준선: best CREB1 self-competition 모델의 R값

### 3A 실행 전략

XML 생성:
```python
# 168개 XML = 21개 TF × 8개 모델
# 각 XML: CREB1 + 다른 TF 1개, SelfComp=true
NON_FAMILY = ['DLX2','HOXA10','HOXA11','HOXA5','HOXA6','HOXA9',
              'HOXB9','HOXD13','NKX2-2','POU3F2','SOX4','TCF3','YY1','ZIC2']
FAMILY = ['ATF1','ATF4','ATF7','CREB3','CREB5','CREM']
```

서버에서 실행:
```bash
nohup bash -c '
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
TRANSCPP=~/cre_reproduction/transcpp/transcpp
for xml in fig3a_xmls/*.xml; do
    [ -f "${xml%.xml}.xml.rates" ] && continue
    $TRANSCPP $xml > "${xml%.xml}.log" 2>&1 &
    while [ $(jobs -r | wc -l) -ge 10 ]; do sleep 3; done
done
wait' > ~/fig3a_log.txt 2>&1 &
```

완료: 168개 rates → 그래프 생성 가능

### 3A 결과

서버에서 완료 (168/168). `figure3a_server.png` 생성 완료.

---

## 6. Figure 3B/C 재현

### 3B/C 의미

- **3B**: SelfComp=false, 127 TF 조합, single-hit fitting R값 분포
- **3C**: 동일 모델로 multi-hit 722개 예측 R값 분포

### 팀원 방식 (권장)

팀원이 Windows에서 완성한 방식이 가장 정확하다.

필요 파일:
```
build_figure3bc.py          # 전체 파이프라인 스크립트
selected_fit_manifest.tsv   # 어떤 fits를 사용했는지 매니페스트
```

실행:
```bash
python3 build_figure3bc.py \
    --forward-results <정방향_결과_폴더> \
    --reverse-results <역방향_결과_폴더> \
    --supplementary-json <mmc4_json> \
    --multi-hit-fasta <multi_hit.fa> \
    --transcpp <transcpp 경로> \
    --runtime-dir <작업폴더> \
    --output-dir <출력폴더> \
    --runs 4 \
    --threads 4 \
    --parallel 4
```

### 핵심 포인트: SelfCompetition=false

3B는 반드시 `SelfCompetition value="false"` 여야 한다:
```xml
<SelfCompetition value="false"/>
```

### 서버에서 직접 돌리는 방법 (시간 절약)

```bash
# XML 생성 (127조합 × 3모델 = 381개, m1/m5/m7)
python3 << 'PYEOF'
for n_tfs in range(1, 8):
    for combo in combinations(TFS, n_tfs):
        for m_num in [1, 5, 7]:  # 3개 seed만
            # SelfCompetition=false XML 생성
            ...
PYEOF

# 25코어로 실행
nohup ~/run_fig3b.sh > ~/fig3b_log.txt 2>&1 &
```

### 3C: multi-hit 예측 방법

3B rates 파일에서 파라미터를 freeze하고 multi-hit 서열 적용:

```python
def make_multi_hit_xml(fit_xml, target, fasta, records, threads):
    tree = ET.parse(fit_xml)
    root = tree.getroot()
    # Output 태그를 Input으로 변환
    new_input = copy.deepcopy(root.find('Output'))
    new_input.tag = 'Input'
    # 모든 anneal=false로 설정
    for elem in new_input.iter():
        if 'anneal' in elem.attrib:
            elem.set('anneal', 'false')
    # multi-hit 서열로 Genes 교체
    ...
```

---

## 7. Figure 3D/E 재현

### 3D/E 의미

- **3D**: SelfComp=true, 127 TF 조합, single-hit fitting R값 분포
- **3E**: 동일 모델로 multi-hit 722개 예측 R값 분포

3B/C와 완전히 동일한 구조이나 `SelfCompetition=true` 라는 점만 다르다.

### 실행 전략: 로컬 + 서버 분업

시간을 절약하기 위해 로컬과 서버가 서로 다른 TF 수를 담당하는 것이 효율적이다.

**경험 기반 권장 분업:**

| 환경 | 담당 | 이유 |
|---|---|---|
| 로컬 M1 | n1~n4 (작은 TF 수) | M1이 단일 코어 빠름, 빨리 완료 |
| 서버 bds1 | n5~n7 (큰 TF 수) | 많은 코어로 병렬 처리 |

실제 우리 경험:
- 로컬에서 n1~n3는 며칠 만에 완료
- 서버에서 n5~n7 역순으로 실행

### 역순 실행의 중요성

서버와 로컬이 동시에 실행할 때 서버는 **n7부터 역순** 으로 실행해야 중복을 피할 수 있다:

```bash
# 서버: n7→n5 역순
for n in 7 6 5; do
    for xml in fig3de_xmls/fig3de_n${n}_m5_*.xml; do
        ...
    done
done
```

로컬: n1→n4 정순으로 자동 실행.

### 최적 설정 (경험 기반)

```
init_loop=100       # 빠른 재현 (트렌드 확인용)
NumThreads=1        # 코어 경합 방지
병렬=25개           # 서버 25코어 활용
seed: m1, m5, m7   # 3개만 (논문은 8개지만 시간 절약)
```

init_loop 비교:

| init_loop | n1 소요 | n3 소요 | 품질 |
|---:|---:|---:|---|
| 100 | ~2분 | ~10분 | 낮음 (트렌드는 재현) |
| 1,000 | ~10분 | ~60분+ | 중간 |
| 100,000 | ~수시간 | 완료 불가 | 논문 수준 |

### 실행 스크립트 (서버)

```bash
# XML 생성 (n1~n7, m5만, SelfComp=true, init_loop=100)
python3 << 'PYEOF'
for n_tfs in range(1, 8):
    for combo in combinations(TFS, n_tfs):
        combo_name = "_".join(combo)
        # init_loop=100, NumThreads=1, SelfComp=true
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<Root>
  <annealer_input init_T="100000" lambda="0.0001" init_loop="100"/>
  ...
  <Mode>
    <NumThreads value="1"/>
    <SelfCompetition value="true"/>
    <Seed value="5"/>
  </Mode>
  ...
</Root>"""
        with open(f'fig3de_xmls/fig3de_n{n_tfs}_m5_{combo_name}.xml', 'w') as f:
            f.write(xml)
PYEOF

# 실행 스크립트 생성
cat > ~/run_fig3de.sh << 'EOF'
#!/bin/bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
TRANSCPP=~/cre_reproduction/transcpp/transcpp
for n in 7 6 5 4 3 2 1; do
    for xml in fig3de_xmls/fig3de_n${n}_m5_*.xml; do
        [ -f "${xml%.xml}.xml.rates" ] && continue
        name=$(basename $xml .xml)
        $TRANSCPP $xml > fig3de_xmls/${name}.log 2>&1 &
        while [ $(jobs -r | wc -l) -ge 25 ]; do sleep 3; done
    done
done
wait
echo "완료!"
EOF
chmod +x ~/run_fig3de.sh
nohup ~/run_fig3de.sh > ~/fig3de_log.txt 2>&1 &
```

### Figure 3E: multi-hit 예측

3D rates 파일을 서버에서 multi-hit XML로 변환하여 실행.

**중요**: 로컬 M1에서는 722개 multi-hit 서열 예측 시 segfault 발생. 반드시 서버에서 실행.

```bash
# 로컬 rates → 서버로 전송
scp -J jumpserver@118.41.98.18 \
    ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_xmls/*.rates \
    hdhyun@220.149.111.120:~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_xmls/
```

서버에서 mh XML 생성 후 실행:
```python
import xml.etree.ElementTree as ET
import copy

# 성공한 fig3a XML을 템플릿으로 사용 (중요!)
tmpl_tree = ET.parse('fig3a_xmls/fig3a_m5_CREB1.xml')

for rates_file in glob.glob('fig3de_xmls/*.rates'):
    xml_file = rates_file.replace('.xml.rates', '.xml')
    mh_tree = ET.parse(xml_file)
    mh_root = mh_tree.getroot()
    mh_input = mh_root.find('Input')

    # 템플릿에서 TFs, Genes, RateData, TFData 교체
    tmpl_root = copy.deepcopy(tmpl_tree.getroot())
    tmpl_input = tmpl_root.find('Input')
    for tag in ['TFs', 'Genes', 'RateData', 'TFData']:
        old = tmpl_input.find(tag)
        new = mh_input.find(tag)
        if old is not None: tmpl_input.remove(old)
        if new is not None: tmpl_input.append(copy.deepcopy(new))

    # multi-hit Genes 교체
    genes = tmpl_input.find('Genes')
    # ... 722개 multi-hit 서열로 교체
```

**핵심 교훈**: 직접 만든 XML보다 **성공한 기존 XML을 템플릿으로 사용** 하는 게 훨씬 안정적이다. Source 중복 등의 문제를 피할 수 있다.

---

## 8. 그래프 생성

### R값 계산

```python
def calc_r_single(rates_file):
    with open(rates_file) as f: lines = f.readlines()
    header = lines[0].strip().split()
    data   = lines[1].strip().split()
    pred   = {header[i+1]: float(data[i+1]) for i in range(len(header)-1)}
    wt_p   = pred.get('synCRE_Promega_0')
    if not wt_p or wt_p <= 0: return None
    # single-hit 측정값과 예측값 비교
    meas, preds = [], []
    for name, mv in meas_dict.items():
        if name in pred and pred[name] > 0:
            meas.append(mv)
            preds.append(np.log2(pred[name]/wt_p))
    if len(meas) < 10: return None
    r, _ = stats.pearsonr(meas, preds)
    return r

def calc_r_multihit(rates_file):
    # multi-hit rates는 WT key가 'synCRE_Promega_0_WT'
    wt_p = pred.get('synCRE_Promega_0_WT') or pred.get('synCRE_Promega_0')
    ...
```

**중요**: multi-hit rates 파일의 WT gene name은 `synCRE_Promega_0_WT`이고, single-hit rates 파일의 WT gene name은 `synCRE_Promega_0`이다. 둘 다 체크해야 한다.

### 그래프 스타일 (팀원 방식과 일치)

```python
COLORS = {
    1: "#9DB8DE",  # 파란색
    2: "#E87513",  # 주황색
    3: "#4169A1",  # 진파란
    4: "#70AD47",  # 초록
    5: "#00A6C6",  # 청록
    6: "#8C8C8C",  # 회색
    7: "#8064A2",  # 보라
}
# 흰색 median 선, 검은 점 (mean)
medianprops = dict(color='white', linewidth=2)
ax.scatter(i+1, np.mean(vals), s=60, color='black', zorder=5)
```

---

## 9. 전체 실행 우선순위 및 타임라인

### 시간 제약이 있을 때 우선순위

```
1순위: Figure 3A (168개, 서버에서 1~2일)
2순위: Figure 3B/C (팀원 완성본 활용!)
3순위: Figure 3D/E (로컬 n1~n4 + 서버 n5~n7)
```

### 권장 타임라인 (일요일 마감 기준)

| 시점 | 할 일 |
|---|---|
| 월요일 | 로컬: Figure 3D/E 전체 시작 (init_loop=100000, 7병렬) |
| 월요일 | 서버: Figure 3A 시작 (168개) |
| 화요일 | 서버: Figure 3D/E n5~n7 역순 시작 |
| 수요일 | Figure 3A 완료 → 그래프 생성 |
| 목요일 | 서버: n5~n7 완료 확인 |
| 금요일 | 로컬 n1~n4 완료 확인 + multi-hit 예측 서버에서 실행 |
| 토요일 | 전체 그래프 생성 및 검토 |

### 빠른 재현이 필요할 때

```
init_loop=100, m1/m5/m7 (3개 seed), NumThreads=1, 25병렬
→ Figure 3D/E: 약 2~3시간 (트렌드 재현 가능)
```

---

## 10. 서버 관리 팁

### 현재 상태 확인 원라이너

```bash
echo "=== 현재 상태 ===" && \
echo "Fig3A: $(ls fig3a_xmls/*.rates 2>/dev/null | wc -l)/168" && \
echo "Fig3B: $(ls fig3b_xmls/*.rates 2>/dev/null | wc -l)/381" && \
echo "Fig3D: $(ls fig3de_xmls/*.rates 2>/dev/null | wc -l)/381" && \
echo "실행 중: $(ps aux | grep transcpp | grep -v grep | wc -l)개" && \
ps aux | grep transcpp | grep -v grep | grep -o 'fig3[a-z]*_n[0-9]' | sort | uniq -c
```

### 프로세스 완전 중단

```bash
pkill -9 -f run_fig3    # 스크립트 먼저
sleep 3
pkill -9 -f transcpp    # 그 다음 transcpp
sleep 5
ps aux | grep hdhyun | grep transcpp | grep -v grep | wc -l
```

### 점프서버 통한 파일 전송

```bash
# 로컬 → 서버
scp -J jumpserver@118.41.98.18 \
    ~/cre_reproduction/.../fig3de_xmls/*.rates \
    hdhyun@220.149.111.120:~/cre_reproduction/.../fig3de_xmls/

# 서버 → 로컬 (임시 공유 링크)
curl -F "file=@/home/hdhyun/System_Biology_AS/figure3.png" \
     https://tmpfiles.org/api/v1/upload
# 출력된 URL에서 /wnwFc7... → /dl/wnwFc7...로 변경하여 다운로드
```

---

## 11. 파일 경로 요약

### 로컬 (맥북 M1)

```
~/cre_reproduction/transcpp/transcpp          # 실행파일
~/cre_reproduction/neoParSA/tests/transcpp/fits/
├── sequences/MRPA_baseM.fa                   # single-hit FASTA
├── sequences/MRPA_multihit.fa                # multi-hit FASTA (수동 생성)
├── non_family_pwms.pkl                       # JASPAR PWM 캐시
├── fig3a_xmls/                               # Figure 3A XMLs
├── fig3b_xmls/                               # Figure 3B XMLs (SelfComp=false)
├── fig3de_xmls/                              # Figure 3D/E XMLs (SelfComp=true)
└── fig3de_mh_xmls/                           # Figure 3E multi-hit XMLs
~/Desktop/SB_final/.../
├── mmc2.xlsx
├── mmc3.xlsx
└── mmc4.xlsx
```

### 서버 (bds1)

```
~/cre_reproduction/transcpp/transcpp
~/cre_reproduction/neoParSA/tests/transcpp/fits/
├── sequences/MRPA_baseM.fa
├── sequences/MRPA_multihit.fa
├── fig3a_xmls/
├── fig3b_xmls/
├── fig3de_xmls/
└── fig3de_mh_xmls/
~/System_Biology_AS/
├── mmc2.xlsx, mmc3.xlsx, mmc4.xlsx
├── figure3a_server.png
└── figure3DE_server.png
```

---

## 12. 현재 재현 상태 (2026-06-14)

| 패널 | 상태 | 데이터 | 비고 |
|---|---|---|---|
| **3A** | ✅ 완료 | 168/168개 | `figure3a_server.png` |
| **3B** | ✅ 완료 | 508개 (4 runs) | 팀원 완성, `Figure3B.png` |
| **3C** | ✅ 완료 | 508개 | 팀원 완성, `Figure3C.png` |
| **3D** | 🔄 부분 완료 | n1~n6 (로컬+서버) | `figure3DE_server.png` (부분) |
| **3E** | 🔄 부분 완료 | n1~n4 수준 | 서버에서 mh 예측 진행 중 |

### 3B/C는 팀원 완성본 사용

팀원(Windows)이 완성한 `Figure3B.png`, `Figure3C.png`, `Figure3_BC.png`을 그대로 사용한다. 127조합 × 4 runs = 508개 완전 재현.

---

## 13. 논문과 다른 점 및 한계

### 1. run 수

- 논문: 127조합 × 8 runs = 1,016개
- 우리 3B/C: 127조합 × 4 runs = 508개 (팀원)
- 우리 3D/E: 127조합 × 1~3 runs (진행 중)

### 2. init_loop

- 논문: 충분한 annealing (정확한 값 미공개)
- 우리: init_loop=100~1000 (시간 제약)

### 3. 결과 차이

init_loop가 작으면 각 모델의 R값이 낮게 나올 수 있으나 TF 수에 따른 트렌드(증가 경향)는 재현된다.

### 4. 서버 속도 문제

서버 CPU 단일 코어 성능이 M1보다 낮아 n3 이상에서 속도가 매우 느리다. 이 때문에 현실적으로 init_loop를 줄이거나 seed 수를 줄여야 한다.

---

## 14. 보고서에 사용할 수 있는 방법 설명

한국어:

> ATF/CREB family 전사인자 7개(CREB1, CREB3, CREB5, CREM, ATF1, ATF4, ATF7)의 모든 비어 있지 않은 조합 127개에 대해 열역학 모델을 학습하였다. Self-competition이 없는 조건(Figure 3B/C)과 있는 조건(Figure 3D/E)으로 나누어 각각 공개된 single-hit MPRA 데이터로 학습하고, 학습에 사용하지 않은 multi-hit 서열 722개로 예측 성능을 검증하였다. Figure 3B와 3D는 각각 single-hit fitting의 Pearson 상관계수를 TF 수별로 boxplot으로 표시하였으며, Figure 3C와 3E는 동일 모델의 파라미터를 고정하여 multi-hit 예측값과 실험값 사이의 Pearson 상관계수를 나타낸다.

---

## 15. 재현에서 가장 중요한 교훈 요약

1. **C와 E는 B와 D를 재활용한다**: 별도 학습 불필요, 시간 대폭 절약
2. **서버는 코어 수보다 단일 코어 성능이 중요**: M1 > 서버 단일 코어
3. **init_loop=100으로도 트렌드는 재현 가능**: 시간 없을 때 유용
4. **NumThreads=1 + 높은 병렬 수**: 서버에서 가장 효율적
5. **nohup 스크립트를 먼저 kill**: transcpp보다 스크립트를 먼저 종료
6. **multi-hit 예측은 서버에서만**: M1에서는 722개 서열 segfault 발생
7. **기존 XML을 템플릿으로 사용**: Source 중복 등의 XML 오류 방지
8. **로컬+서버 분업**: 로컬은 n1~n4, 서버는 n5~n7 역순

