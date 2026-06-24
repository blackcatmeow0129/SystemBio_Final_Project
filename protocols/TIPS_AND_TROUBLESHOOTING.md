# Tips & Troubleshooting

## 자주 발생하는 오류와 해결법

### 1. "Could not open file sequences/MRPA_baseM.fa"
**원인**: transcpp를 fits 폴더가 아닌 다른 폴더에서 실행  
**해결**: 반드시 `fits/` 폴더에서 실행
```bash
cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
~/cre_reproduction/transcpp/transcpp your_file.xml
```

### 2. Segmentation fault (multi-hit 예측)
**원인**: Mac M1에서 722개 multi-hit 서열 처리 시 메모리 문제  
**해결**: 서버(Linux)에서 실행. scp로 rates 파일 전송 후 서버에서 mh 예측

### 3. Floating point exception
**원인**: gene name 중복 또는 XML 구조 문제  
**해결**:
- gene name에 prefix 추가 (`rev_`, `rear_` 등)
- XML을 처음부터 새로 작성하거나 기존 XML을 템플릿으로 사용

### 4. 모든 예측값이 동일 (rates 파일)
**원인**: XML에 Source 태그 중복  
**해결**: XML에서 Source 개수 확인
```bash
grep -c "Source name" your_file.xml  # 1이어야 함
```

### 5. nohup 프로세스가 계속 새 프로세스 생성
**원인**: nohup bash 스크립트가 살아있어서 계속 새 transcpp 생성  
**해결**: 스크립트를 먼저 kill
```bash
pkill -9 -f run_fig3     # 스크립트 먼저
sleep 3
pkill -9 -f transcpp     # 그 다음 transcpp
```

### 6. FASTA 서열 인식 불가
**원인**: FASTA가 한 줄로 작성됨  
**해결**: 60자씩 줄바꿈
```python
for i in range(0, len(seq), 60):
    f.write(seq[i:i+60] + '\n')
```

### 7. "score not same after rerunning" 오류
**원인**: 멀티스레드 비결정성  
**해결**: rates 파일이 생성됐는지 확인 후 사용 가능하면 무시
```bash
ls *.rates  # 파일이 있으면 사용 가능
```

---

## 시간 절약 팁

### init_loop 설정

| 목적 | init_loop | 소요시간 (n3 기준) |
|---|---|---|
| 빠른 트렌드 확인 | 100 | ~10분 |
| 중간 품질 | 1,000 | ~60분 |
| 논문 수준 | 100,000 | 수시간+ |

### 로컬 + 서버 분업

```
로컬 M1: n1~n4 (작은 TF 수, 단일 코어 빠름)
서버: n5~n7 역순 (큰 TF 수, 많은 코어 활용)
```

### NumThreads 설정

```
NumThreads=1 + 병렬 프로세스 수로만 제어
→ 서버 32코어에서: 병렬 25~30개
```

### multi-hit 예측 (Fig3C/E)

```
rates 파일 완료 → 서버로 scp 전송 → 서버에서 mh XML 생성 → 서버에서 실행
(로컬에서는 segfault 발생)
```

---

## 진행 상황 모니터링

```bash
# 전체 상태 확인 원라이너
echo "=== 현재 상태 ===" && \
echo "Fig3A: $(ls fig3a_xmls/*.rates 2>/dev/null | wc -l)/168" && \
echo "Fig3B: $(ls fig3b_xmls/*.rates 2>/dev/null | wc -l)개" && \
echo "Fig3D: $(ls fig3de_xmls/*.rates 2>/dev/null | wc -l)/1016" && \
echo "Fig3E mh: $(ls fig3de_mh_xmls/*_mh_v2.xml.rates 2>/dev/null | wc -l)/127" && \
echo "실행 중: $(ps aux | grep transcpp | grep -v grep | wc -l)개"
```

---

## 서버 접속 (점프서버 경유)

```bash
# 점프서버 → 서버
ssh jumpserver@서버주소
ssh 서버이름

# 파일 전송 (로컬 → 서버)
scp -J jumpserver@서버주소 \
    ~/path/to/files/*.rates \
    서버이름:~/path/to/destination/

# 임시 파일 공유
curl -F "file=@figure.png" https://tmpfiles.org/api/v1/upload
# 출력 URL에서 /파일명 → /dl/파일명으로 변경하여 다운로드
```
