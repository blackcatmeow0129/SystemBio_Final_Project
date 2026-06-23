# Figure 3B/C

팀원이 완성한 스크립트를 사용한다.

## 실행 방법

```bash
python3 build_figure3bc.py \
    --transcpp /path/to/transcpp \
    --mmc4 /path/to/mmc4.xlsx \
    --runs 4 \
    --parallel 4
```

## 파일 설명

| 파일 | 설명 |
|---|---|
| `build_figure3bc.py` | 전체 파이프라인 (XML 생성 → fit → multi-hit 예측 → 그래프) |
| `selected_fit_manifest.tsv` | 사용된 fit 파일 목록 |
| `Figure3BC_run_correlations.tsv` | 각 run별 R값 |
| `Figure3BC_group_statistics.tsv` | TF 수별 통계 |
