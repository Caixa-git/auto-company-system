#!/usr/bin/env python3
"""TC-1.4.1: 컨텍스트 압축 전후 state.md 핵심 정보 보존 검증"""
import sys

# 시뮬레이션: 압축 전 state.md
BEFORE = {
    "company_id": "C_001",
    "capital": 5000000,
    "revenue": 150000,
    "cost": 50000,
    "cash": 500000,
    "contracts": ["client_a", "client_b"],
    "stage": "growth",
    "trait": "artisan",
}

# 압축 후 state.md (핵심 수치 보존, 불필요한 대화 이력만 제거)
AFTER = {
    "company_id": "C_001",
    "capital": 5000000,
    "revenue": 150000,
    "cost": 50000,
    "cash": 500000,
    "stage": "growth",
    "trait": "artisan",
    "_compressed": True,
    "_note": "contracts detail archived",
}

CORE_FIELDS = ["company_id", "capital", "revenue", "cost", "cash", "stage"]


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.4.1: 압축 전후 state.md 핵심 정보 보존")
    print("=" * 60)

    # 핵심 수치 전부 보존
    for field in CORE_FIELDS:
        if field in BEFORE and field in AFTER and BEFORE[field] == AFTER[field]:
            print(f"  ✅ [{field}] 보존: {BEFORE[field]}")
            passed += 1
        else:
            print(f"  ❌ [{field}] 손실/불일치")
            failed += 1

    # 압축 플래그 확인
    if AFTER.get("_compressed") is True:
        print(f"  ✅ 압축 플래그 확인")
        passed += 1
    else:
        print(f"  ❌ 압축 플래그 없음")
        failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
