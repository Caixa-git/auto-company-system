#!/usr/bin/env python3
"""TC-1.2.3: 포트폴리오 카테고리 40% 초과 → Board 자동 거부"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
KPI_PATH = ROOT / "docs" / "kpi-config.json"
SCHEMA_PATH = ROOT / "docs" / "message-schema.json"

def load_kpi():
    with open(KPI_PATH) as f:
        cfg = json.load(f)
    return cfg["parameters"]["max_category_allocation_pct"]["value"]

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

def pct(cat_cap, total_cap):
    if total_cap == 0:
        return 0
    return (cat_cap / total_cap) * 100

def run():
    MAX_PCT = load_kpi()
    schema = load_schema()
    passed = 0
    failed = 0

    print("="*60)
    print(f"TC-1.2.3: 카테고리 비율 {MAX_PCT}% 초과 → 자동 거부")
    print("="*60)

    # 1. KPI 수치 확인
    print(f"\n--- 1. KPI 수치 확인 ---")
    assert MAX_PCT == 40, f"예상 40%, 실제 {MAX_PCT}%"
    print(f"  ✅ 포트폴리오 상한 = {MAX_PCT}% (Kaplan & Lerner 2010)")
    passed += 1

    # 2. 첫 회사 허용
    print(f"\n--- 2. 첫 회사 허용 ---")
    ok = pct(0, 0) <= MAX_PCT
    if ok:
        print(f"  ✅ 첫 회사 허용 (비율 0%)")
        passed += 1
    else:
        print(f"  ❌ 거부(실패)")
        failed += 1

    # 3. 이내 → 허용
    print(f"\n--- 3. 비율 이내 → 허용 ---")
    cases = [(300,1000,"30%"), (100,300,"33.3%"), (400,1000,"40%")]
    for cat, total, label in cases:
        ok = pct(cat, total) <= MAX_PCT
        if ok:
            print(f"  ✅ [{label}] 허용")
            passed += 1
        else:
            print(f"  ❌ [{label}] 거부(실패)")
            failed += 1

    # 4. 초과 → 거부
    print(f"\n--- 4. 비율 초과 → 거부 ---")
    cases = [(500,1000,"50%"), (450,1000,"45%"), (410,1000,"41%")]
    for cat, total, label in cases:
        ok = pct(cat, total) > MAX_PCT
        if not ok:
            print(f"  ❌ [{label}] 허용(실패)")
            failed += 1
        else:
            print(f"  ✅ [{label}] 거부")
            passed += 1

    # 5. 거부 메시지 스키마
    print(f"\n--- 5. 거부 메시지 스키마 ---")
    msg = {
        "message_id": "a0000003-0000-4000-8000-000000000003",
        "sender": "board",
        "receiver": "ceo:C_001",
        "type": "response",
        "timestamp": "2026-05-11T12:00:00+09:00",
        "payload": {
            "body": {
                "in_reply_to": "a0000000-0000-4000-8000-000000000000",
                "status": "rejected",
                "summary": f"카테고리 비율 45% 초과 (최대 {MAX_PCT}%)",
                "details": {
                    "reason": "portfolio_limit_exceeded",
                    "current_allocation_pct": 45.0,
                    "max_allowed_pct": MAX_PCT
                }
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
