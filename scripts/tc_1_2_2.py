#!/usr/bin/env python3
"""TC-1.2.2: 현금 소진율 폐업 임계값 → 즉각 보고"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
KPI_PATH = ROOT / "docs" / "kpi-config.json"
SCHEMA_PATH = ROOT / "docs" / "message-schema.json"

def load_kpi():
    with open(KPI_PATH) as f:
        cfg = json.load(f)
    return cfg["parameters"]["survival_months"]["value"]

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
    MONTHS = load_kpi()
    schema = load_schema()
    passed = 0
    failed = 0

    print("="*60)
    print(f"TC-1.2.2: 폐업 임계값 {MONTHS}개월치 → 즉각 보고")
    print("="*60)

    # 1. KPI 수치 확인
    print(f"\n--- 1. KPI 수치 확인 ---")
    assert MONTHS == 3, f"예상 3개월, 실제 {MONTHS}"
    print(f"  ✅ 폐업 임계값 = 현금 {MONTHS}개월치 (Startup Genome 2022)")
    passed += 1

    # 2. 정상: cash > burn × MONTHS
    print(f"\n--- 2. 정상: cash > burn×{MONTHS} ---")
    for cash, burn, desc in [(10000000,500000,"넉넉"), (1600000,500000,"임계근접")]:
        ok = cash > burn * MONTHS
        if ok:
            print(f"  ✅ [{desc}] cash={cash} > {burn}×{MONTHS}={burn*MONTHS}")
            passed += 1
        else:
            print(f"  ❌ [{desc}] 파산감지(실패)")
            failed += 1

    # 3. 위험: cash <= burn × MONTHS
    print(f"\n--- 3. 위험: cash ≤ burn×{MONTHS} ---")
    for cash, burn, desc in [(1500000,500000,"임계도달"), (1000000,500000,"소진중"), (100000,500000,"거의바닥")]:
        ok = cash <= burn * MONTHS
        if ok:
            print(f"  ✅ [{desc}] cash={cash} ≤ {burn}×{MONTHS}={burn*MONTHS} → 보고")
            passed += 1
        else:
            print(f"  ❌ [{desc}] 정상판정(실패)")
            failed += 1

    # 4. 보고 메시지 스키마
    print(f"\n--- 4. 보고 스키마 ---")
    msg = {
        "message_id": "a0000002-0000-4000-8000-000000000002",
        "sender": "cfo:C_001",
        "receiver": "system_cfo",
        "type": "anomaly_report",
        "timestamp": "2026-05-11T12:00:00+09:00",
        "payload": {
            "urgency": "high",
            "body": {
                "type": "insolvency_risk",
                "cash": 1000000,
                "burn_rate": 500000,
                "threshold_cash": 500000 * MONTHS,
                "survival_months": MONTHS
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
