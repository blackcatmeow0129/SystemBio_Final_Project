#!/bin/bash
# Figure 3D/E 실행 스크립트 (Linux 서버, n5~n7 역순)
# 사용법: nohup bash run_figure3de_server.sh > ~/fig3de_server_log.txt 2>&1 &
#
# 주의: NumThreads=1로 XML 생성 필요
# sed -i 's/<NumThreads value="4"\/>/<NumThreads value="1"\/>/g' fig3de_xmls/*.xml

FITS=${FITS:-~/cre_reproduction/neoParSA/tests/transcpp/fits}
TRANSCPP=${TRANSCPP:-~/cre_reproduction/transcpp/transcpp}
PARALLEL=${PARALLEL:-25}  # 서버 32코어에서 25개 권장
TF_COUNTS=${TF_COUNTS:-"7 6 5"}

cd $FITS
echo "=== Fig3D/E n7~n5 역순 실행 시작 (${PARALLEL}개 병렬) ==="

for n in $TF_COUNTS; do
    echo "n${n} 시작..."
    for xml in fig3de_xmls/fig3de_n${n}_*.xml; do
        [ -f "${xml%.xml}.xml.rates" ] && continue
        name=$(basename $xml .xml)
        $TRANSCPP $xml > fig3de_xmls/${name}.log 2>&1 &
        while [ $(jobs -r | wc -l) -ge $PARALLEL ]; do sleep 3; done
    done
done
wait
echo "✅ n5~n7 완료!"
