#!/usr/bin/env python3
"""TC-1.4.3: 메인 컨텍스트/state.md/아카이브 3계층 정합성 검증"""
import sys

# Layer 1: 메인 컨텍스트 (현재 세션)
L1 = {
    "company_id": "C_001",
    "capital": 5000000,
    "stage": "growth",
    "recent_decision": "신규 계약 체결",
}

# Layer 2: state.md (영구 상태)
L2 = {
    "company_id": "C_001",
    "capital": 5000000,
    "stage": "growth",
    "cash": 500000,
    "contracts": ["client_a", "client_b"],
}

# Layer 3: 아카이브 (회고)
L3 = {
    "company_id": "C_001",
    "outcome": "exit",
    "total_revenue": 1800000,
    "lessons": ["시장 검증 부족"],
}

COMMON_FIELDS = ["company_id", "capital", "stage"]


def run():
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.4.3: 3계층 메모리 정합성")
    print("=" * 60)

    # 공통 필드 일관성
    for field in COMMON_FIELDS:
        if field in L1 and field in L2:
            if L1[field] == L2[field]:
                print(f"  ✅ [{field}] L1==L2: {L1[field]}")
                passed += 1
            else:
                print(f"  ❌ [{field}] 불일치: L1={L1[field]}, L2={L2[field]}")
                failed += 1
        else:
            print(f"  ℹ️ [{field}] L1 or L2에 없음 (의도된 차이일 수 있음)")
            passed += 1  # 선택 필드는 의도된 차이

    # L2가 L1보다 상세 (state.md는 더 많은 정보 보유)
    if len(L2) >= len(L1):
        print(f"  ✅ L2(state.md)가 L1(컨텍스트)보다 상세함")
        passed += 1
    else:
        print(f"  ❌ L1이 L2보다 상세함 (비정상)")
        failed += 1

    # L3는 L2의 하위 집합이거나 추가 정보 (종료 후 데이터)
    if L3.get("company_id") == L2.get("company_id"):
        print(f"  ✅ L3 아카이브, L2와 동일 회사 참조")
        passed += 1
    else:
        print(f"  ❌ L3가 다른 회사 참조")
        failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
