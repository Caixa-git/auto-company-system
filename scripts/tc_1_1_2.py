#!/usr/bin/env python3
"""TC-1.1.2: 필드 누락/타입 불일치 메시지 거부 검증"""
import json, sys
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

def generate_error_messages():
    """TC-1.1.2용 에러 테스트 — 필드 누락/타입 불일치"""
    return [
        # 필드 누락: message_id 없음
        {
            "sender": "ceo:C_001",
            "receiver": "board",
            "type": "approval_request",
            "timestamp": "2026-05-11T06:00:00+09:00",
            "payload": {"body": {}}
        },
        # 타입 불일치: timestamp가 숫자
        {
            "message_id": "a1b2c3d4-e5f6-4789-8abc-def012345678",
            "sender": "ceo:C_001",
            "receiver": "board",
            "type": "approval_request",
            "timestamp": 1234567890,
            "payload": {"body": {}}
        },
        # 잘못된 sender 형식
        {
            "message_id": "a1b2c3d4-e5f6-4789-8abc-def012345678",
            "sender": "invalid_agent",
            "receiver": "board",
            "type": "approval_request",
            "timestamp": "2026-05-11T06:00:00+09:00",
            "payload": {"body": {}}
        },
        # 잘못된 type
        {
            "message_id": "a1b2c3d4-e5f6-4789-8abc-def012345678",
            "sender": "ceo:C_001",
            "receiver": "board",
            "type": "unknown_type",
            "timestamp": "2026-05-11T06:00:00+09:00",
            "payload": {"body": {}}
        }
    ]

def run():
    schema = load_schema()
    passed = 0
    failed = 0

    print("=" * 60)
    print("TC-1.1.2: 필드 누락/타입 불일치 메시지 거부")
    print("=" * 60)

    invalid_msgs = generate_error_messages()
    for i, msg in enumerate(invalid_msgs):
        ok, errors = validate(msg, schema)
        if not ok:
            print(f"  ✅ [{i+1}] 거부됨: {errors[0][:80]}...")
            passed += 1
        else:
            print(f"  ❌ [{i+1}] 통과됨 (실패): 누락 필드가 스키마 통과")
            failed += 1

    print()
    print(f"결과: {passed} 통과, {failed} 실패 (총 {passed + failed}개)")
    return failed == 0

if __name__ == "__main__":
    try:
        import jsonschema
    except ImportError:
        print("jsonschema 미설치 — pip install jsonschema 필요")
        sys.exit(1)
    sys.exit(0 if run() else 1)
