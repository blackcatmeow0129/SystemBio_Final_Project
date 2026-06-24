"""
Figure 3E multi-hit XML 생성 스크립트
fig3de_xmls/*.rates 완료 후 실행
반드시 서버(Linux)에서 실행 (Mac M1에서는 segfault 발생)

사용법:
    cd ~/cre_reproduction/neoParSA/tests/transcpp/fits
    python3 /path/to/generate_figure3e_mh.py
"""

import argparse
import os, glob, copy
import openpyxl
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Generate Figure 3E multi-hit XML files from completed Figure 3D fits.")
    parser.add_argument("--data-dir", type=Path, default=Path("~/Desktop/SB_final/ScienceDirect_files_26May2026_04-41-20.049").expanduser())
    parser.add_argument("--mmc4", type=Path, default=None)
    parser.add_argument("--fits-dir", type=Path, default=Path("~/cre_reproduction/neoParSA/tests/transcpp/fits").expanduser())
    parser.add_argument("--mh-dir", type=Path, default=None)
    parser.add_argument("--template-xml", type=Path, default=None,
                        help="Template XML with a stable transcpp structure. Defaults to fig3a_xmls/fig3a_m5_CREB1.xml.")
    return parser.parse_args()

def main():
    args = parse_args()
    mmc4 = args.mmc4 or args.data_dir / "1-s2.0-S2589004223028249-mmc4.xlsx"
    fits = args.fits_dir
    mh_dir = args.mh_dir or fits / "fig3de_mh_xmls"
    mh_dir.mkdir(parents=True, exist_ok=True)
    template_xml = args.template_xml or fits / "fig3a_xmls" / "fig3a_m5_CREB1.xml"

    print("=== Figure 3E multi-hit XML 생성 ===")
    print(f"mmc4: {mmc4}")
    print(f"fits_dir: {fits}")
    print(f"mh_dir: {mh_dir}")

    # multi-hit 데이터
    wb     = openpyxl.load_workbook(mmc4)
    rows_m = list(wb['multi-hit'].iter_rows(values_only=True))[1:]

    # multi-hit FASTA 생성
    fasta  = fits / "sequences" / "MRPA_multihit.fa"
    fasta.parent.mkdir(parents=True, exist_ok=True)
    with open(fasta, 'w') as f:
        for name, seq, expr in rows_m:
            if seq:
                f.write(f'>{name}\n')
                for i in range(0, len(seq), 60):
                    f.write(seq[i:i+60] + '\n')
    print(f"FASTA 생성: {fasta} ({len(rows_m)}개)")

    # 성공한 fig3a XML을 템플릿으로 사용 (중요!)
    tmpl_tree = ET.parse(template_xml)

    count = 0
    for rates_file in glob.glob(str(fits / 'fig3de_xmls' / '*.rates')):
        xml_file = rates_file.replace('.xml.rates', '.xml')
        if not os.path.exists(xml_file): continue

        out_path = mh_dir / os.path.basename(xml_file).replace('.xml','_mh_v2.xml')
        if os.path.exists(out_path): continue

        try:
            src_root  = ET.parse(xml_file).getroot()
            src_input = src_root.find('Input')

            # anneal=false 설정
            for elem in src_root.iter():
                if 'anneal' in elem.attrib:
                    elem.set('anneal', 'false')
            src_root.find('annealer_input').set('init_loop', '1')

            # Genes 교체 (multi-hit)
            genes = src_input.find('Genes')
            if genes is not None: src_input.remove(genes)
            genes  = ET.SubElement(src_input, 'Genes')
            source = ET.SubElement(genes, 'Source', {
                'name':'multi_hit', 'file':'sequences/MRPA_multihit.fa', 'type':'fasta'})
            for name, seq, expr in rows_m:
                if name and seq:
                    ET.SubElement(source, 'Gene', {
                        'name':str(name), 'header':str(name),
                        'left_bound':'-235', 'right_bound':'-38',
                        'TSS':'-1', 'promoter':'basic'})

            # RateData 교체
            rd = src_input.find('RateData')
            if rd is not None: src_input.remove(rd)
            rd = ET.SubElement(src_input, 'RateData', {'row':'ID','col':'gene'})
            tv = {'ID':'theonlyone'}
            tv.update({str(r[0]):str(r[2]) for r in rows_m if r[0] and r[2]})
            ET.SubElement(rd, 'TableRow', tv)

            # TFData 교체
            tfd = src_input.find('TFData')
            if tfd is not None: src_input.remove(tfd)
            tfd = ET.SubElement(src_input, 'TFData', {'row':'ID','col':'TF'})
            tfs = [tf.get('name') for tf in src_input.find('TFs').findall('TF')]
            tt  = {'ID':'theonlyone'}
            tt.update({tf:'100' for tf in tfs})
            ET.SubElement(tfd, 'TableRow', tt)

            # 템플릿으로 감싸기 (XML 구조 안정성)
            tmpl_root  = copy.deepcopy(tmpl_tree.getroot())
            tmpl_input = tmpl_root.find('Input')
            for tag in ['TFs','Genes','RateData','TFData']:
                old = tmpl_input.find(tag)
                new = src_input.find(tag)
                if old is not None: tmpl_input.remove(old)
                if new is not None: tmpl_input.append(copy.deepcopy(new))

            ET.ElementTree(tmpl_root).write(out_path, encoding='unicode', xml_declaration=True)
            count += 1
        except Exception as e:
            print(f"  Error {rates_file}: {e}")

    print(f"✅ {count}개 mh XML 생성 완료! → {mh_dir}")
    print("다음 단계: nohup bash run_figure3e_mh.sh > ~/fig3e_log.txt 2>&1 &")

if __name__ == '__main__':
    main()
