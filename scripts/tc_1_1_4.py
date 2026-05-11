#!/usr/bin/env python3
"""
TC-1.1.4: 에스컬레이션 메시지 payload 변조 방지 검증
- 체인 중간에서 payload 수정 없이 원본 보존
- 정보 왜곡(MAST 2025 — 멀티에이전트 실패 1순위 원인) 방지
"""
import json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def load_schema():
    with open(ROOT / "docs" / "message-schema.json") as f:
        return json.load(f)


def validate(msg, schema):
    import jsonschema
    try:
        jsonschema.validate(msg, schema)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [e.message]


def payload_hash(msg):
    """payload의 안정적인 SHA-256 해시"""
    return hashlib.sha256(
        json.dumps(msg["payload"], sort_keys=True).encode()
    ).hexdigest()


# ── 정상 체인 ──────────────────────────────────────────
# 각 체인은 hop 목록(sender→receiver)과 base_msg로 구성
# hop 통과 후 payload가 원본과 동일한지 검증

TEST_CHAINS = [
    {
        "name": "재무 이상 보고 (CFO → System CFO → Board)",
        "hops": [("cfo:C_001", "system_cfo"), ("system_cfo", "board")],
        "msg": {
            "message_id": "a0000001-0000-4000-8000-000000000001",
            "sender": "cfo:C_001",
            "receiver": "system_cfo",
            "type": "escalation",
            "timestamp": "2026-05-11T12:00:00+09:00",
            "payload": {
                "urgency": "medium",
                "body": {
                    "type": "financial_anomaly",
                    "description": "매출 대비 비용 300% 초과",
                    "revenue": 10000,
                    "cost": 35000,
                    "period": "2026-05",
                },
            },
        },
    },
    {
        "name": "감사 이상 보고 (Auditor → Board → System Auditor)",
        "hops": [("company_auditor:C_001", "board"), ("board", "system_auditor")],
        "msg": {
            "message_id": "a0000002-0000-4000-8000-000000000002",
            "sender": "company_auditor:C_001",
            "receiver": "board",
            "type": "escalation",
            "timestamp": "2026-05-11T12:05:00+09:00",
            "payload": {
                "urgency": "high",
                "body": {
                    "type": "report_delay",
                    "description": "CEO 재무 보고 30분 지연 감지",
                    "delay_minutes": 30,
                },
                "attachments": [
                    {
                        "name": "evidence",
                        "content": {
                            "log_count": 3,
                            "last_event": "2026-05-11T11:35:00",
                        },
                    }
                ],
            },
        },
    },
    {
        "name": "절대 에스컬레이션 (System Auditor → Human 직행)",
        "hops": [("system_auditor", "human")],
        "msg": {
            "message_id": "a0000003-0000-4000-8000-000000000003",
            "sender": "system_auditor",
            "receiver": "human",
            "type": "escalation",
            "timestamp": "2026-05-11T13:00:00+09:00",
            "payload": {
                "urgency": "absolute",
                "body": {
                    "issue": "Hermes API 10회 연속 타임아웃 — 시스템 종료 검토 필요",
                    "affected": ["ceo:C_001", "cfo:C_001", "board"],
                    "recommendation": "긴급 점검",
                },
            },
        },
    },
]

# ── 변조 시나리오 ──────────────────────────────────────
# 원본과 변조본의 해시 차이를 감지할 수 있는지 검증

TAMPER_SCENARIOS = [
    {
        "name": "payload.body.amount 다운그레이드",
        "original": {
            "message_id": "a0000004-0000-4000-8000-000000000004",
            "sender": "cfo:C_001",
            "receiver": "system_cfo",
            "type": "escalation",
            "timestamp": "2026-05-11T14:00:00+09:00",
            "payload": {
                "urgency": "high",
                "body": {"type": "loss", "amount": 50000},
            },
        },
        "tampered": {
            "message_id": "a0000004-0000-4000-8000-000000000004",
            "sender": "cfo:C_001",
            "receiver": "system_cfo",
            "type": "escalation",
            "timestamp": "2026-05-11T14:00:00+09:00",
            "payload": {
                "urgency": "high",
                "body": {"type": "loss", "amount": 30000},  # 50000→30000 변조!
            },
        },
    },
    {
        "name": "payload.urgency 다운그레이드 (absolute → low)",
        "original": {
            "message_id": "a0000005-0000-4000-8000-000000000005",
            "sender": "system_auditor",
            "receiver": "human",
            "type": "escalation",
            "timestamp": "2026-05-11T14:05:00+09:00",
            "payload": {
                "urgency": "absolute",
                "body": {"issue": "시스템 종료 필요"},
            },
        },
        "tampered": {
            "message_id": "a0000005-0000-4000-8000-000000000005",
            "sender": "system_auditor",
            "receiver": "human",
            "type": "escalation",
            "timestamp": "2026-05-11T14:05:00+09:00",
            "payload": {
                "urgency": "low",  # absolute → low 변조!
                "body": {"issue": "시스템 종료 필요"},
            },
        },
    },
]


def run():
    schema = load_schema()
    passed = 0
    failed = 0
    total = 0

    print("=" * 60)
    print("TC-1.1.4: 에스컬레이션 payload 변조 방지 검증")
    print("=" * 60)

    # ── 1. 정상 체인: payload 원본 보존 ──
    print("\n--- 1. 정상 체인: payload 원본 보존 ---")
    for chain in TEST_CHAINS:
        msg = chain["msg"]
        ok, errors = validate(msg, schema)
        if not ok:
            print(f"  ❌ [{chain['name']}] 스키마 오류: {errors[0][:80]}")
            failed += 1
            total += 1
            continue

        orig_hash = payload_hash(msg)
        hop_ok = True

        for i, (sender, receiver) in enumerate(chain["hops"]):
            hop_msg = {**msg, "sender": sender, "receiver": receiver}
            if payload_hash(hop_msg) != orig_hash:
                print(
                    f"  ❌ [{chain['name']}] Hop {i+1} payload 변조!"
                )
                print(f"     원본: {orig_hash[:16]}...")
                print(f"     hop:  {payload_hash(hop_msg)[:16]}...")
                hop_ok = False
                failed += 1
                total += 1
                break

        if hop_ok:
            print(
                f"  ✅ [{chain['name']}] {len(chain['hops'])}hop payload 보존"
            )
            passed += 1
            total += 1

    # ── 2. 변조 감지 ──
    print("\n--- 2. 변조 감지: payload 변경 시 해시 불일치 ---")
    for sc in TAMPER_SCENARIOS:
        orig_ok, _ = validate(sc["original"], schema)
        if not orig_ok:
            print(f"  ❌ [{sc['name']}] 원본 스키마 오류")
            failed += 1
            total += 1
            continue

        o_hash = payload_hash(sc["original"])
        t_hash = payload_hash(sc["tampered"])

        if o_hash != t_hash:
            print(f"  ✅ [{sc['name']}] 변조 감지 (해시 불일치)")
            passed += 1
            total += 1
        else:
            print(f"  ❌ [{sc['name']}] 변조 미감지 (해시 동일)")
            failed += 1
            total += 1

    print()
    print(f"결과: {passed} 통과, {failed} 실패 (총 {total}개)")
    return failed == 0


if __name__ == "__main__":
    try:
        import jsonschema
    except ImportError:
        print("jsonschema 미설치 — pip install jsonschema 필요")
        sys.exit(1)
    sys.exit(0 if run() else 1)
