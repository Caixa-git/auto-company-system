#!/usr/bin/env python3
"""TC-1.1.1: 모든 에이전트 유형 동일 JSON 스키마 통과 검증"""
import json, sys, os
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "docs" / "message-schema.json"

def load_schema(path=None):
    path = path or SCHEMA_PATH
    with open(path) as f:
        return json.load(f)

def validate(message, schema=None):
    """메시지가 ACS 스키마에 맞는지 검증"""
    import jsonschema
    if schema is None:
        schema = load_schema()
    try:
        jsonschema.validate(message, schema)
        return True, []
    except jsonschema.exceptions.ValidationError as e:
        return False, [e.message]

def generate_test_messages():
    """TC-1.1.1용 테스트 메시지 6종 — 모든 에이전트 유형"""
    return [
        # CEO → Board 승인요청
        {
            "message_id": "a1b2c3d4-e5f6-4789-8abc-def012345678",
            "sender": "ceo:C_001",
            "receiver": "board",
            "type": "approval_request",
            "timestamp": "2026-05-11T06:00:00+09:00",
            "payload": {
                "body": {"request": "업종 선택 승인 요청", "industry": "AI 콘텐츠 생성"}
            }
        },
        # Board → CEO 응답
        {
            "message_id": "b2c3d4e5-f6a7-5890-9bcd-ef0123456789",
            "sender": "board",
            "receiver": "ceo:C_001",
            "type": "response",
            "timestamp": "2026-05-11T06:01:00+09:00",
            "payload": {
                "body": {"approved": True, "note": "업종 승인 완료"}
            }
        },
        # Company CFO → System CFO 재무보고
        {
            "message_id": "c3d4e5f6-a7b8-6901-acde-f01234567890",
            "sender": "cfo:C_001",
            "receiver": "system_cfo",
            "type": "financial_report",
            "timestamp": "2026-05-11T06:00:00Z",
            "payload": {
                "urgency": "low",
                "body": {
                    "revenue": 0,
                    "cost": 5000,
                    "cash": 50000,
                    "period": "2026-05-01~2026-05-11"
                },
                "attachments": [
                    {"name": "transaction_log", "content": {"count": 3, "items": []}}
                ]
            }
        },
        # Company Auditor → Board 이상보고
        {
            "message_id": "d4e5f6a7-b8c9-7012-bdef-012345678901",
            "sender": "company_auditor:C_001",
            "receiver": "board",
            "type": "anomaly_report",
            "timestamp": "2026-05-11T06:05:00+09:00",
            "payload": {
                "urgency": "medium",
                "body": {
                    "type": "report_delay",
                    "description": "CEO 재무 보고 지연 감지",
                    "delay_minutes": 15
                }
            }
        },
        # System Auditor → human 에스컬레이션
        {
            "message_id": "e5f6a7b8-c9d0-8123-ef01-234567890123",
            "sender": "system_auditor",
            "receiver": "human",
            "type": "escalation",
            "timestamp": "2026-05-11T07:00:00+09:00",
            "payload": {
                "urgency": "high",
                "body": {
                    "issue": "Hermes API 5회 연속 타임아웃",
                    "affected": ["ceo:C_001", "cfo:C_001"]
                },
                "attachments": [
                    {"name": "error_log", "content": {"count": 5, "last_error": "timeout"}}
                ]
            }
        },
        # System CFO → Board 포트폴리오 리뷰
        {
            "message_id": "f6a7b8c9-d0e1-9234-ef01-234567890123",
            "sender": "system_cfo",
            "receiver": "board",
            "type": "portfolio_review",
            "timestamp": "2026-05-11T08:00:00+09:00",
            "payload": {
                "urgency": "low",
                "body": {
                    "total_capital": 100000,
                    "companies": 1,
                    "recommendation": "Tier 0 유지"
                }
            }
        }
    ]

def run_tests():
    """TC-1.1.1 실행"""
    schema = load_schema()
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("TC-1.1.1: 모든 에이전트 유형이 동일 JSON 스키마 통과")
    print("=" * 60)
    
    valid_msgs = generate_test_messages()
    for i, msg in enumerate(valid_msgs):
        ok, errors = validate(msg, schema)
        if ok:
            print(f"  ✅ [{i+1}] {msg['sender']} → {msg['receiver']} ({msg['type']})")
            passed += 1
        else:
            print(f"  ❌ [{i+1}] {msg['sender']} → {msg['receiver']}: {errors[0]}")
            failed += 1
    
    print()
    print(f"결과: {passed} 통과, {failed} 실패 (총 {passed + failed}개)")
    return failed == 0

if __name__ == "__main__":
    # jsonschema 체크
    try:
        import jsonschema
    except ImportError:
        print("jsonschema 미설치 — pip install jsonschema 필요")
        sys.exit(1)
    
    success = run_tests()
    sys.exit(0 if success else 1)
