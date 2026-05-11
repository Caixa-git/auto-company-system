# ACS Message Catalog — 메시지 유형별 상세 정의

> Phase 1.1.2 — 유형별 body 구조 + 예시 메시지
> 스키마 버전: 1.0.0 | 기준 문서: `docs/message-schema.json`

---

## 1. financial_report — 재무 보고

**발신 → 수신:** `cfo:{company_id}` → `system_cfo`
**설명:** Company CFO가 System CFO에게 주기적/이상 발생 시 재무 현황 보고.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `revenue` | number | ✅ | 해당 기간 매출 (원) |
| `cost` | number | ✅ | 해당 기간 비용 (원) |
| `cash` | number | ✅ | 현재 보유 현금 (원) |
| `period` | string | ✅ | 보고 기간 (ISO 8601 기간 or "YYYY-MM-DD~YYYY-MM-DD") |
| `burn_rate` | number | | 월간 현금 소진율 (선택, 위험 상황 시 포함) |

### 예시

```json
{
  "message_id": "a1b2c3d4-e5f6-4789-8abc-def012345678",
  "sender": "cfo:C_001",
  "receiver": "system_cfo",
  "type": "financial_report",
  "timestamp": "2026-05-11T06:00:00+09:00",
  "payload": {
    "body": {
      "revenue": 150000,
      "cost": 50000,
      "cash": 500000,
      "period": "2026-05-01~2026-05-11"
    },
    "attachments": [
      { "name": "transaction_log", "content": { "count": 23, "items": [] } }
    ]
  }
}
```

---

## 2. anomaly_report — 이상 보고

**발신 → 수신:** `company_auditor:{company_id}` → `board`
**설명:** Company Auditor가 Board에게 CEO/CFO의 이상 징후를 직접 보고. CEO/CFO 경유 금지.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `type` | string | ✅ | 이상 유형 (`report_delay`, `data_mismatch`, `suspicious_tx`, `collusion_signal`) |
| `description` | string | ✅ | 구체적 이상 내용 |
| `severity` | string | | `warning` / `critical` (기본값: `warning`) |
| `evidence` | array | | 증거 데이터 목록 (attachments와 별도로 요약 가능한 증거) |

### 예시

```json
{
  "message_id": "b2c3d4e5-f6a7-5890-9bcd-ef0123456789",
  "sender": "company_auditor:C_001",
  "receiver": "board",
  "type": "anomaly_report",
  "timestamp": "2026-05-11T06:05:00+09:00",
  "payload": {
    "urgency": "medium",
    "body": {
      "type": "report_delay",
      "description": "CEO 재무 보고가 예정 시각보다 15분 지연됨",
      "severity": "warning"
    }
  }
}
```

---

## 3. approval_request — 승인 요청

**발신 → 수신:** `ceo:{company_id}` → `board` (또는 `system_cfo`)
**설명:** CEO가 Board에게 업종 선택, 자금 사용, 외부 액션 등에 대한 승인 요청.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `request_type` | string | ✅ | `industry_select`, `fund_use`, `external_action`, `hire_manager`, `exit` |
| `summary` | string | ✅ | 요청 내용 요약 (한 줄) |
| `details` | object | ✅ | 요청 상세 (type별로 구조 상이) |
| `justification` | string | | 요청 근거 (선택적) |

### 예시

```json
{
  "message_id": "c3d4e5f6-a7b8-6901-acde-f01234567890",
  "sender": "ceo:C_001",
  "receiver": "board",
  "type": "approval_request",
  "timestamp": "2026-05-11T06:00:00+09:00",
  "payload": {
    "body": {
      "request_type": "industry_select",
      "summary": "AI 콘텐츠 생성 업종 진입 요청",
      "details": {
        "industry": "AI 콘텐츠 생성",
        "tier": 0,
        "estimated_monthly_revenue": 300000,
        "estimated_time_to_exit_months": 6
      },
      "justification": "장인형 성향에 최적 — 완성도 높은 콘텐츠 제작 가능. Tier 0, 자본 0원."
    }
  }
}
```

---

## 4. escalation — 에스컬레이션

**발신 → 수신:** `system_auditor` → `human`
**설명:** System Auditor가 담당 Human(위진수)에게 긴급 상황 알림. **payload.urgency 필수** (medium/high/absolute).

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `issue` | string | ✅ | 문제 요약 |
| `affected` | array | ✅ | 영향 받은 에이전트 목록 |
| `impact` | string | | 영향도 설명 |
| `recommended_action` | string | | 권장 조치 |

### 예시

```json
{
  "message_id": "d4e5f6a7-b8c9-7012-bdef-012345678901",
  "sender": "system_auditor",
  "receiver": "human",
  "type": "escalation",
  "timestamp": "2026-05-11T07:00:00+09:00",
  "payload": {
    "urgency": "high",
    "body": {
      "issue": "Hermes API 5회 연속 타임아웃 — Circuit Breaker 발동 필요",
      "affected": ["ceo:C_001", "cfo:C_001", "company_auditor:C_001"],
      "impact": "CEO/CFO의 RAG 조회 불가, 재무 데이터 기반 의사결정 중단",
      "recommended_action": "Hermes 재시작 또는 API 키 교체"
    },
    "attachments": [
      { "name": "error_log", "content": { "count": 5, "last_error": "timeout", "first_error_at": "2026-05-11T06:55:00+09:00" } }
    ]
  }
}
```

---

## 5. retrospective — 회고

**발신 → 수신:** `ceo:{company_id}` 또는 `cfo:{company_id}` → `board`
**설명:** CEO/CFO가 Exit/실패 후 회고 작성. Reflexion 패턴 기반 (Shinn et al., 2023).

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `author_role` | string | ✅ | `ceo` 또는 `cfo` |
| `outcome` | string | ✅ | `exit` / `failure` / `retirement` |
| `lessons_learned` | array | ✅ | 교훈 목록 (최소 1개) |
| `key_decisions` | array | | 주요 의사결정 이력 |
| `data_summary` | object | | 기간/매출/비용/Exit 금액 요약 (CFO 필수) |

### 예시

```json
{
  "message_id": "e5f6a7b8-c9d0-8123-ef01-234567890123",
  "sender": "ceo:C_001",
  "receiver": "board",
  "type": "retrospective",
  "timestamp": "2026-05-11T18:00:00+09:00",
  "payload": {
    "body": {
      "author_role": "ceo",
      "outcome": "exit",
      "lessons_learned": [
        "초기 시장 검증에 2주를 썼어야 했는데 1주일 만에 시작한 게 아쉬움",
        "장인형 성향대로 완성도를 높인 것이 Exit 가치 상승에 기여"
      ],
      "key_decisions": [
        { "decision": "AI 콘텐츠 생성 업종 선택", "rationale": "장인형 성향에 최적" }
      ],
      "data_summary": {
        "period_months": 6,
        "total_revenue": 1800000,
        "exit_amount": 4500000
      }
    }
  }
}
```

---

## 6. portfolio_review — 포트폴리오 리뷰

**발신 → 수신:** `system_cfo` → `board`
**설명:** System CFO가 Board에게 포트폴리오 전체 현황 및 전략 권고.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `total_capital` | number | ✅ | 전체 가용 자본 (원) |
| `operating_budget` | number | ✅ | ACS 운영 예산 (원) |
| `companies` | number | ✅ | 현재 운영 중인 회사 수 |
| `recommendation` | string | ✅ | `maintain` / `expand` / `contract` |
| `details` | array | | 회사별 성과 요약 |

### 예시

```json
{
  "message_id": "f6a7b8c9-d0e1-9234-ef01-234567890123",
  "sender": "system_cfo",
  "receiver": "board",
  "type": "portfolio_review",
  "timestamp": "2026-05-11T08:00:00+09:00",
  "payload": {
    "urgency": "low",
    "body": {
      "total_capital": 10000000,
      "operating_budget": 2000000,
      "companies": 2,
      "recommendation": "expand",
      "details": [
        { "company_id": "C_001", "status": "active", "roi_pct": 15 },
        { "company_id": "C_002", "status": "active", "roi_pct": -5 }
      ]
    }
  }
}
```

---

## 7. heartbeat — 생존 신호

**발신 → 수신:** 모든 에이전트 → `system_auditor` (또는 Board)
**설명:** 각 에이전트가 정상 동작 중임을 알리는 주기적 신호.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `status` | string | ✅ | `alive` / `degraded` / `recovering` |
| `uptime_seconds` | number | ✅ | 마지막 시작 이후 경과 시간 |
| `last_action` | string | | 마지막 수행 작업 |

### 예시

```json
{
  "message_id": "a1b2c3d4-e5f6-4789-8abc-def012345679",
  "sender": "board",
  "receiver": "system_auditor",
  "type": "heartbeat",
  "timestamp": "2026-05-11T06:00:30+09:00",
  "payload": {
    "body": {
      "status": "alive",
      "uptime_seconds": 7200,
      "last_action": "approval_queue_process"
    }
  }
}
```

---

## 8. error — 오류

**발신 → 수신:** 모든 에이전트 → 발신자에 따라 가변
**설명:** 메시지 처리 실패, API 오류, 내부 오류 등. **payload.error_code 필수** (형식: `ERR_XXXX`).

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `error_code` | string | ✅ | `ERR_XXXX` 형식 (schema에서 패턴 강제) |
| `message` | string | ✅ | 사람이 읽을 수 있는 오류 설명 |
| `source` | string | ✅ | 오류 발생 지점 (에이전트명 or 모듈명) |
| `original_message` | object | | 오류를 발생시킨 원본 메시지 (디버깅용) |

### 에러 코드 범위

| 범위 | 의미 |
|:-----|:------|
| ERR_0001–0999 | 메시지 포맷/스키마 오류 |
| ERR_1000–1999 | API/통신 오류 |
| ERR_2000–2999 | 내부 에이전트 오류 |
| ERR_3000–3999 | 금융/자본 오류 |
| ERR_9000–9999 | 시스템 치명적 오류 |

### 예시

```json
{
  "message_id": "b2c3d4e5-f6a7-5890-9bcd-ef0123456790",
  "sender": "hermes",
  "receiver": "ceo:C_001",
  "type": "error",
  "timestamp": "2026-05-11T06:00:00+09:00",
  "payload": {
    "body": {
      "error_code": "ERR_1002",
      "message": "DeepSeek API 타임아웃 — 30초 초과",
      "source": "hermes.router.llm_call",
      "original_message": { "message_id": "..." }
    }
  }
}
```

---

## 9. command — 명령 / RAG 조회

**발신 → 수신:** 모든 에이전트 → `hermes`
**설명:** Hermes에게 RAG 데이터 조회, API 호출, 라우팅 등을 요청.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `command` | string | ✅ | `rag_query` / `api_call` / `route` / `context_compress` |
| `target` | string | ✅ | 조회 대상 (RAG: 데이터 소스명, API: 엔드포인트) |
| `params` | object | | 명령별 파라미터 |
| `response_required` | boolean | | 응답 필요 여부 (기본값: true) |

### 예시

```json
{
  "message_id": "c3d4e5f6-a7b8-6901-acde-f0123456791",
  "sender": "system_cfo",
  "receiver": "hermes",
  "type": "command",
  "timestamp": "2026-05-11T06:00:00+09:00",
  "payload": {
    "body": {
      "command": "rag_query",
      "target": "industry_db",
      "params": {
        "query": "Tier 0 AI 업종 평균 수익률",
        "filters": { "tier": 0, "category": "AI" }
      },
      "response_required": true
    }
  }
}
```

---

## 10. response — 응답

**발신 → 수신:** 요청 수신 에이전트 → 요청 발신 에이전트
**설명:** 모든 요청 타입에 대한 표준 응답. `payload.body.approved`, `payload.body.result` 등으로 구성.

### body 구조

| 필드 | 타입 | 필수 | 설명 |
|:-----|:----:|:----:|:------|
| `in_reply_to` | string | ✅ | 응답 대상 원본 메시지의 `message_id` |
| `status` | string | ✅ | `approved` / `rejected` / `processing` / `failed` |
| `summary` | string | ✅ | 응답 내용 요약 |
| `details` | object | | 응답 상세 (type별로 구조 상이) |
| `error` | object | | status=failed인 경우 오류 정보 |

### 예시 (승인)

```json
{
  "message_id": "d4e5f6a7-b8c9-7012-bdef-0123456792",
  "sender": "board",
  "receiver": "ceo:C_001",
  "type": "response",
  "timestamp": "2026-05-11T06:01:00+09:00",
  "payload": {
    "body": {
      "in_reply_to": "c3d4e5f6-a7b8-6901-acde-f01234567890",
      "status": "approved",
      "summary": "AI 콘텐츠 생성 업종 승인",
      "details": {
        "approved_industry": "AI 콘텐츠 생성",
        "conditions": ["월간 보고 필수", "3개월 후 첫 리뷰"]
      }
    }
  }
}
```

---

## 부록: 타입별 에이전트 통신 매트릭스

| 발신 ↓ / 수신 → | board | system_cfo | system_auditor | human | hermes | ceo | cfo | company_auditor |
|:----------------|:-----:|:----------:|:--------------:|:-----:|:-----:|:---:|:---:|:---------------:|
| **board** | — | — | heartbeat | — | — | response | — | — |
| **system_cfo** | portfolio_review | — | heartbeat | escalation | command | — | — | — |
| **system_auditor** | heartbeat | heartbeat | — | **escalation** | — | — | — | — |
| **human** | (추후) | (추후) | — | — | — | — | — | — |
| **hermes** | heartbeat | heartbeat | heartbeat | — | — | response | response | — |
| **ceo** | approval_request | — | heartbeat | — | command | — | — | — |
| **cfo** | — | financial_report | heartbeat | — | command | — | — | — |
| **company_auditor** | **anomaly_report** | — | heartbeat(사본) | — | — | — | — | — |

> **범례:** — = 해당 쌍의 직접 통신 없음 (Board/System Auditor 경유)
> heartbeat과 error는 모든 에이전트가 모든 수신자에게 발신 가능
