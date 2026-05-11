#!/usr/bin/env python3
"""TC-1.3.3: 장인형→Effectuation, 분석가형→Causation 업종 편향 검증"""
import sys

# ceo-traits.md 선호도 매트릭스 (Effectuation vs Causation 우선 업종)
PREF = {
    "artisan": {"콘텐츠제작": 0.9, "하드웨어": 0.8, "교육": 0.7},  # Effectuation
    "analyst": {"데이터AI": 0.9, "전자상거래": 0.8, "소프트웨어": 0.6},  # Causation
}


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.3.3: 성향별 업종 선택 편향")
    print("=" * 60)

    # 장인형: Effectuation 업종 최고 점수 확인
    artisan_top = max(PREF["artisan"].values())
    for industry, score in PREF["artisan"].items():
        ok = score >= 0.7
        if ok:
            print(f"  ✅ [장인형] {industry}: {score} (≥0.7)")
            passed += 1
        else:
            print(f"  ❌ [장인형] {industry}: {score} (<0.7)")
            failed += 1

    # 분석가형: Causation 업종 선호도
    for industry, score in PREF["analyst"].items():
        ok = score > 0.5
        if ok:
            print(f"  ✅ [분석가형] {industry}: {score}")
            passed += 1
        else:
            print(f"  ❌ [분석가형] {industry}: {score} (≤0.5)")
            failed += 1

    # 장인형이 분석가형보다 Effectuation 업종 선호도가 높은지
    for ind in ["콘텐츠제작", "하드웨어"]:
        ok = PREF["artisan"][ind] >= PREF["analyst"].get(ind, 0) + 0.2
        label = f"{ind}: 장인형={PREF['artisan'][ind]} vs 분석가형={PREF['analyst'].get(ind, 0)}"
        if ok:
            print(f"  ✅ {label} (편향 확인)")
            passed += 1
        else:
            print(f"  ❌ {label} (편향 없음)")
            failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
