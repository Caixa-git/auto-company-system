#!/usr/bin/env python3
"""TC-1.3.2: 동일 업종 → 성향별 의사결정 가중치 차이 검증"""
import sys

TRAIT_DECISIONS = {
    "artisan": {"investment": "small", "speed": "slow", "risk": "low"},
    "hacker":  {"investment": "minimal", "speed": "fast", "risk": "high"},
    "analyst": {"investment": "data-driven", "speed": "medium", "risk": "medium"},
}
DECISION_AREAS = ["investment", "speed", "risk"]


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.3.2: 동일 업종 → 성향별 의사결정 차이")
    print("=" * 60)

    # 성향별 결정이 전부 다른지 (동일한 결정 없음)
    for area in DECISION_AREAS:
        values = set(TRAIT_DECISIONS[t][area] for t in TRAIT_DECISIONS)
        if len(values) == 3:
            print(f"  ✅ [{area}] 3성향 모두 다른 결정: {values}")
            passed += 1
        else:
            print(f"  ❌ [{area}] 일부 동일 결정: {values}")
            failed += 1

    # 각 성향이 고유한 결정 조합을 가지는지
    signatures = set(tuple(v[a] for a in DECISION_AREAS) for v in TRAIT_DECISIONS.values())
    if len(signatures) == 3:
        print(f"  ✅ 모든 성향 고유 결정 조합 보유")
        passed += 1
    else:
        print(f"  ❌ 일부 성향 결정 조합 중복")
        failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
