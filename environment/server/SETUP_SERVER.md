# 서버 (Linux) 환경 설정 가이드

> 실제 구현에 사용된 환경: **bds1 (Ubuntu 22.04, 32코어, 125GB RAM)**  
> Figure 3A, 3D(n5-7), 3E, 4D-K 등 계산량 많은 작업에 사용

---

## 1. 서버 접속 (점프서버 경유)

```bash
# 로컬에서 점프서버로
ssh jumpserver@118.41.98.18

# 점프서버에서 서버로
ssh hdhyun@220.149.111.120

# 또는 로컬에서 한번에 (ProxyJump)
ssh -J jumpserver@118.41.98.18 hdhyun@220.149.111.120
```

파일 전송:
```bash
# 로컬 → 서버 (점프서버 경유)
scp -J jumpserver@118.41.98.18 \
    ~/로컬/파일/*.rates \
    hdhyun@220.149.111.120:~/서버/경로/

# 서버 결과 임시 공유 (다운로드용)
curl -F "file=@figure.png" https://tmpfiles.org/api/v1/upload
# URL에서 /파일명 → /dl/파일명으로 변경하여 다운로드
```

## 2. Python 패키지 설치

```bash
pip install openpyxl numpy scipy matplotlib scikit-learn requests --break-system-packages
# 또는 conda 사용
conda install -c conda-forge openpyxl numpy scipy matplotlib scikit-learn
```

## 3. transcpp 빌드

```bash
sudo apt-get install -y libxml2-dev libboost-all-dev cmake git

mkdir -p ~/cre_reproduction && cd ~/cre_reproduction

# neoParSA
git clone https://github.com/kennethabarr/neoParSA
cd neoParSA && mkdir -p build && cd build
cmake .. -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_PREFIX_PATH=~/miniconda3
make parsa -j4
cd ~/cre_reproduction

# transcpp
git clone https://github.com/kennethabarr/transcpp
cd transcpp
sed -i "s|BOOST_DIR  ?=.*|BOOST_DIR  ?=$HOME/miniconda3/include|g" Makefile
sed -i "s|PARSA_ROOT ?=.*|PARSA_ROOT ?=$HOME/cre_reproduction/neoParSA|g" Makefile

make XML_CFLAGS="\`/usr/bin/xml2-config --cflags\`" \
     XML_LIBS="\`/usr/bin/xml2-config --libs\`" \
     BOOST_DIR=~/miniconda3/include \
     CXXFLAGS="-std=c++17 -DU_SHOW_CPLUSPLUS_API=0" transcpp
```

## 4. printRate 패치 적용 (필수!)

```bash
cd ~/cre_reproduction/transcpp
nano src/main/transcpp.cpp
# fly_sa->writeResult(); 다음에 아래 3줄 추가:
# ofstream ratefile((xmlname+".rates").c_str());
# embryo.printRate(ratefile, false);
# ratefile.close();

# 재컴파일
make XML_CFLAGS="\`/usr/bin/xml2-config --cflags\`" \
     XML_LIBS="\`/usr/bin/xml2-config --libs\`" \
     BOOST_DIR=~/miniconda3/include \
     CXXFLAGS="-std=c++17 -DU_SHOW_CPLUSPLUS_API=0" transcpp
```

## 5. 데이터 파일 저장 경로

```bash
# 서버로 데이터 전송
scp -J jumpserver@118.41.98.18 \
    ~/Desktop/SB_final/.../mmc*.xlsx \
    hdhyun@220.149.111.120:~/System_Biology_AS/
```

저장 경로:
```
~/System_Biology_AS/
├── 1-s2.0-S2589004223028249-mmc2.xlsx
├── 1-s2.0-S2589004223028249-mmc3.xlsx
└── 1-s2.0-S2589004223028249-mmc4.xlsx
```

## 6. 작업 폴더 생성

```bash
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/sequences
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3a_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3b_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_xmls
mkdir -p ~/cre_reproduction/neoParSA/tests/transcpp/fits/fig3de_mh_xmls
```

## 7. Figure별 실행 방법

> ⚠️ **transcpp는 항상 `fits/` 폴더에서 실행해야 한다**

### Figure 3A (서버 필수 ✅)

```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits

# XML 생성 (168개)
python3 /path/to/figures/Figure3/Figure3A/plot_figure3a.py --generate-xml

# 실행 (10코어 병렬)
nohup bash -c '
TRANSCPP=~/cre_reproduction/transcpp/transcpp
for xml in fig3a_xmls/*.xml; do
    [ -f "${xml%.xml}.xml.rates" ] && continue
    $TRANSCPP $xml > "${xml%.xml}.log" 2>&1 &
    while [ $(jobs -r | wc -l) -ge 10 ]; do sleep 3; done
done
wait' > ~/fig3a_log.txt 2>&1 &

# 진행 확인
watch -n 30 "ls fig3a_xmls/*.rates | wc -l"
```

### Figure 3D/E (서버 담당: n5~n7 역순 ✅)

```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits

# XML 생성
python3 /path/to/figures/Figure3/Figure3DE/generate_figure3de_xmls.py

# NumThreads=1로 수정 (필수)
sed -i 's/<NumThreads value="4"\/>/<NumThreads value="1"\/>/g' fig3de_xmls/*.xml

# n7→n5 역순 실행 (25코어 병렬)
nohup bash /path/to/figures/Figure3/Figure3DE/run_figure3de_server.sh \
    > ~/fig3de_server_log.txt 2>&1 &
echo "PID: $!"
```

### Figure 3E multi-hit 예측 (서버 필수 ✅)

```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits

# 로컬 rates 파일 먼저 전송받아야 함
# scp -J ... 로 전송

# multi-hit XML 생성
python3 /path/to/figures/Figure3/Figure3DE/generate_figure3e_mh.py

# 실행 (25코어 병렬)
nohup bash /path/to/figures/Figure3/Figure3DE/run_figure3e_mh.sh \
    > ~/fig3e_log.txt 2>&1 &

# 진행 확인
watch -n 60 "ls fig3de_mh_xmls/*_mh_v2.xml.rates | wc -l"
```

### Figure 4D-K (서버에서도 가능 ✅)

```bash
python3 /path/to/figures/Figure4/Figure4AK/reproduce_figure4.py \
    --best-xml ~/cre_reproduction/.../fig3de_n4_m5_CREB1_CREB3_CREM_ATF1.xml \
    --mmc4 ~/System_Biology_AS/mmc4.xlsx \
    --transcpp ~/cre_reproduction/transcpp/transcpp \
    --threads 4
```

### Figure 4L/M data-only (서버 ✅)

```bash
python3 /path/to/figures/Figure4/Figure4LM/train_figure4lm.py \
    --mode data-only \
    --mmc4 ~/System_Biology_AS/mmc4.xlsx \
    --fits-dir ~/cre_reproduction/neoParSA/tests/transcpp/fits
```

### 그래프 생성 후 결과 공유

```bash
# 서버에서 로컬로 임시 공유
curl -F "file=@~/System_Biology_AS/figure3DE_complete.png" \
     https://tmpfiles.org/api/v1/upload
# 출력된 URL에서 /파일명 → /dl/파일명 변경 후 접속
```

## 8. 서버 관리 명령어

```bash
# 전체 진행 상황
echo "Fig3A:  $(ls fig3a_xmls/*.rates 2>/dev/null | wc -l)/168" && \
echo "Fig3D:  $(ls fig3de_xmls/*.rates 2>/dev/null | wc -l)/1016" && \
echo "Fig3E:  $(ls fig3de_mh_xmls/*_mh_v2.xml.rates 2>/dev/null | wc -l)/127" && \
echo "실행 중: $(ps aux | grep transcpp | grep -v grep | wc -l)개"

# TF 수별 완료 현황
for n in 1 2 3 4 5 6 7; do
    done=$(ls fig3de_xmls/fig3de_n${n}_*.rates 2>/dev/null | wc -l)
    total=$(ls fig3de_xmls/fig3de_n${n}_*.xml 2>/dev/null | wc -l)
    echo "n${n}: ${done}/${total}"
done

# 프로세스 완전 종료
pkill -9 -f run_fig3 && sleep 3 && pkill -9 -f transcpp

# nohup 로그 확인
tail -f ~/fig3de_server_log.txt
```

## 서버에서 실행 가능 여부 요약

| Figure | 서버 | 비고 |
|---|---|---|
| Figure 3A | ✅ 필수 | 168개 fitting |
| Figure 3B/C | ✅ | build_figure3bc.py 사용 |
| Figure 3D (n5-7) | ✅ 필수 | 역순 실행 |
| Figure 3E | ✅ 필수 | Mac M1 segfault |
| Figure 4D-K | ✅ | |
| Figure 4L/M | ✅ data-only | |
| Figure 5 | ✅ | |
