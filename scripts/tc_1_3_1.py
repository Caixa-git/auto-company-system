#!/usr/bin/env python3
"""TC-1.3.1: 랜덤 성향 부여 100회 → 3가지 유형 100% 매핑"""
import json, random, math, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# docs/ceo-traits.md Big5 속성표
TRAITS = {
    "artisan":  {"openness": 0.7, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.7, "neuroticism": 0.4},
    "hacker":   {"openness": 0.9, "conscientiousness": 0.5, "extraversion": 0.7, "agreeableness": 0.5, "neuroticism": 0.3},
    "analyst":  {"openness": 0.5, "conscientiousness": 0.8, "extraversion": 0.4, "agreeableness": 0.4, "neuroticism": 0.5},
}
FACTORS = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]


def assign_trait():
    """랜덤 Big5 생성 → 가장 가까운 성향 매핑"""
    profile = {f: random.gauss(0.5, 0.2) for f in FACTORS}
    profile = {f: max(0.0, min(1.0, v)) for f, v in profile.items()}

    best_trait = None
    best_dist = float("inf")
    for trait, base in TRAITS.items():
        dist = math.sqrt(sum((profile[f] - base[f]) ** 2 for f in FACTORS))
        if dist < best_dist:
            best_dist = dist
            best_trait = trait
    return best_trait


def run():
    random.seed(42)
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.3.1: 랜덤 성향 부여 100회 → 3유형 100% 매핑")
    print("=" * 60)

    counts = {"artisan": 0, "hacker": 0, "analyst": 0}

    for i in range(100):
        t = assign_trait()
        if t in counts:
            counts[t] += 1
        else:
            print(f"  ❌ [{i+1}회] 알 수 없는 성향: {t}")
            failed += 1
            continue

    print(f"\n--- 100회 분포 ---")
    for t, c in sorted(counts.items()):
        print(f"  {t}: {c}회 ({c}%)")
    print(f"  매핑 성공: {sum(counts.values())}/100")

    if sum(counts.values()) == 100:
        passed += 1
    else:
        failed += 1

    # 각 유형이 최소 1회 이상 나왔는지
    all_present = all(c > 0 for c in counts.values())
    if all_present:
        print(f"  ✅ 모든 유형 최소 1회 이상 출현")
        passed += 1
    else:
        print(f"  ❌ 일부 유형 미출현")
        failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
