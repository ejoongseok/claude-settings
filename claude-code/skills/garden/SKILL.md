---
name: garden
description: ".local.claude/ 문서 정원 관리: 만료 문서 식별, 미반영 지식 수확, 아카이브, INDEX 갱신을 단일 명령으로 수행합니다. 문서가 쌓이거나 정리가 필요할 때 사용하세요."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
effort: high
disable-model-invocation: true
---

`.local.claude/` 하위 문서의 수명을 관리합니다.
만료된 문서에서 미반영 지식을 수확(harvest)하여 영구 문서에 반영하고, 원본을 아카이브로 이동합니다.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 대상 디렉터리 | `.local.claude/` 전체 | **필수** | "정원 관리 대상 없음" |
| frontmatter | 각 파일 상단 | 선택 | 경로 기반 추론 fallback |
| absorb-log | `.local.claude/docs/absorb-log.md` | 선택 | 미흡수 감지 생략 |

## 전체 흐름

Phase 1 스캔에서 시작해 Phase 2 만료 식별, Phase 3 수확 점검, Phase 4 보고 + 승인, Phase 5 실행 + INDEX 갱신 순으로 진행한다.

---

## Phase 1: 스캔

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**하여 컨텍스트 효율화:
> - Glob 병렬: `.local.claude/**/*.md` (archive 제외), 카테고리별 경로 패턴(`daily/*.md`, `meetings/*.md`, `customers/*.md`, `modules/*.md`, `projects/**/STATUS.md` 등) 동시 수집
> - Bash: mtime 수집(`find ... -printf "%T@ %p\n"` 또는 `stat`), 파일 수와 줄 수 집계(`wc -l`) 를 카테고리별로 동시 실행
> - Read: `CLAUDE.md`, `.local.claude/INDEX.md`, `.local.claude/docs/absorb-log.md`, 자동 로드 후보(biz-rules.md, customers/*.md, modules/*.md) 분량 임계 검사용 병렬 로드
>
> 순차 호출 대신 병렬 호출로 네트워크 왕복 감소 + 전체 정원 상태가 동시에 컨텍스트에 로드되어 Phase 2 만료 식별 + Phase 3 수확 매핑이 한 번에 계산 가능.

`.local.claude/` 전체 .md 파일을 수집한다. **archive/ 하위는 제외.**

```bash
find .local.claude/ -name "*.md" -not -path "*/archive/*" -printf "%T@ %Td/%Tm/%TY %p\n" 2>/dev/null | sort -rn
```

Windows 환경에서는:
```bash
find .local.claude/ -name "*.md" -not -path "*/archive/*" | while read f; do echo "$(stat -c '%Y %n' "$f" 2>/dev/null || stat -f '%m %N' "$f" 2>/dev/null)"; done | sort -rn
```

또는 Glob + Bash stat 조합으로 수집.

### 카테고리 분류 (경로 패턴 기반)

| 경로 패턴 | 카테고리 | 유형 |
|-----------|---------|------|
| `modules/*.md` (TEMPLATE/TODO/PLAN 제외) | modules | 영구 |
| `fe-guide/*.md` | fe-guide | 영구 |
| `be-guide/*.md` | be-guide | 영구 |
| `customers/*.md` | customers | 영구 |
| `ddl/*.md` | ddl | 영구 |
| `pmd/*` | pmd | 영구 |
| `biz-rules*.md`, `ONBOARDING*.md`, `INFRASTRUCTURE*.md` | core-ref | 영구 |
| `SKILLS-GUIDE.md`, `team.md` | reference | 영구 |
| `people/*.md` | people | 영구 |
| `adr/*.md` | adr | 영구 |
| `daily/*.md` | daily | 시간 한정 |
| `daily-todos/*.md` | daily-todos | 시간 한정 |
| `briefing/*.md` | briefing | 시간 한정 |
| `meetings/*.md` | meetings | 시간 한정 |
| `memo/*.md` | memo | 시간 한정 |
| `draft/*.md` | draft | 시간 한정 |
| `learn/*.md` | learn | 시간 한정 |
| `leadership/*.md` (config.md 제외) | leadership | 시간 한정 |
| `reports/*.md` | reports | 시간 한정 |
| `coaching/*.md` | coaching | 시간 한정 |
| `cs/*.md` | cs | 시간 한정 |
| `issues/*.md` | issues | 시간 한정 |
| `prs/*.md` | prs | 시간 한정 |
| `deploys/*.md` | deploys | 시간 한정 |
| `convention-audit/*.md` | convention-audit | 시간 한정 |
| `review/*.md` | review | 시간 한정 |
| `brainstorm/*.md` | brainstorm | 시간 한정 |
| `projects/*/STATUS.md` | project-status | 프로젝트 |
| `projects/**/*.md` (STATUS 외) | project-docs | 프로젝트 |
| `docs/parsed/**` | docs-parsed | 즉시 아카이브 |
| `docs/original/**` | docs-original | 즉시 아카이브 |

frontmatter에 `category`, `retention`이 있으면 그것을 우선 사용한다.

각 카테고리별 파일 수와 줄 수를 집계한다.

---

## Phase 2: 만료 식별

오늘 날짜 기준으로 카테고리별 보존 기간을 적용한다.

### 보존 정책

| 카테고리 | 보존 기간 | 만료 조건 |
|---------|----------|----------|
| daily | 14일 | 수정일 < 오늘 - 14일 |
| daily-todos | 14일 | 수정일 < 오늘 - 14일 |
| memo | 14일 | 수정일 < 오늘 - 14일 |
| draft | 14일 | 수정일 < 오늘 - 14일 |
| briefing | 30일 | 수정일 < 오늘 - 30일 |
| meetings | 30일 | 수정일 < 오늘 - 30일 |
| learn | 30일 | 수정일 < 오늘 - 30일 |
| leadership | 30일 | 수정일 < 오늘 - 30일 (config.md 제외) |
| reports | 30일 | 수정일 < 오늘 - 30일 |
| coaching | 30일 | 수정일 < 오늘 - 30일 |
| cs | 30일 | 수정일 < 오늘 - 30일 |
| issues | 30일 | 수정일 < 오늘 - 30일 |
| prs | 30일 | 수정일 < 오늘 - 30일 |
| deploys | 30일 | 수정일 < 오늘 - 30일 |
| convention-audit | 30일 | 수정일 < 오늘 - 30일 (changelog.md 제외) |
| review | 30일 | 수정일 < 오늘 - 30일 |
| brainstorm | 30일 | 수정일 < 오늘 - 30일 |
| project-docs | 프로젝트 종료 시 | STATUS.md에 "종료"/"completed" 표기 + 7일 |
| project-status | 프로젝트 종료 시 | 동일 |
| docs-parsed | 흡수 확인 후 | absorb-log.md에서 흡수 완료 확인 시 만료. 미흡수면 `/absorb 먼저?` 안내 |
| docs-original | 즉시 | 항상 만료 후보 |
| 영구 (modules, guides 등) | 없음 | 아카이브 대상 아님 |
| adr | 없음 | 아카이브 대상 아님 (아키텍처 결정 영구 보존) |
| people | 없음 | 아카이브 대상 아님 (팀원 프로필 영구 보존) |

frontmatter에 `retention`이 있으면 그것을 우선 사용한다.
예: `retention: permanent`는 만료 없음, `retention: 7d`는 7일.

만료 파일 목록을 생성한다.

---

## Phase 3: 수확 점검 (Harvest Check)

만료 파일에서 영구 문서에 아직 반영되지 않은 지식을 추출한다.

### 수확 대상 매핑

| 소스 카테고리 | 추출할 정보 | 반영처 | 수확 방법 |
|-------------|-----------|-------|----------|
| daily | 버그/상태전이 발견 | biz-rules.md | "버그", "발견", "상태 코드", "상태 전이" 탐색 |
| daily | 모듈 동작 발견 | modules/*.md | "알게 됨", "확인됨", 모듈명 |
| daily | 교훈/인사이트 | auto memory | "앞으로는", "다음부터", "교훈" |
| meetings | 결정 사항 | biz-rules.md | "결정", "합의", "확정" |
| meetings | 고객 요구 | customers/*.md | 고객사명 + "요구", "요청", "Pain" |
| meetings | 조직 변경 | auto memory (team.md) | "담당", "프로세스", "조직" |
| briefing | 미반영 biz-rules | biz-rules.md | briefing 스킬이 이미 부분 반영, 누락 확인 |
| briefing | 미반영 모듈 변경 | modules/*.md | briefing 스킬 갱신 기록 확인 |
| learn | 학습 결과 | 반영 대상 문서 | "반영 완료" 표기 확인 |
| coaching | 성장 기록 | people/*.md | 피드백 패턴, 성장 영역 |
| cs | 고객 이슈 패턴 | customers/*.md | 고객사명 + 이슈 유형 |
| reports | 분석 결과 | biz-rules.md, modules/*.md | 인사이트/제안 섹션 |
| project STATUS | 프로젝트 교훈 | modules/*.md, auto memory | "교훈", "회고", "결론" 섹션 |
| daily-todos | (수확 불필요) | 없음 | 작업 목록뿐, 스킵 |
| memo | 미승격 메모 | 사용자에게 질문 | /learn, /customer-profile 등으로 승격 여부 |
| draft | (수확 불필요) | 없음 | 발신 콘텐츠, 스킵 |
| issues, prs | (수확 불필요) | 없음 | GitHub에 원본, 스킵 |
| docs-parsed | `/absorb` 스킬로 처리 | 없음 | `absorb-log.md` 확인: 흡수 완료면 아카이브, 미흡수면 `/absorb {path}` 안내 |
| docs-original | (수확 불필요) | 없음 | 바이너리, 스킵 |

### 수확 실행 방법

> **[1M 활용]** 서브에이전트 분할 대신(또는 병행하여) 메인에서 직접 **다중 파일 동시 Read** 후 교차 분석:
> - 로드: 만료 소스 파일(daily/*, meetings/*, learn/*, reports/*, cs/*, memo/*) 과 반영처 sink 문서(biz-rules.md, modules/*.md, customers/*.md, team.md, people/*.md, INFRASTRUCTURE.md) 를 **동시에** 로드
> - 교차 분석: {소스의 추출 후보} vs {sink 의 기존 내용}. 이미 반영된 것(SKIP) / 미반영 신규(NEW) / 기존 보강(ENRICH) / 모순(CONFLICT) 한 번에 분류
> - 서브에이전트 병렬 위임은 만료 파일 20개+ 또는 총 로드 추정 토큰 ~600K(1M 컨텍스트의 60%; 줄 수로 대략 가늠) 근접 시로 보류. 1M context 내면 메인에서 한꺼번에 처리가 더 정확(소스-싱크 교차 정확도 증가).

만료 파일이 **10개 이상**이면 서브에이전트에 병렬 위임한다:

```
Agent A: daily/*.md + daily-todos/*.md 수확 점검
Agent B: meetings/*.md + briefing/*.md + coaching/*.md 수확 점검
Agent C: learn/*.md + reports/*.md + cs/*.md + memo/*.md 수확 점검
```

각 서브에이전트는:
1. 만료 대상 파일을 Read
2. "수확 대상 매핑" 표의 추출 패턴으로 후보 정보 추출
3. 반영처 문서를 Read하여 이미 반영됐는지 대조
4. **미반영 항목만** 리턴 (소스 파일, 추출 내용, 반영 대상, 반영 위치 제안)

만료 파일이 **10개 미만**이면 메인에서 직접 처리한다.

**docs/ (parsed+original)** 은 수확 없이 즉시 아카이브 대상으로 분류. 파일 수만 집계.

### 분량 임계 검사 (자동 로드 문서 비대 방지)

수확 점검과 별도로, 자동 로드 후보 문서가 임계를 초과했는지 검사한다.

| 대상 파일 | 임계 (줄 수) | 초과 시 안내 스킬 |
|----------|:-----------:|----------------|
| `CLAUDE.md` (자동 로드) | 200 | `/optimize-claude-md` |
| `.local.claude/biz-rules.md` (자동 로드 후보) | 200/400 | `/biz-rules` (분리 가이드) |
| `human/SETUP.md` | 300/500 | `/setup-guide` (분리 가이드) |
| `.local.claude/customers/*.md` | 300/500 | `/customer-profile` (분리 가이드) |
| `.local.claude/modules/*.md` | 300 | 사용자 결정 (큰 모듈은 sub-doc 분리 권장) |
| `bot/*.md` | 150 | `/dualize-docs` 또는 `/on-boarding --refresh` |

검사 결과는 Phase 4 보고서 "분량 초과 알림" 섹션에 표시. 강제 분리하지 않고 사용자에게 안내만.

---

## Phase 4: 보고 + 승인

사용자에게 다음 형식으로 보고한다:

```markdown
## /garden 보고서: YYYY-MM-DD

### 현황
| 구분 | 파일 수 | 줄 수 |
|------|--------|------|
| 전체 (.local.claude/) | N | N |
| 영구 참조 | N | N |
| 시간 한정 (활성) | N | N |
| 만료 대상 | N | N |
| 아카이브 기존 | N | N |

### 수확 결과 (반영 필요 N건)
| # | 소스 | 내용 요약 | 반영 대상 | 반영 위치 |
|---|------|----------|----------|----------|
| 1 | daily/YYYY-MM-DD | (예시: 도메인 상태 전이 발견) | biz-rules.md | "해당 상태" 절 |

### 이미 반영된 것 (확인 완료 N건)
| # | 소스 | 내용 | 반영된 곳 |
|---|------|------|----------|

### 승격 질문 (memo N건)
| # | 메모 | 제안 승격 대상 |
|---|------|--------------|

### 미흡수 문서 (docs-parsed)
(absorb-log.md 확인 결과)
- 흡수 완료 N건: 아카이브 가능
- **미흡수 N건**: `/absorb {path}` 먼저 실행 권장

### 분량 초과 알림 (자동 로드 부담 / 비대 위험)
| 파일 | 현재 | 임계 | 권장 조치 |
|------|:----:|:----:|----------|
| (해당 시만 채움) | | | |

임계 초과 0건이면 섹션 통째 생략.

### 아카이브 대상 (N건)
| 카테고리 | 파일 수 | 예시 |
|---------|--------|------|
| daily (14일 초과) | N | 2026-04-02.md |
| docs/parsed (흡수 완료분) | N | weekly/*.md |

### 영구 참조 (변경 없음)
modules/, fe-guide/, be-guide/, customers/, ddl/, people/, adr/ (아카이브 제외)

---
진행하시겠습니까?
- 전체 진행
- 특정 항목 제외 (번호 지정)
- 수확만 (아카이브 안 함)
- 아카이브만 (수확 안 함)
```

---

## Phase 5: 실행

사용자 승인 후 실행한다.

### 5-1. 수확 반영

미반영 항목을 영구 문서에 반영한다:
- **biz-rules.md**: "변경 이력" 테이블에 `| YYYY-MM-DD | garden 수확: {내용} | {소스} |` 추가
- **modules/*.md**: 해당 섹션에 항목 추가
- **customers/*.md**: 해당 고객사 파일에 추가
- **auto memory**: 해당 메모리 파일 생성 또는 업데이트

반영 시 반드시 Read 후 Edit 순서로 최신 상태 확인 후 수정.

### 5-2. 아카이브 이동

만료 파일을 `archive/` 하위로 이동한다.

**아카이브 디렉터리 구조:**
```
.local.claude/archive/
  YYYY-MM/                    ← 시간 한정 문서 (월별 그룹)
    daily/
    daily-todos/
    briefing/
    meetings/
    memo/
    draft/
    learn/
    leadership/
    reports/
    coaching/
    cs/
    issues/
    prs/
  projects/                   ← 종료된 프로젝트 (이름으로 그룹)
    {project-name}/
  docs/                       ← 외부 문서 (유형별)
    parsed/
    original/
```

**이동 절차:**
1. 아카이브 디렉터리 생성: `mkdir -p .local.claude/archive/{path}`
2. 파일에 frontmatter 추가 (또는 갱신):
   ```yaml
   ---
   archived: YYYY-MM-DD
   harvested_to:
     - biz-rules.md {반영 섹션} 섹션
     - modules/{name}.md {반영 섹션} 섹션
   original_path: {원래 상대 경로}
   ---
   ```
3. 파일을 Write로 아카이브 경로에 작성
4. 원본을 Bash `rm`으로 삭제

수확 불필요 카테고리(daily-todos, draft, issues, prs, docs)는 frontmatter의 `harvested_to`를 비워둔다.

### 5-3. INDEX.md 갱신

`.local.claude/INDEX.md`를 현재 상태로 갱신한다.
INDEX.md 구조와 갱신 방법은 아래 "INDEX.md 관리" 섹션 참조.

### 5-4. 완료 보고

```markdown
## /garden 완료: YYYY-MM-DD

### 수확 반영
- biz-rules.md: N건 추가
- modules/{name}.md: N건 추가
- customers/{name}.md: N건 추가

### 아카이브
- 이동: N건, archive/YYYY-MM/ 으로
- docs: N건, archive/docs/ 으로

### 현재 활성 문서: N개 (아카이브 전 N개에서 N개로 감소)

### 다음 만료 예정
| 파일 | 만료일 | 카테고리 |
|------|-------|---------|
```

---

## INDEX.md 관리

`/garden` 실행 시마다 `.local.claude/INDEX.md`를 갱신한다.

INDEX.md는 CLAUDE.md에서 `@.local.claude/INDEX.md`로 자동 로드된다.
**60줄 이내를 유지한다.** 파일명을 개별 나열하지 않고 카테고리별 요약만.

### INDEX.md 구조

```markdown
# .local.claude 문서 인덱스

> 자동 갱신: /garden. 수동 편집 금지.
> 마지막 갱신: YYYY-MM-DD
> archive/는 수확 완료된 문서 보관소. 이력 확인이 필요하면 archive/ 하위를 직접 탐색.

## 영구 참조
| 경로 | 파일 수 | 용도 |
|------|--------|------|
| modules/ | N | 모듈별 서비스, 테이블, 이벤트 분석 |
| be-guide/ | N | BE 코드 컨벤션 (코드 작성 시 필수) |
| fe-guide/ | N | FE 코드 컨벤션 (코드 작성 시 필수) |
| customers/ | N | 고객사별 특성과 요구사항 |
| people/ | N | 팀원 프로필 |
| adr/ | N | 아키텍처 결정 기록 |
| ddl/ | N | 테이블 컬럼 정의 |

## 활성 프로젝트
| 프로젝트 | 경로 | 최종 갱신 |
|---------|------|----------|
(projects/ 하위에서 STATUS.md에 "종료" 없는 것만)

## 시간 한정 (활성)
| 카테고리 | 경로 | 파일 수 | 보존 | 최신부터 최고령 |
|---------|------|--------|------|-------------|
(만료 안 된 시간 한정 파일만)

## 다음 만료 예정 (최대 5건)
| 파일 | 만료일 | 카테고리 |
|------|-------|---------|

## 아카이브 현황
| 구간 | 파일 수 | 주요 내용 |
|------|--------|----------|
(archive/ 하위 월별 요약)
```

---

## 아카이브 접근 정책

archive/는 **접근 가능하되 평소에는 활성 문서를 우선 참조**한다.

- INDEX.md의 "아카이브 현황"으로 무엇이 보관되어 있는지 파악 가능
- 과거 이력/맥락이 필요하면 archive/ 하위를 Glob/Read로 탐색
- `harvested_to` frontmatter로 "이 정보가 어디에 반영됐는지" 역추적 가능
- archive 파일은 **수정하지 않는다** (읽기 전용)

---

## 주의사항

- 영구 참조 문서(modules, guides, customers, people, adr, ddl, pmd, core-ref)는 절대 아카이브하지 않는다
- leadership/config.md는 아카이브하지 않는다 (설정 파일)
- INDEX.md 60줄 초과 시 카테고리를 병합하여 줄인다
- 수확 시 오탐 방지: 보고서에서 사용자가 최종 확인한 항목만 반영
- docs/original은 .docx, .xlsx 등 바이너리라 수확 없이 이동만
- 프로젝트 종료 판단이 불확실하면 사용자에게 질문

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT 6-1절** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경/규모]** 전체 문서 10,000줄 이상
- 신호: 가든 대상 문서 트리의 총 라인 수 10,000+
- 대응: 카테고리별 분할 스캔: (learn / people / customer / 기타) 단위로 순차 실행, 사용자에게 우선순위 선택 요청

**[데이터 결함]** 만료 정책 충돌(frontmatter vs 경로 추론)
- 신호: 파일 frontmatter `expires`와 경로 관례(예: `temp/`, `draft/`)가 상충
- 대응: frontmatter 우선. frontmatter 값을 신뢰하고, 경로 추론 결과는 `[경로 힌트 무시됨]` 주석으로만 남김
