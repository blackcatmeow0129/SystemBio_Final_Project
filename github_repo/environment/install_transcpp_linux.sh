#!/bin/bash
# transcpp 설치 스크립트 - Linux Ubuntu
echo "=== transcpp 설치 (Linux Ubuntu) ==="

sudo apt-get install -y libxml2-dev libboost-all-dev cmake

mkdir -p ~/cre_reproduction
cd ~/cre_reproduction

git clone https://github.com/kennethabarr/neoParSA
cd neoParSA && mkdir -p build && cd build
cmake .. -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_PREFIX_PATH=~/miniconda3
make parsa -j4
cd ~/cre_reproduction

git clone https://github.com/kennethabarr/transcpp
cd transcpp
sed -i "s|BOOST_DIR  ?=.*|BOOST_DIR  ?=$HOME/miniconda3/include|g" Makefile
sed -i "s|PARSA_ROOT ?=.*|PARSA_ROOT ?=$HOME/cre_reproduction/neoParSA|g" Makefile
make XML_CFLAGS="\`/usr/bin/xml2-config --cflags\`" \
     XML_LIBS="\`/usr/bin/xml2-config --libs\`" \
     BOOST_DIR=~/miniconda3/include \
     CXXFLAGS="-std=c++17 -DU_SHOW_CPLUSPLUS_API=0" transcpp

echo "✅ 완료: ~/cre_reproduction/transcpp/transcpp"
echo "다음 단계: printRate 패치 적용 (transcpp_printRate_patch.cpp 참조)"
