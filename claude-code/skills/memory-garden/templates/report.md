# /memory-garden 진단 보고서 템플릿

> Phase 5 보고 단계에서 이 구조로 사용자에게 제시한다. 값은 실제 진단 결과로 치환.

## 🧠 /memory-garden 보고서 — YYYY-MM-DD

### 현황

| 구분 | 개수 | 줄 수 |
|------|------|------|
| MEMORY.md 인덱스 | N | N |
| 개별 메모리 파일 | N | N |
| 아카이브 기존 | N | — |

### 유효성 진단 결과

| 판정 | 개수 | 평균 confidence |
|------|------|---------------|
| Active (유지) | N | High/Med |
| Completed (아카이브) | N | High/Med |
| Resolved (삭제) | N | High/Med |
| Outdated (갱신 or 삭제) | N | High/Med |
| Promoted (삭제) | N | High/Med |
| Consolidate (메타 게이트 + 하위 유지) | N | High/Med |
| Duplicate (통합) | N | High/Med |
| Stale (사용자 확인) | N | Low |

### Completed — 아카이브 후보 (N건)

| # | 파일 | confidence | 근거 (구체 출처) |
|---|------|-----------|----------------|
| 1 | project_alpha_analysis.md | High | `.local.claude/projects/project-alpha/STATUS.md:12` "종료 2026-04-16" |

### Resolved — 삭제 후보 (N건)

| # | 파일 | confidence | 해소 근거 |
|---|------|-----------|----------|

### Outdated — 갱신 or 삭제 후보 (N건)

| # | 파일 | confidence | 불일치 내용 | 제안 |
|---|------|-----------|------------|------|

### Promoted — 규칙 반영 완료, 메모리 제거 (N건)

| # | 파일 | confidence | 반영처 (CLAUDE.md / rules / skills) |
|---|------|-----------|-----------------------------------|

### Consolidate — 메타 게이트 후보 (N건)

| # | 도메인 | 하위 메모리 (N건) | confidence | 권장 옵션 (A/B) |
|---|-------|----------------|-----------|--------------|

### Duplicate — 통합 후보 (N건)

| # | 병합 대상 2개 | confidence | 통합 방향 |
|---|-------------|-----------|---------|

### Stale — 사용자 확인 필요 (N건)

| # | 파일 | Low confidence 원인 | 현재 유효? |
|---|------|------------------|---------|

### 판정 간 의존 관계 (해당 시)

| 판정 A | 판정 B | 관계 | 실행 순서 |
|-------|-------|------|---------|

### 관계 그래프 요약 (Phase 2)

| 관계 유형 | 건수 | 대표 예시 |
|----------|------|---------|
| succession | N | {A} → {B} |
| containment | N | {A} ⊃ {B} |
| contradiction | N | {A} ⇄ {B} |
| reference | N | {A} → {B} |

### 근거 품질 검증 결과 (Phase 4-2)

| 증상 | 건수 | 조치 |
|------|------|------|
| 경로만 있고 인용 없음 | N | Stale 강등 |
| 경로 존재하지 않음 | N | Outdated 재분류 |
| 추상 서술 | N | Stale 강등 |

---

### 진행 옵션

- **전체 반영** — Completed 아카이브 + Resolved/Promoted 삭제 + Outdated 갱신 + Consolidate 메타 게이트 + Duplicate 통합
- **선택 반영** — 번호 지정 (예: `1,3,5`)
- **카테고리 한정** — 예: `Promoted만`
- **취소**

*승인 후 Phase 6 Dry-run 미리보기가 먼저 출력됩니다. 실제 파일 변경은 Dry-run 확인 후에만 수행.*
