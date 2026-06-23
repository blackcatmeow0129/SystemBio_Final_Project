/**
 * transcpp printRate 패치
 *
 * 파일: transcpp/src/main/transcpp.cpp
 * 위치: fly_sa->writeResult(); 바로 다음 줄에 아래 코드 추가
 *
 * 이 패치 없이는 rates 파일이 자동 저장되지 않는다.
 */

// ===== 추가할 코드 (fly_sa->writeResult(); 다음에 삽입) =====
ofstream ratefile((xmlname+".rates").c_str());
embryo.printRate(ratefile, false);
ratefile.close();
// ===== 여기까지 =====

/**
 * 전체 컨텍스트:
 *
 * fly_sa->writeResult();
 * ofstream ratefile((xmlname+".rates").c_str());  // <-- 추가
 * embryo.printRate(ratefile, false);               // <-- 추가
 * ratefile.close();                                // <-- 추가
 *
 * 추가 후 재컴파일 필요:
 * make XML_CFLAGS="..." XML_LIBS="..." ... transcpp
 */
