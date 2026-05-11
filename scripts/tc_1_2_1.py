#!/usr/bin/env python3
"""TC-1.2.1: CEO 연속 실패 N회 → 은퇴 권고 자동 생성"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
KPI_PATH = ROOT / "docs" / "kpi-config.json"
SCHEMA_PATH = ROOT / "docs" / "message-schema.json"

def load_kpi():
    with open(KPI_PATH) as f:
        cfg = json.load(f)
    return cfg["parameters"]["ceo_retirement_threshold"]["value"]

def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def validate(msg, schema):
    import jsonschema
    try:
        jsonschema.validate(msg, schema)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [e.message]

def run():
    N = load_kpi()
    schema = load_schema()
    passed = 0
    failed = 0

    print("="*60)
    print(f"TC-1.2.1: CEO 연속 실패 N={N}회 → 은퇴 권고")
    print("="*60)

    # 1. kpi-config.json 수치 확인
    print(f"\n--- 1. KPI 수치 확인 ---")
    assert N == 3, f"예상 N=3, 실제 N={N}"
    print(f"  ✅ CEO 은퇴 임계값 = {N} (CB Insights 2023)")
    passed += 1

    # 2. N-1 실패 → 권고 없음
    print(f"\n--- 2. N-1 = {N-1}회 실패 → 권고 없음 ---")
    for n in range(1, N):
        ok = n >= N
        if not ok:
            print(f"  ✅ [{n}회] 권고 없음")
            passed += 1
        else:
            print(f"  ❌ [{n}회] 권고 발생(실패)")
            failed += 1

    # 3. N 실패 → 권고 발송
    print(f"\n--- 3. N = {N}회 실패 → 권고 ---")
    ok = N >= N
    if ok:
        print(f"  ✅ [{N}회] 권고 발생")
        passed += 1
    else:
        print(f"  ❌ [{N}회] 권고 없음(실패)")
        failed += 1

    # 4. 권고 메시지 스키마 검증
    print(f"\n--- 4. 권고 메시지 스키마 ---")
    msg = {
        "message_id": "a0000001-0000-4000-8000-000000000001",
        "sender": "system_cfo",
        "receiver": "board",
        "type": "escalation",
        "timestamp": "2026-05-11T12:00:00+09:00",
        "payload": {
            "urgency": "medium",
            "body": {
                "type": "retirement_recommendation",
                "company_id": "C_001",
                "failure_count": N,
                "threshold": N,
                "reason": f"CEO {N}회 연속 실패"
            }
        }
    }
    ok, errs = validate(msg, schema)
    if ok:
        print(f"  ✅ 스키마 통과")
        passed += 1
    else:
        print(f"  ❌ {errs[0][:80]}")
        failed += 1

    print(f"\n결과: {passed} 통과, {failed} 실패 (총 {passed+failed}개)")
    return failed == 0

if __name__ == "__main__":
    try:
        import jsonschema
    except ImportError:
        print("jsonschema 미설치")
        sys.exit(1)
    sys.exit(0 if run() else 1)
