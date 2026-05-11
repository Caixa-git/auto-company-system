# ACS HOTL 라우팅 규칙 — 위급도 × 라우팅 대상

> Phase 1.1.3 — 에러/예외 메시지 포맷 + HOTL 위급도 매핑
> 스키마 버전: 1.0.0 | 기준 문서: `docs/message-schema.json`, `docs/message-catalog.md`

---

## 1. HOTL 4단계 정의

HOTL(Human Oversight Tier Level)은 ACS 에이전트가 처리할 수 없는 예외/에러 상황에서
인간 개입의 긴급도와 라우팅 대상을 결정하는 4단계 체계.

| 단계 | urgency 값 | 의미 | 처리 방식 |
|:----:|:----------:|:-----|:----------|
| 1 | `low` | 낮음 — 정보성 | Board 자율 처리, 보고만 전달 |
| 2 | `medium` | 중간 — 주의 필요 | 담당 Human(위진수) 알림 + 타임아웃 후 자동 처리 |
| 3 | `high` | 높음 — 즉시 대응 | 담당 Human 응답 필수, 응답 없으면 대기 |
| 4 | `absolute` | 절대 — 위진수 직접 | 위진수 직접 채널 (Glasswing 단계 무관, 절대 승인 항목만) |

---

## 2. 라우팅 규칙

### 2.1 기본 라우팅

| urgency | 발신 에이전트 | 수신 에이전트 | 타임아웃 | 타임아웃 시 처리 |
|:-------:|:-------------|:-------------|:--------:|:----------------|
| `low` | system_cfo, board, hermes | board | 없음 | — (자율 처리) |
| `medium` | system_auditor, company_auditor | human | 30분 | 자동 처리 (Board가 대신 결정) |
| `high` | system_auditor, company_auditor, system_cfo | human | 무제한 대기 | — (Human 응답 필수) |
| `absolute` | system_auditor | human | 1시간 | 자동 재알림 (3회), 이후 System Auditor 에스컬레이션 |

### 2.2 예외 규칙

- `absolute`는 **System Auditor만** 발신 가능
- `absolute` 메시지는 Glasswing 단계와 무관하게 **항상 위진수 직접 채널**로 라우팅
- `low` urgency 메시지는 Board가 자체 판단으로 처리 (Human 개입 불필요)
- `medium` 타임아웃(30분) 내 Human 무응답 시 Board가 자동 대리 결정

---

## 3. 에러 코드 체계

메시지 타입이 `error`인 경우 `payload.body.error_code` 필드에 다음 코드 사용.

### 3.1 에러 코드 범위표

| 범위 | 카테고리 | 설명 | 기본 urgency |
|:----:|:---------|:-----|:-----------:|
| ERR_0001–0999 | 메시지 포맷 오류 | 스키마 검증 실패, 필드 누락, 타입 불일치 | `low` |
| ERR_1000–1999 | API/통신 오류 | LLM API 타임아웃, 외부 API 실패, 네트워크 오류 | `medium` |
| ERR_2000–2999 | 내부 에이전트 오류 | state.md 갱신 실패, 메모리 부족, 컨텍스트 한도 초과 | `medium` |
| ERR_3000–3999 | 금융/자본 오류 | 자본 부족, 계정 접근 실패, 배분 오류 | `high` |
| ERR_9000–9999 | 시스템 치명적 오류 | System Auditor 다운, Hermes 연결 완전 손실, 데이터 정합성 붕괴 | `absolute` |

### 3.2 자주 사용되는 에러 코드

| 코드 | 이름 | 설명 | 수신 | 기본 urgency |
|:----:|:-----|:-----|:----:|:-----------:|
| ERR_0001 | SCHEMA_VALIDATION_FAILED | 스키마 검증 실패 | 발신자 | `low` |
| ERR_0002 | REQUIRED_FIELD_MISSING | 필수 필드 누락 | 발신자 | `low` |
| ERR_0003 | INVALID_MESSAGE_TYPE | 존재하지 않는 메시지 타입 | 발신자 | `low` |
| ERR_1001 | LLM_TIMEOUT | LLM API 응답 시간 초과 | 발신자 | `medium` |
| ERR_1002 | LLM_API_ERROR | LLM API 오류 반환 | 발신자 | `medium` |
| ERR_1003 | EXTERNAL_API_FAILED | 외부 API(금융, 등록 등) 실패 | 발신자 | `medium` |
| ERR_2001 | STATE_UPDATE_FAILED | state.md 갱신 충돌/실패 | 발신자 | `medium` |
| ERR_2002 | CONTEXT_LIMIT_EXCEEDED | 에이전트 컨텍스트 한도 초과 | 발신자 | `medium` |
| ERR_3001 | INSUFFICIENT_CAPITAL | 자본 부족으로 액션 불가 | 발신자 | `high` |
| ERR_3002 | ACCOUNT_ACCESS_DENIED | Financial Gateway 접근 거부 | 발신자 | `high` |
| ERR_9001 | SYSTEM_AUDITOR_DOWN | System Auditor 응답 없음 | human | `absolute` |
| ERR_9002 | HERMES_DISCONNECTED | Hermes API 완전 연결 손실 | human | `absolute` |
| ERR_9003 | DATA_INTEGRITY_BREACH | 중요 데이터 정합성 붕괴 감지 | human | `absolute` |

---

## 4. 에러 메시지 예시

### 4.1 일반 스키마 오류 (ERR_0001, urgency=low)

```json
{
  "sender": "hermes",
  "receiver": "ceo:C_001",
  "type": "error",
  "payload": {
    "urgency": "low",
    "body": {
      "error_code": "ERR_0001",
      "message": "스키마 검증 실패: 필수 필드 'message_id' 누락",
      "source": "hermes.validator.schema",
      "original_message": { "sender": "ceo:C_001" }
    }
  }
}
```

### 4.2 LLM 타임아웃 (ERR_1001, urgency=medium)

```json
{
  "sender": "hermes",
  "receiver": "ceo:C_001",
  "type": "error",
  "payload": {
    "urgency": "medium",
    "body": {
      "error_code": "ERR_1001",
      "message": "DeepSeek API 타임아웃 — 30초 초과 (재시도 3회 실패)",
      "source": "hermes.router.llm_call",
      "original_message": { "message_id": "abc-123" }
    }
  }
}
```

### 4.3 자본 부족 (ERR_3001, urgency=high)

```json
{
  "sender": "system_cfo",
  "receiver": "board",
  "type": "error",
  "payload": {
    "urgency": "high",
    "body": {
      "error_code": "ERR_3001",
      "message": "CEO(C_001) 창업 자본 부족: 필요 5,000,000원, 가용 2,000,000원",
      "source": "system_cfo.capital_management"
    }
  }
}
```

### 4.4 시스템 치명적 오류 (ERR_9001, urgency=absolute)

```json
{
  "sender": "system_auditor",
  "receiver": "human",
  "type": "error",
  "payload": {
    "urgency": "absolute",
    "body": {
      "error_code": "ERR_9001",
      "message": "System Auditor 하트비트 미수신 — Hermes 다운 상태에서도 System Auditor 단독 감지 실패",
      "source": "system_auditor.watchdog"
    },
    "attachments": [
      {
        "name": "heartbeat_log",
        "content": {
          "last_successful": "2026-05-11T06:00:00+09:00",
          "missed_count": 5
        }
      }
    ]
  }
}
```

---

## 5. 통신 매트릭스 (HOTL 반영)

| 발신 → 수신 | error (no urgency) | error (low) | error (medium) | error (high) | error (absolute) |
|:-----------|:------------------:|:-----------:|:--------------:|:------------:|:----------------:|
| → board | ✅ | ✅ | ✅ | ✅ | — |
| → system_cfo | ✅ | ✅ | ✅ | ✅ | — |
| → system_auditor | ✅ | ✅ | ✅ | ✅ | — |
| → human | — | — | ✅ (timeout auto) | ✅ (wait) | ✅ (direct) |
| → hermes | ✅ | ✅ | ✅ | ✅ | — |
| → ceo:C_N | ✅ | ✅ | — | — | — |
| → cfo:C_N | ✅ | ✅ | — | — | — |
| → company_auditor:C_N | ✅ | ✅ | — | — | — |

> **참고:** `human` 에이전트는 HOTL urgency가 있는 error만 수신 가능.
> `absolute`는 System Auditor만 발신 가능 (절대 승인 채널).
> Company 레벨 에이전트(CEO/CFO/Company Auditor)는 low urgency 이하의 error만 수신.
