# Auto-Company-System (ACS) — 큰 그림 설계

> AI 에이전트가 자율적으로 회사를 창업·운영·Exit하는 시스템.
> MVF → Exit/Human CEO 전환 → 재투자 루프.

---

## 1. 전체 계층 구조

```
위진수 (Meta-level) ← 절대 승인 직접 처리 (HOTL 최상위)
  └── Human Interface Layer
        ├── 담당 Human (현재 = 위진수 / 추후 위임 가능)
        ├── Financial Gateway (위진수 명의 — 이중화 필요)
        │     위진수 투입: 회사 자본 + ACS 운영 예산 (별도 계정)
        ├── Exit Channel (위진수 승인 플랫폼 목록 — Board 참조)
        └── Auto-Company-System
              ├── System Auditor  ← Hermes 외부 감시 담당 (독립 실행)
              ├── Board
              ├── System CFO Interface  ← Financial Gateway 접근 (읽기/수령만)
              ├── Company A
              │     ├── CEO Interface   ← Financial Gateway 직접 접근 불가
              │     ├── Company CFO Interface
              │     ├── Company Auditor (Board 직속 독립)
              │     └── Company state.md
              ├── Company B ...
              └── Hermes (Circuit Breaker 내장 — System Auditor가 외부 감시)
```

---

## 2. 구성 요소

### System Auditor
- Board, Hermes, 각 회사 전체 상태 감시 (거시적)
- Company Auditor 보고를 집계만 담당 (직접 감시 X)
- **Hermes 외부 감시 (Watchdog)**: Hermes와 독립 실행 — Hermes 장애 시 유일한 감지 주체
- state.md: 이상 목록 집계
- 확장성: 회사 N개가 돼도 집계 구조로 버팀

### Board
- CEO/CFO 생성·종료·승인·에스컬레이션
- 승인 큐: 우선순위 기반 처리
- CEO vs CFO 충돌 시 최종 중재자
- **포트폴리오 분산 규칙 적용**: System CFO 정의 기준으로 업종 배정 시 분산 규칙 적용 (동일 카테고리 상한선 등 — 수치는 세부 설계에서 확정)
- **Exit Channel 참조**: CEO 업종 배정 시 Exit Channel 요건 확인
- state.md: CEO 포인터 목록, 승인 큐, 업종 목록 (핵심 요약만)
- 상세 내역은 각 Company state.md에 보관

### System CFO Interface (AI → Human 전환 가능)
- 포트폴리오 전체 자본 관리
- **ACS 운영 예산 별도 계정 관리** (Hermes·Board·Auditor API 비용 — 회사 자본과 분리)
- Tier 0 수익이 운영 비용 커버 시점부터 위진수 투입 예산 자동 대체
- 자본 기반 Company 최대 수 상한선 계산
- Exit/Human CEO 전환 수익 수령 및 재투자
- 실패 임계값 감지 (논문 기반 공식 — 세부 단계에서 확정)
- CEO 성과 추적 → 은퇴 권고
- **포트폴리오 분산 기준 정의** → Board에 전달
- **Meta-Learning Loop**: 포트폴리오 회고 → 업종별 성공률/평균 회수 기간 갱신 → Board 업종 DB 자동 업데이트
- 포트폴리오 라운드마다 회고 작성
- state.md: 자본 현황, 상한선, 성과 추적, 회고 요약

### Company (N개 병렬)
각 Company 구성:
- **CEO Interface** (AI → Human 전환 가능)
- **Company CFO Interface** (AI → Human 전환 가능, 최초부터 존재)
- **Company Auditor** (Board 직속 독립 — CEO/CFO 목표 공유 금지)
- **Company state.md** (고객, 계약, 업종, 단계, 자산 — CEO/CFO 교체 시에도 유지)

### Hermes
- 모든 에이전트의 DeepSeek API 키 중앙 관리
- 에이전트별 모델 라우팅 (추후 차등 적용)
- Circuit Breaker: 장애 감지 → 해당 에이전트 격리 → 복구 후 재연결
- 컨텍스트 압축 담당

---

## 3. LLM 설정

| 현재 | 추후 |
|------|------|
| 모든 에이전트 → DeepSeek V4 Flash | 에이전트별 모델 차등 (Hermes 라우팅) |
| 단일 API 키 (Hermes 중앙 관리) | 자본 증가 시 고성능 모델 업그레이드 |

---

## 4. 자율성 체계

### Glasswing 5단계 × HOTL 매핑

| Glasswing | 자율 처리 | 담당 Human | 위진수 |
|-----------|---------|-----------|------|
| Stage 1 (Operator) | 낮음만 | 중간·높음 | 절대 승인 |
| Stage 2 (Collaborator) | 낮음 + 반복 중간 | 높음 | 절대 승인 |
| Stage 3 (Consultant) | 낮음 + 중간 | 높음만 | 절대 승인 |
| Stage 4 (Approver) | 낮음·중간·높음 | — | 절대 승인 |
| Stage 5 (Observer) | 낮음·중간·높음 | — | 절대 승인 |

- 절대 승인: Glasswing 단계 무관, 항상 위진수 직접
- 단계 상향: Board+CFO 분석 → 위진수 최종 승인

### HOTL (Human-on-the-Loop) 위급도 라우팅
```
낮음     → Board 자율 처리
중간     → 담당 Human 알림 + 타임아웃 → 자동 처리
높음     → 담당 Human 응답 필수 + 대기 모드
절대 승인 → 위진수 직접 (HOTL 최상위 — Glasswing 단계 무관)
```

### 절대 승인 목록 (Glasswing 단계 무관, 항상 위진수 승인)
- Exit (매각)
- Human CEO/CFO 전환
- Human CEO/CFO 자발적 퇴직
- 대규모 투자 (임계값 이상 — 세부 단계에서 확정)
- Human Manager 고용/해고
- 새 시스템 Bootstrap
- 시스템 전체 종료

---

## 5. 운영 루프

### 성공 루프
```
창업
  → CEO: 성향 랜덤 부여, 업종 선택 (Board 중복 체크)
  → Company CFO: System CFO에 초기 자금 결재
  → 실행 (내부 작업 자유 / 외부 액션 승인)
  → 성장 임계값 도달
       ↓
  System CFO: 업종 매각가능 여부 + 포트폴리오 전략 기반 A/B 권고
  → Board 검토 → 위진수 최종 결정 (절대 승인)
       ↓
  A) Exit (매각)          B) Human CEO 전환
  → CFO 수익 수령         → 회사 시스템 내 유지
  → 재투자                → CEO 인수인계 → 은퇴
       ↓                        ↓
  CEO 회고 작성           다음 창업 시작
  CFO 회고 작성
  다음 창업 시작
       ↓
  System CFO 포트폴리오 회고
  → 업종 DB 성공률/회수기간 갱신 (Meta-Learning)
  → Board 분산 규칙 재조정
```

### 실패 루프
```
실패 감지 (Company CFO → System CFO, 논문 기반 공식)
  → Company Auditor → System Auditor 집계
  → Board → 담당 Human 집계 보고서
  → 승인
       ↓
  동결 (타임아웃 대기) or 즉시 종료
  → CEO 회고 (실패 원인 분석)
  → CFO 회고 (재무 분석)
  → Company state.md 보존
  → 다음 창업 시작 (교훈 반영)
```

### 폐업 vs CEO 은퇴
| | CEO 은퇴 | 회사 폐업 |
|---|----------|----------|
| 트리거 | CEO 성과 (System CFO 추적) | 회사 재무 임계값 (Company CFO) |
| 회사 | 계속 운영 | 종료 |
| CEO | 은퇴 → 새 CEO 투입 | 종료 → 다음 창업 |
| CFO | 성과 기반 A or B 판단 | 종료 |
| 우선순위 | — | 폐업이 항상 우선 |

---

## 6. CEO/CFO 생명주기

### CEO
- 성향: 랜덤 부여 (장인형/해커형/분석가형 — 논문 기반)
- 업종: Board 중복 체크 후 선택
- state.md: 창업마다 새로 시작 (회고 요약만 반영)
- 회고: 자기 자신의 회고만 참조 (경험 격리 원칙 유지)
- 동일 Agent가 계속 운영 (경험 축적)
- 타 CEO 회고 원본 직접 접근 금지 (Board가 익명 패턴만 업종 DB에 반영)
- 연속 실패 N회 → System CFO 은퇴 권고 → 위진수 승인

### Company CFO
- 최초 창업부터 존재 (CEO가 CFO 겸직 X)
- 역할: 예산 관리, 비용 추적, System CFO 보고
- state.md: CEO와 별개로 관리
- 회고: 창업마다 재무 회고 작성
- CEO 은퇴 시: Company CFO 성과 기반으로 유지(B) or 교체(A) 판단

### 결정권 위계
```
사업 결정 → CEO 우선
재무 결정 → Company CFO 우선
충돌 시   → Board 최종 중재

System CFO > Company CFO (재무 관련 항상)
이의 시    → Board 에스컬레이션
```

---

## 7. State 관리

| 구성요소 | state.md 내용 |
|---------|-------------|
| System Auditor | 이상 목록 집계 |
| Board | CEO 포인터, 승인 큐, 업종 목록 |
| System CFO | 자본 현황, 상한선, 성과 추적, 회고 요약 |
| Company state.md | 고객, 계약, 업종, 단계, 자산 (CEO/CFO 교체 시 유지) |
| CEO state.md | 창업마다 새로 시작, 회고 요약 반영 |
| Company CFO state.md | 재무 이력, 회고 요약 |

---

## 8. 예외 처리

| 상황 | 처리 |
|------|------|
| DeepSeek API 다운 | Hermes 감지 → 위급도 판단 → 대기 모드 |
| Hermes 장애 | Circuit Breaker → 에이전트 격리 → 복구 후 재연결 |
| Financial Gateway 장애 | System CFO 감지 → 수익 수령 중단 → 위진수 긴급 알림 (이중화 필요) |
| 담당 Human 부재 | HOTL 위급도 라우팅 |
| 담당 Human 교체 | Board/CFO state.md → 온보딩 문서 자동 생성 |
| 자본 소진 | CFO 긴급 보고 → 위진수: 추가 투입 or 종료 |
| CEO 무한 실패 | CFO 추적 → 은퇴 권고 → 위진수 승인 |
| CEO 은퇴 + 폐업 동시 | 폐업 항상 우선 처리 |
| Company 만석 (상한선 도달) | 신규 CEO 생성 중단 → Board 대기 큐 → Exit/종료 발생 시 슬롯 자동 개방 → 재개 (위진수 승인 불필요) |

---

## 9. 시스템 시작/종료

### 시작 (Bootstrap)
```
위진수 → bootstrap.py (수동 1회)
  → Hermes → System Auditor → Board → System CFO 순으로 시작
  → 이후 자동 운영
```

### 종료 순서
```
1. 신규 CEO/CFO 생성 중단
2. 외부 액션 승인 중단
3. 진행 중인 외부 계약 → 위진수 판단
4. Human Manager 해고 → 위진수 직접
5. 각 CEO/CFO 회고 작성
6. System CFO 최종 정산 보고
7. Hermes → System Auditor 순으로 종료
```

---

## 10. 미래 확장

```
현재:
위진수 = 담당 Human (1인 겸직)
  └── Auto-Company-System
        절대 승인 + 일상 감독 모두 위진수 직접

추후 (위임 단계):
위진수 (Meta-level — 절대 승인만)
  └── 담당 Human (위임받은 별도 인물 — 일상 감독)
        └── Auto-Company-System

추후 (다중 ACS):
위진수 (Meta-level)
  ├── Human A → Auto-Company-System A
  ├── Human B → Auto-Company-System B
  └── Human C → Auto-Company-System C

표준 KPI 보고 형식으로 위진수에게 집계
위진수는 절대 승인 + 고수준 판단만
```

---

## 11. 구조적 리스크 대응 (논문 기반)

> 출처: MAST 2025 (Why Do Multi-Agent LLM Systems Fail?), LLM Hallucination Survey 2025, Federated Learning (McMahan et al., 2017)

### 리스크 1: 환각(Hallucination) — 금융 결정
```
문제: LLM은 금융 수치/시장 분석에서 높은 환각 발생률
대응:
  - 모든 재무 결정 → RAG 기반 실제 데이터 조회 후 판단
  - Company Auditor가 재무 계산 독립 검증
  - 추측 기반 결정 금지 (데이터 없으면 에스컬레이션)
```

### 리스크 2: 에이전트 간 정보 왜곡
```
문제: 멀티에이전트 시스템의 1순위 실패 원인 — 정보 흐름 단절
대응:
  - 에이전트 간 통신 표준 메시지 포맷 강제
  - 요약 금지, 원본 데이터 첨부 의무화
  - CEO → Board → System CFO 체인에서 원본 보존
```

### 리스크 3: CEO-Company CFO 담합
```
문제: 같은 목표 공유 에이전트들이 잘못된 방향으로 정렬
대응:
  - Company Auditor = Board 직속 독립 (CEO/CFO 목표 공유 금지)
  - Company Auditor 별도 평가 지표 부여
  - 실패 보고 지연/축소 감지 로직 포함
```

### 리스크 4: 성과 검증 벤치마크 부재
```
문제: 명확한 성공 기준 없으면 시스템 전체 방향성 상실
대응:
  - CEO 은퇴 조건 N회, 임계값 X% 등 → 세부 단계에서 논문 기반 확정 필수
  - KPI 없이 운영 시작 금지
```

---

## 12. 업종 시스템

### 철학: 자동 확장
> 자본이 쌓이면 System CFO가 자동으로 접근 가능 업종 범위를 재계산.
> 위진수 승인 불필요. 자동화가 이 프로젝트의 핵심 철학.

### 업종 속성 기반 필터링
```
각 업종 = {
  최소자본: 원,
  인력필요: bool,
  디지털: bool,
  규제: bool,
  매각가능: bool,       ← Exit 가능 여부 (불가능 업종은 Human CEO 전환만)
  위진수부담: 항목 (Tier 0만 해당),
  예상회수기간: 기간
}

System CFO: 가용 자본 변화 시
  → 최소자본 ≤ 가용자본 필터링
  → Board에 갱신 목록 전달 (자동)
Board: 갱신된 목록 안에서 CEO 업종 배정 (중복 체크)
```

### Tier 0 (부트스트랩)
```
최소자본: 0원
위진수부담: API 토큰만
특징: 자본 없이 시스템 시작 가능 (자가 부트스트랩)
예시: 프롬프트 판매, AI 콘텐츠 생성, 정보 중개, 자동화 스크립트
흐름: Tier 0 수익 → System CFO → 자본 누적 → 상위 업종 자동 개방
```

---

*세부 설계 (프롬프트, 공식, 임계값)는 별도 문서에서 논문 기반으로 확정*
