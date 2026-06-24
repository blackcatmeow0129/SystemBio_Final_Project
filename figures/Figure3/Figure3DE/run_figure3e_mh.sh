#!/bin/bash
# Figure 3E multi-hit 예측 실행 스크립트 (서버에서 실행)
# 사용법: nohup bash run_figure3e_mh.sh > ~/fig3e_log.txt 2>&1 &

FITS=${FITS:-~/cre_reproduction/neoParSA/tests/transcpp/fits}
TRANSCPP=${TRANSCPP:-~/cre_reproduction/transcpp/transcpp}
PARALLEL=${PARALLEL:-25}

cd $FITS
echo "=== Fig3E multi-hit 예측 시작 (${PARALLEL}개 병렬) ==="

for xml in fig3de_mh_xmls/*_mh_v2.xml; do
    [ -f "${xml%.xml}.xml.rates" ] && continue
    name=$(basename $xml .xml)
    $TRANSCPP $xml > fig3de_mh_xmls/${name}.log 2>&1 &
    while [ $(jobs -r | wc -l) -ge $PARALLEL ]; do sleep 3; done
done
wait
echo "✅ Fig3E multi-hit 예측 완료!"
