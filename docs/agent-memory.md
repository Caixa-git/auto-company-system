# ACS 에이전트 메모리 아키텍처

> Phase 1.4 — 계층적 메모리 관리, 컨텍스트 한도 처리, 회고 → 재창업 반영
> **논문 근거:** MemGPT (Packer et al., 2023), Reflexion (Shinn et al., 2023)

---

## 1. 메모리 계층 구조

각 에이전트는 3계층 메모리:

```
Layer 1: 메인 컨텍스트 (현재 세션, ~8K 토큰)
Layer 2: state.md (영구 상태, Hermes와 독립 접근)
Layer 3: 회고 아카이브 (장기 저장, Exit/실패 시 기록)
```

| 구성 요소 | Layer 1 | Layer 2 (state.md) | Layer 3 (아카이브) |
|:---------|:--------|:-------------------|:------------------|
| CEO | 성향, 현재 업종, 최근 결정 | 고객, 계약, 자산, 단계 | 회고 요약 (익명) |
| Company CFO | 최근 재무, 예산 | 재무 이력, 비용 | 회고 요약 |
| Board | 승인 큐 상위 | CEO 포인터, 업종 목록 | 업종 DB (익명 패턴) |
| System CFO | 자본 현황, 최근 보고 | 자본, 성과, 임계값 | 포트폴리오 회고 |
| System Auditor | 최근 이상, Hermes 상태 | 이상 목록, Watchdog | 감사 로그 |

---

## 2. 컨텍스트 한도 초과 처리

| 사용률 | 액션 |
|:------|:------|
| 70% | 경고 로그 |
| 85% | 사전 압축 (오래된 메시지 배치 요약) |
| 95% | 긴급 압축 (state.md 외 대화 이력 요약) |
| 100%+ | state.md 보존 후 세션 초기화 |

압축 전략: Batch Summarize / Drop Resolved / Archive State / Session Reset

**압축 후 state.md 핵심 수치 100% 보존 필수**

---

## 3. 회고 파이프라인 (Reflexion)

회고 트리거: Exit 성공 / 실패/폐업 / CEO 은퇴 / Human CEO 전환 / 포트폴리오 리뷰

### CEO 회고 형식
```json
{
  "outcome": "exit | failure | retirement",
  "company_id": "C_001",
  "period_months": 6,
  "total_revenue": 1800000,
  "total_cost": 500000,
  "exit_amount": 4500000,
  "lessons_learned": ["..."],
  "trait_reflection": "장인형→초기 속도 느림, 품질 좋음"
}
```

### 익명화 파이프라인
```
CEO 회고 → Board 수신 → 식별자 마스킹 → 익명 패턴 추출 → 업종 DB 갱신
```

### 회고 미완료 시
```
CEO 종료 시도 → 회고 미완료 감지 → Board가 완료 요청 → 완료 전 종료 차단
```

---

## 4. 멀티 프로필 메모리 구성

```
~/.hermes/profiles/
├── acs-core/       (System Auditor + Bootstrap)
├── acs-board/      (승인 큐, 업종 목록)
├── acs-cfo/        (자본, 성과, KPI)
└── acs-ceo-C_001/  (성향, 회고, company-state.md)
```

### 에이전트 간 통신
```
공유 메시지 큐: ~/acs/messages/{component}/inbox/*.json
```

---

## 5. 버전 정보

| 항목 | 내용 |
|:-----|:------|
| 문서 버전 | 1.0.0 |
| 적용 Phase | 1.4 |
