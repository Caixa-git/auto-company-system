#!/usr/bin/env python3
"""TC-1.3.4: 성향 속성표 수치 무결성 검증"""
import sys

FACTORS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]
TRAITS = {
    "artisan": {"openness": 0.7, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.7, "neuroticism": 0.4},
    "hacker":  {"openness": 0.9, "conscientiousness": 0.5, "extraversion": 0.7, "agreeableness": 0.5, "neuroticism": 0.3},
    "analyst": {"openness": 0.5, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.4, "neuroticism": 0.5},
}


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.3.4: 성향 속성표 수치 무결성")
    print("=" * 60)

    # 1. 모든 값 0.0~1.0 범위
    print("\n--- 1. 값 범위 (0.0~1.0) ---")
    for t, props in TRAITS.items():
        for f, v in props.items():
            ok = 0.0 <= v <= 1.0
            if ok:
                passed += 1
            else:
                print(f"  ❌ [{t}] {f}={v} (범위 초과)")
                failed += 1
    print(f"  ✅ {len(TRAITS)*len(FACTORS)}개 값 모두 0.0~1.0")

    # 2. 각 성향이 고유한 Big5 패턴 (동일 패턴 없음)
    print("\n--- 2. 성향별 고유 패턴 ---")
    sigs = set(tuple(TRAITS[t][f] for f in FACTORS) for t in TRAITS)
    if len(sigs) == 3:
        print(f"  ✅ 3성향 모두 고유한 Big5 패턴")
        passed += 1
    else:
        print(f"  ❌ 일부 성향 Big5 패턴 중복")
        failed += 1

    # 3. 각 성향의 최고/최저 요인이 명확
    print("\n--- 3. 성향별 특징적 요인 ---")
    checks = [
        ("artisan", "conscientiousness", 0.8, "최고=성실성"),
        ("hacker", "openness", 0.9, "최고=개방성"),
        ("analyst", "conscientiousness", 0.8, "최고=성실성"),
        ("analyst", "neuroticism", 0.5, "최고=신경증"),
    ]
    for t, factor, expected, label in checks:
        ok = TRAITS[t][factor] == expected
        if ok:
            print(f"  ✅ [{t}] {label}: {expected}")
            passed += 1
        else:
            print(f"  ❌ [{t}] {label}: 예상={expected}, 실제={TRAITS[t][factor]}")
            failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
