#!/bin/bash
# transcpp 설치 스크립트 - Mac M1
echo "=== transcpp 설치 (Mac M1) ==="

brew install libxml2 boost cmake

mkdir -p ~/cre_reproduction
cd ~/cre_reproduction

git clone https://github.com/kennethabarr/neoParSA
cd neoParSA && mkdir -p build && cd build
cmake .. -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make parsa -j4
cd ~/cre_reproduction

git clone https://github.com/kennethabarr/transcpp
cd transcpp
sed -i '' "s|PARSA_ROOT ?=.*|PARSA_ROOT ?=$HOME/cre_reproduction/neoParSA|g" Makefile
make XML_CFLAGS="$(xml2-config --cflags)" \
     XML_LIBS="$(xml2-config --libs)" \
     BOOST_DIR=$(brew --prefix boost)/include \
     CXXFLAGS="-std=c++17" transcpp

echo "✅ 완료: ~/cre_reproduction/transcpp/transcpp"
echo "다음 단계: printRate 패치 적용 (transcpp_printRate_patch.cpp 참조)"
