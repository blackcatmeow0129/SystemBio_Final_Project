#!/bin/bash
# Figure 3D/E 실행 스크립트 (Mac M1 로컬, n1~n4)
# 사용법: bash run_figure3de_local.sh

FITS=${FITS:-~/cre_reproduction/neoParSA/tests/transcpp/fits}
TRANSCPP=${TRANSCPP:-~/cre_reproduction/transcpp/transcpp}
PARALLEL=${PARALLEL:-7}  # Mac M1 권장: 7코어
TF_COUNTS=${TF_COUNTS:-"1 2 3 4"}

cd $FITS
echo "=== Fig3D/E n1~n4 실행 시작 (${PARALLEL}개 병렬) ==="

for n in $TF_COUNTS; do
    for xml in fig3de_xmls/fig3de_n${n}_*.xml; do
        [ -f "${xml%.xml}.xml.rates" ] && continue
        name=$(basename $xml .xml)
        $TRANSCPP $xml > fig3de_xmls/${name}.log 2>&1 &
        while [ $(jobs -r | wc -l) -ge $PARALLEL ]; do sleep 3; done
    done
done
wait
echo "✅ n1~n4 완료!"
