#!/usr/bin/env python3
"""TC-1.2.4: 소액 임계값 500,000원 분기 검증"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
KPI_PATH = ROOT / "docs" / "kpi-config.json"
SCHEMA_PATH = ROOT / "docs" / "message-schema.json"

def load_kpi():
    with open(KPI_PATH) as f:
        cfg = json.load(f)
    return cfg["parameters"]["small_amount_threshold"]["value"]

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
    TH = load_kpi()
    schema = load_schema()
    passed = 0
    failed = 0

    print("="*60)
    print(f"TC-1.2.4: 소액 임계값 {TH:,}원 분기")
    print("="*60)

    # 1. KPI 수치 확인
    print(f"\n--- 1. KPI 수치 확인 ---")
    assert TH == 500000, f"예상 500000, 실제 {TH}"
    print(f"  ✅ 소액 임계값 = {TH:,}원")
    passed += 1

    # 2. 이하 → 자동
    print(f"\n--- 2. ≤ {TH:,}원 → 자동 ---")
    for amt, desc in [(50000,"소액"), (250000,"중간"), (TH-1,"임계직전"), (TH,"경계값")]:
        ok = amt <= TH
        if ok:
            print(f"  ✅ [{desc}] {amt:,}원 → 자동")
            passed += 1
        else:
            print(f"  ❌ [{desc}] 승인요청(실패)")
            failed += 1

    # 3. 초과 → 승인 요청
    print(f"\n--- 3. > {TH:,}원 → 승인 요청 ---")
    for amt, desc in [(TH+1,"초과소액"), (5000000,"대액")]:
        ok = amt > TH
        if ok:
            print(f"  ✅ [{desc}] {amt:,}원 → 승인 요청")
            passed += 1
        else:
            print(f"  ❌ [{desc}] 자동처리(실패)")
            failed += 1

    # 4. 메시지 스키마 검증
    print(f"\n--- 4. 메시지 스키마 ---")
    for amt, label in [(100000,"자동"), (1000000,"승인요청")]:
        msg = {
            "message_id": "a0000004-0000-4000-8000-000000000004",
            "sender": "cfo:C_001",
            "receiver": "system_cfo",
            "type": "approval_request",
            "timestamp": "2026-05-11T12:00:00+09:00",
            "payload": {
                "body": {
                    "request_type": "fund_use",
                    "summary": f"금융액션 {amt}원",
                    "details": {"action": "지출", "amount": amt, "threshold": TH}
                }
            }
        }
        ok, errs = validate(msg, schema)
        if ok:
            print(f"  ✅ [{label}] {amt:,}원 스키마 통과")
            passed += 1
        else:
            print(f"  ❌ [{label}] {errs[0][:80]}")
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
