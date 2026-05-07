---
name: memory-garden
description: Claude Code auto memory(MEMORY.md + 개별 엔트리 파일)를 주기적으로 정리합니다. 관계 그래프·confidence·근거 품질·dry-run·피드백 루프로 종료된 프로젝트·해소된 차단·반영 완료된 피드백·outdated 참조를 식별해 아카이브/삭제/갱신/통합/메타 게이트 통합하고, 인덱스 카테고리 그룹핑과 메모리 작성 단계 개선 제안까지 생성. 프로젝트 문서 정원(`/garden`)과 타겟이 다름(메모리 엔트리 전용).
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
effort: high
---

대상: **Claude Code auto memory 디렉터리** — 시스템 메시지의 `# auto memory` 섹션에 명시된 경로. 일반 형태는 `~/.claude/projects/{profile-slug}/memory/` 하위 `MEMORY.md` + 개별 `.md`.

few-shot 판정 예시: [`templates/examples.md`](./templates/examples.md) (Phase 3 판정 전 참조)

## 역할

Claude Code의 자동 메모리 시스템이 시간이 지나면 종료된 프로젝트 기록, 이미 규칙으로 반영된 피드백, 실체와 불일치하는 참조가 쌓인다. 이 스킬은 그런 엔트리를 **의미 비교로 판정**해 아카이브/삭제/갱신/통합하고, 작성 단계의 구조적 결함(근거 누락·과도 생성·늦은 반영)까지 역추적해 개선 신호를 낸다.

## 핵심 원칙

- **판정은 의미 비교**. grep은 후보 수집 보조, 확정 판정은 Read로 실제 상태 확인 후
- **판정 근거 = 구체 출처(`경로:줄 + 인용`) 필수**. 근거 품질 미달 → Stale 강등
- **각 판정에 confidence(High/Med/Low) 필수**. Low → Stale 강등
- **Stale 자동 처리 금지** (사용자 개별 확인). `user` 타입 갱신·삭제는 명백 근거 필수. 아카이브 수정 금지
- **Dry-run 필수**. Phase 6 실제 수정 전 diff 미리보기 + 사용자 승인

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| `.local.claude/` 프로젝트 문서(daily·meetings·customers·modules 등) 정리 | `/garden` | 다루지 않음 |
| `CLAUDE.md` 자동 로드 파일 최적화 | `/optimize-claude-md` | 다루지 않음 |
| daily/memo 문서의 미흡수 지식 수확 | `/absorb`, `/garden` | 다루지 않음 |
| 메모리 작성 지침 개정안 **반영** | `/optimize-claude-md` 또는 사용자 직접 편집 | 제안만, 반영 안 함 |
| **Claude Code auto memory 엔트리 정리·개선 제안** | **이 스킬** | 핵심 |

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| auto memory 디렉터리 | system-reminder `# auto memory` 경로 또는 `~/.claude/projects/{profile-slug}/memory/` | **필수** | 경로 탐지 실패 → 사용자에게 AskUser로 직접 확인 후 중단 |
| MEMORY.md 인덱스 | `{auto memory}/MEMORY.md` | **필수** | 인덱스 부재 시 Glob으로 파일 목록 복구 후 경고 |
| 개인 CLAUDE.md | `~/.claude/CLAUDE.md` | 선택 | 개인 지침 기반 Promoted 판정 생략 |
| 프로젝트 CLAUDE.md | `./CLAUDE.md` (현 작업 디렉터리) | 선택 | 프로젝트 지침 기반 Promoted 판정 생략 |
| 규칙 파일 | `~/.claude/rules/*.md`, `./rules/*.md` | 선택 | 규칙 반영 판정 생략 |
| 스킬 디렉터리 (feedback 주제 겹칠 때) | `~/.claude/skills/*/SKILL.md` | 선택 | 스킬 반영 판정 생략 |
| 프로젝트 상태 | `.local.claude/projects/{name}/STATUS.md` | 선택 | Completed 판정 시 Grep 기반 휴리스틱으로 대체 |
| 아카이브 이력 | `{auto memory}/_archive/**/*.md` | 선택 | 수명 분석 제외 |

## 실행 규칙

- 기본: 메인 문맥 일괄 처리. `Agent` 서브에이전트 위임 금지 — 판정 근거(경로·줄·인용)의 연속성·신뢰도가 서브에이전트 요약을 거치며 손실됨
- 경로는 POSIX 구분자(`/`) 표기. Windows 환경에서도 이 표기로 통일
- 흐름: Phase 1 스캔 → 1.5 인덱스 그룹핑 점검 → 2 관계 그래프 → 3 판정 → 4 교차 검증 → 5 보고 → 6 실행(dry-run) → 7 정합성+피드백

---

## Phase 1: 스캔 + 컨텍스트 로드

### 1-1. auto memory 경로 확정

1. 시스템 메시지 `# auto memory` 섹션에서 디렉터리 경로 추출
2. 없으면 `~/.claude/projects/` 하위에서 현 작업 디렉터리와 매칭되는 `{profile-slug}/memory/` 추정
3. 여전히 해소 안 되면 사용자에게 AskUser로 확인하고 중단

### 1-2. 메모리 수집 (단일 메시지 병렬)

> **[Opus 4.7 / 1M 활용]** 아래를 병렬 호출:
> - Read: `{auto memory}/MEMORY.md`
> - Glob: `{auto memory}/*.md` (`_archive/` 제외), `{auto memory}/_archive/**/*.md` (수명 분석용)
> - Bash: 각 파일 mtime 수집 (`stat` — Linux `-c '%Y %n'`, macOS `-f '%m %N'`)

개별 파일 Read는 Phase 3 판정 직전 필요분만 로드 (1M context 활용, 100개 이하면 전부 선로드 가능).

### 1-3. 판정 근거원 로드 (병렬)

- `./CLAUDE.md` (프로젝트)
- `~/.claude/CLAUDE.md` (개인)
- `~/.claude/rules/*.md`, `./rules/*.md`
- `~/.claude/skills/*/SKILL.md` 중 feedback 주제 겹치는 것만 (description 키워드 매칭)
- `.local.claude/projects/*/STATUS.md` (있을 시)
- 메모리 본문에서 언급된 경로·심볼은 Phase 3에서 필요분만 Read/Grep

### 1-4. type별 1차 분류

| type | 기본 정책 | 후보 판정 |
|------|----------|----------|
| `user` | 보수적 유지 | 환경 정보 낡음만 갱신 |
| `feedback` | 반영 여부 확인 | Promoted |
| `project` | 생명주기 연동 | Completed / Outdated |
| `reference` | 대상 존재 확인 | Outdated |

---

## Phase 1.5: 인덱스 그룹핑 점검 (선택)

MEMORY.md가 평탄 리스트로 자라면 가독성·발동률이 떨어진다. 임계 도달 시 카테고리 헤딩으로 그룹핑한다. 본문 변경 0건, 라인 재배치 + 헤딩 추가만.

### 1.5-1. 평탄 vs 그룹핑 판정

| 신호 | 조치 |
|------|------|
| MEMORY.md ≤ 100줄 또는 ≤ 40 엔트리 | 평탄 유지 (그룹핑 비용 > 효과) |
| MEMORY.md > 180줄 또는 > 80 엔트리 | 그룹핑 권장 |
| 이미 카테고리 그룹핑 적용됨 | 추가 엔트리의 카테고리 배치 점검만 |

### 1.5-2. 카테고리 골격 (사용자 정의)

구체 카테고리 라벨은 사용자 환경(역할·도메인)에 따라 결정한다. 일반 골격 축:

- **type 축**: `user` / `feedback` / `project` / `reference` (4 헤딩, 가장 단순. 시작 권장)
- **활성도 축**: 활성 / 정체 / 메타 게이트(★)
- **도메인 축**: 사용자가 직접 정의 (역할·고객사·프로젝트·주제 등)

축은 단독 또는 조합 사용. 첫 적용은 type 축 단독을 권장한다.

### 1.5-3. 메타 게이트 표지

- 같은 도메인 메모리들의 **진입점 역할 메모리**에는 frontmatter `meta_gate: true` 권장
- 인덱스(MEMORY.md)에서는 `★` 등 시각 표지로 구분
- Phase 3 Consolidate 판정 시 "이미 메타 게이트 존재" 신호로 활용

### 1.5-4. 그룹핑 원칙

- **본문 변경 금지** — MEMORY.md의 라인 재배치 + 카테고리 헤딩 추가만
- **빈 카테고리 허용 X** — 엔트리 0개인 헤딩은 두지 않음
- **합산 줄 수 ≤ 200 유지** — 카테고리 헤딩이 줄 수를 늘리므로 본 정리(Phase 6) 후 적용 권장

---

## Phase 2: 관계 그래프 구축

엔트리 간 관계를 먼저 파악해 Phase 3 판정 정확도를 끌어올린다. 1M context 이점 최대 활용.

### 2-1. 관계 탐지

각 엔트리 본문·description에서 **다른 엔트리 언급**을 식별 (파일명, 공통 주제, 동일 PR/이슈 번호, 날짜 연속성).

### 2-2. 관계 유형 분류

| 관계 | 정의 | 판정 힌트 |
|------|------|----------|
| **succession(선후)** | A가 B의 후속/갱신본 (예: PR 머지 단계별 메모리) | 구 엔트리 → Resolved/Completed 후보 |
| **containment(포함)** | A가 B를 부분집합으로 포함 (프로젝트 ↔ 그 내부 이슈) | 포함된 쪽 → Duplicate 후보 (상위 유지) |
| **contradiction(모순)** | A와 B가 상충하는 정보 | 양쪽 → Stale 또는 최신 기준 갱신 |
| **reference(참조)** | 한쪽이 다른 쪽을 인용하나 독립적 주장 | 둘 다 유지 가능. Phase 3 개별 판정 |

### 2-3. 그래프 출력

다음 형식으로 관계 맵을 메인 문맥에 유지:

```
{entry_A} --succession--> {entry_B}  (근거: ...)
{entry_C} --containment--> {entry_D} (근거: ...)
{entry_E} <--contradiction--> {entry_F}  (근거: ...)
```

Phase 3 판정 시 관계 힌트를 **우선 참고**하되, 힌트가 Phase 3 조건과 충돌하면 조건 우선.

---

## Phase 3: 판정

### 판정 절차 (엔트리마다)

1. **claim 추출** — 본문에서 사실·상태·경로·이름·날짜 단위로 분리 (예: "PR #297 머지 완료", "담당=역할명", "만료=YYYY-MM-DD")
2. **검증 경로 매핑** — 각 claim의 확인 대상 결정 (STATUS.md / 소스 경로·심볼 / CLAUDE.md 섹션 / 날짜 비교 등)
3. **관계 힌트 적용** — Phase 2 그래프에서 이 엔트리와 관련된 관계 확인
4. **현재 상태 확보** — Read/Grep으로 실제 상태 획득
5. **불일치 평가** — 전체 불일치 / 부분 불일치(claim 중 일부만) / 주변부 불일치(설명 정보만)
6. **판정 + confidence(High/Med/Low)** — Low → Stale 강등

판정 과정·근거 서술 방식은 [`templates/examples.md`](./templates/examples.md)의 few-shot 사례를 모범으로 삼는다.

### 판정 간 우선순위 (동시 적용 가능 시)

```
Completed > Resolved > Promoted > Consolidate > Duplicate > Outdated > Stale > Active
```

### 판정 조건표

| 판정 | 조건 | 근거 확인 |
|------|------|----------|
| Active | 현재 유효, confidence High | 기본값 |
| Completed | 프로젝트 종료 + 역사적 전환 | `.local.claude/projects/{name}/STATUS.md`의 "종료"/"completed"/"아카이브 가능" + 현재 의사결정 영향 없음 |
| Resolved | 차단·문제·만료 경고 해소 | 후속 처리 확인(일정/커밋/후속 메모리). Phase 2 succession 관계도 증거 |
| Outdated | 참조 경로·코드·상태 불일치 | claim vs 현재 상태 의미 비교. 경로·심볼은 Grep/Read로 실체 확인 |
| Promoted | feedback이 CLAUDE.md/rules/skills에 의미론적 반영 | 반영처 Read 후 의미 매칭 판정 (grep 0건이어도 다른 표현일 수 있음) |
| Consolidate | 같은 도메인 메모리 N건+ 누적, 메타 게이트 없음 | 같은 본질의 서로 다른 사실들이 분산. Duplicate(주장 동일)와 구분. N 권장 시작값=3, 환경에 따라 조정 |
| Duplicate | 다른 메모리와 주장·범위 실질 동일/포함 | 본문 의미 비교. Phase 2 containment 관계 활용. description 유사만으로 불충분 |
| Stale | 근거 부족 / confidence Low / 유효성 불확실 | 본질 변화 추적 실패 |

---

## Phase 4: 교차 검증

### 4-1. 판정 간 충돌 해소

1. Duplicate ∩ Outdated → 최신 상태 기준 병합
2. Promoted ∩ Active → Active 유지 + 본문에서 반영 부분만 제거(갱신)
3. Completed ∩ Resolved → Completed 우선
4. Consolidate ∩ Duplicate → Consolidate 우선 (메타 게이트 신규 + 하위 본문 유지로 정보 손실 0)
5. 판정 의존 관계 있으면 보고에 명시(실행 순서 포함)

### 4-2. 근거 품질 검증

각 판정의 근거 필드를 다음 기준으로 체크:

| 증상 | 조치 |
|------|------|
| 경로만 있고 인용 없음 | Stale 강등 |
| 경로 존재하지 않음 | Outdated로 재분류 |
| "시스템 상태 확인" 등 추상 서술 | Stale 강등 |
| 근거 0개 또는 "기본값"만 | Active 외 판정 금지 |
| confidence Low + 근거 희박 | Stale 강등 + 사용자 개별 확인 대상 |

### 4-3. 관계 그래프 검증

Phase 2 관계 힌트와 Phase 3 판정이 일치하는지 역검사:

- succession인데 구 엔트리가 Active로 남았으면 → 근거 재확인
- contradiction인데 둘 다 Active면 → Stale 강등 검토

---

## Phase 5: 보고 + 승인

템플릿: [`templates/report.md`](./templates/report.md)

- 판정 항목마다 **근거 컬럼 + confidence 컬럼 필수** (빈 값 금지)
- 관계 그래프 섹션 포함 (succession/containment/contradiction 건수)
- 진행 옵션: 전체 / 선택(번호) / 카테고리 한정 / 취소

---

## Phase 6: 실행

### 6-0. Dry-run 미리보기 (필수)

실제 수정 전 각 작업의 예상 diff를 보고:

- 아카이브: 원경로 → 새경로 (추가될 frontmatter 라인 포함)
- 삭제: 파일 경로 + 바이트 크기
- 갱신: Edit 전후 diff (unified format)
- 통합: 병합 본문 preview + 아카이브되는 쪽
- MEMORY.md 변경: 제거·수정·추가 라인 표시

사용자 "실행" / "수정"(번호 지정) / "취소" 응답 대기.

### 6-1. 판정별 동작

| 판정 | 동작 | 상세 |
|------|------|------|
| Completed | 아카이브 | `{auto memory}/_archive/YYYY-MM/` 이동 + 아래 frontmatter 추가 |
| Resolved, Promoted | 삭제 | Bash `rm`. 승인된 것만 |
| Outdated | 갱신 | Edit 부분 수정 + `description` 재확인 |
| Consolidate | 메타 게이트 신규 + 하위 유지 | 진입점 메모리 신규 작성. frontmatter `meta_gate: true` + 본문에 하위 메모리 목록·도메인 요약. 하위 N건 본문 유지(정보 손실 0). 인덱스에서 ★ 등 시각 표지 |
| Duplicate | 통합 | 한쪽 병합 → 다른 쪽 아카이브. 두 본문 검토 후 재작성 |

아카이브 frontmatter (기존 frontmatter에 추가):

```yaml
archived: YYYY-MM-DD
archive_reason: completed|resolved|promoted|duplicate
original_name: {원 파일명}
```

### 6-2. MEMORY.md 갱신

- 삭제·아카이브 라인 제거
- 통합 시 대표 엔트리 라인의 `description` 갱신
- Consolidate 시 메타 게이트 라인 신규 추가(★ 표지) + 하위 메모리 라인 유지
- 갱신(Outdated) 엔트리의 `description`이 frontmatter와 일치하는지 재확인

---

## Phase 7: 정합성 + 피드백 루프 + 완료 보고

### 7-1. 정합성 체크

- MEMORY.md 링크 → 실제 `{auto memory}/*.md` 존재 (죽은 링크 0)
- 고아 파일 0 (`{auto memory}/*.md` 중 MEMORY.md 미인덱싱)
- 아카이브 정상 이동
- frontmatter(`type`/`name`/`description`) 유효성
- MEMORY.md ≤ 200줄

자동 보정 가능(죽은 링크 제거, 고아 인덱싱)은 수정. 나머지는 보고.

### 7-2. 피드백 루프 분석

이번 실행의 판정 결과 + `_archive/` 누적 이력을 종합해 **메모리 작성 단계 개선 신호** 추출:

| 분석 항목 | 방법 | 개선 신호 |
|----------|------|----------|
| type별 판정 분포 | 이번 + 최근 아카이브에서 type × 판정 집계 | 특정 type이 Outdated/Stale 비율 높으면 작성 지침 문제 |
| 수명 분석 | 작성일 ~ 아카이브/삭제 시점 평균 | 평균 수명이 짧으면 과도 생성 / 길면 정리 주기 낮음 |
| 근거 품질 결함 빈도 | Phase 4-2 Stale 강등 원인 집계 | 특정 결함(인용 누락·추상 서술)이 반복되면 템플릿 강화 필요 |
| feedback 반영 속도 | 작성 → Promoted까지 평균 | 너무 길면 feedback 반영 체크 루틴 부재 |
| 관계 그래프 누락 | 단일 주제의 분산된 메모리 비율 | 높으면 작성 시 기존 메모리 검색 단계 부재 |
| Consolidate 후보 누락 | 같은 도메인 메모리 3건+ 있으나 메타 게이트(`meta_gate: true`) 없음 | 작성 시점 게이트 부재 신호. 새 메모리 추가 직전 grep 자가 점검 루틴 권장 |

신호가 있으면 개인 `~/.claude/CLAUDE.md`의 `# auto memory` 섹션 또는 메모리 작성 템플릿에 대한 **개정 제안**을 완료 보고에 첨부. **이 스킬은 제안만**, 수정은 `/optimize-claude-md` 또는 사용자 직접.

### 7-3. 완료 보고

템플릿: [`templates/completion-report.md`](./templates/completion-report.md)

필수 포함:
- 처리 결과 (작업 × 건수)
- MEMORY.md 크기 변화
- 정합성 체크 결과
- **피드백 루프 분석 결과 + 개정 제안** (해당 시)
- Stale 미결 건수

## 분량 임계

| 대상 | 임계 1 (알림) | 임계 2 (강제 정리) |
|------|:----------:|:--------------:|
| MEMORY.md 줄 수 | 180줄 | 200줄 — auto memory 규약 한계, 초과 시 200줄 이후 잘림 |
| 활성 개별 메모리 파일 수 | 80개 | 100개 초과 시 일괄 정리 권고 |
| 한 엔트리 본문 줄 수 | 60줄 | 100줄 초과 시 분할 또는 요약 권고 |

## 다음 스킬 연결

- 피드백 루프 분석에서 `~/.claude/CLAUDE.md` 개정 제안 발생 → `/optimize-claude-md` 또는 사용자 직접 편집
- `.local.claude/` 프로젝트 문서 정리가 함께 필요 → `/garden`
- Stale 미결 건이 장기 누적 → 사용자 직접 검토 후 재실행

## 제약조건

- 아카이브 파일(`_archive/**`) 수정 금지 — 역사 보존
- Stale 자동 처리 금지 — 사용자 개별 확인 대상
- `user` 타입 갱신·삭제는 명백 근거 필수 (환경 정보 낡음만 갱신 허용)
- Phase 6 Dry-run 미리보기 없이 실제 수정 금지
- 원본 메모리 파일을 Edit 할 때 frontmatter `type`/`name` 필드 변경 금지 (의미 변질 위험)
- 근거 = `경로:줄 + 인용` 형태 필수. 추상 서술("시스템 상태 확인" 등)은 Stale 강등
- 메모리 본문이 민감 정보(토큰·비밀번호·사번)를 포함하면 Phase 5 보고에 **경고 섹션** 추가 + 사용자 확인 후 수정

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[의존성 부재]** auto memory 디렉터리 경로 해석 실패
- 신호: system-reminder `# auto memory` 섹션 없음 + `~/.claude/projects/` 하위에 현 프로젝트 매칭 슬러그 부재
- 대응: 사용자에게 경로 직접 입력 요청 후 재시도. 응답 없으면 중단 (검증 불가능한 상태에서 수정 절대 금지)

**[데이터 결함]** MEMORY.md ↔ 개별 파일 죽은 링크 다수 (>10건)
- 신호: Phase 7-1 정합성 체크에서 인덱스 엔트리의 N개 이상이 실제 파일 없음
- 대응: 자동 보정(죽은 링크 제거)을 **사용자 승인 후** 일괄 적용. 원인 추정(수동 파일 삭제·경로 변경)을 보고에 포함

**[데이터 결함]** 관계 그래프에 contradiction 3건 이상
- 신호: Phase 2에서 상호 모순 엔트리 쌍이 다수 탐지됨
- 대응: 자동 판정 보류, Phase 5 보고서 상단 경고 + 사용자 개별 검토 요청. 모순 자체가 작성 단계 문제 신호이므로 Phase 7-2 개정 제안에 반드시 포함

**[사용자 개입 필요]** Stale 누적 (연속 2회 이상 실행에도 해소 안 됨)
- 신호: `_archive/` 이력 vs 현재 `Stale 미결` 목록 비교 시 같은 파일이 이전 실행에서도 Stale이었음
- 대응: "반복 Stale" 섹션 보고, 해당 엔트리 삭제 또는 근거 보강 중 선택 강제. 자동 반복 처리는 위험 (의도된 보존일 수 있음)

