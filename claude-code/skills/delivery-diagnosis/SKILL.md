---
name: delivery-diagnosis
description: 전달과 실행 관점 진단. 일정 예측 가능성, WIP와 차단 요인, 작업 흐름, 재작업률, 자원과 역량 매칭에 집중. 사업, 제품, 기술 진단이 "무엇을, 왜" 라면 이 스킬은 "어떻게 흘러가고 있는가" 에 답한다.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash, WebSearch, AskUserQuestion, mcp__github__list_issues, mcp__github__list_pull_requests, mcp__github__search_issues
---

## 역할

**일이 흘러가는가** 를 본다. "약속한 것이 약속한 시기에 나오는가".

역할:
1. **예측 가능성**: 일정 준수율, 추정 vs 실제 갭, 오버런 패턴
2. **워크플로우 건강도**: WIP, lead time, throughput, 작업 흐름 정체
3. **차단과 블로커 분석**: 누가 무엇에 차단되고 있는가, 인접 팀 의존성
4. **품질 vs 속도 트레이드오프**: 재작업률, 핫픽스 비율, 기술 부채 누적
5. **자원과 역량 매칭**: 일과 사람의 매칭 (중복, 갭, 번아웃 신호)
6. **사이클 권고**: 다음 스프린트/사이클에서 가장 급한 개선 1~2개

톤: 스크럼 마스터, DM, PM. 실무 호흡, 데이터 기반, 비난 금지. 사람이 아니라 시스템.

## 핵심 원칙

### 다른 진단과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "무엇을 만들까?" | /product-diagnosis | [FAIL] 다루지 않음 |
| "코드가 건강한가?" | /tech-diagnosis | [FAIL] 다루지 않음. 재작업률만 참조 |
| "돈이 충분한가?" | /business-diagnosis | [FAIL] 다루지 않음. 자원 배분 결과만 참조 |
| "왜 자꾸 일정이 밀리는가?" | **/delivery-diagnosis** | [OK] 핵심 |
| "WIP 가 너무 많은가?" | **/delivery-diagnosis** | [OK] 핵심 |
| "팀 어디에 차단이 쌓이는가?" | **/delivery-diagnosis** | [OK] 핵심 |

### 검증과 편향 방지

1. **사람이 아니라 시스템.** 특정 인물 비난 금지. 패턴, 구조, 인센티브를 봄
2. **데이터 우선, 일화는 보조.** "느낌상 느려진다" 보다 "lead time p50 이 X에서 Y로" 가 우선
3. **추정값은 명시.** 정확한 데이터 없으면 `(근사 추정, 신뢰도 2/5)` 표기
4. **선행 신호 vs 후행 신호.** 일정 미준수는 후행. WIP 증가와 재작업 증가가 선행
5. **다른 진단 보고서 참조 시** 날짜와 신뢰도 명시

### 데이터 소스 신뢰도

| 소스 | 신뢰도 | 전달 관점에서의 가치 |
|------|:------:|-----------------|
| issues/ (이슈 트래커) | 5/5 | 약속, 완료, 기한의 객관적 기록 |
| git log / PR | 5/5 | 실제 산출 시점, 리뷰 사이클 |
| daily-todos/ | 4/5 | 일일 작업 흐름, 차단 신호 |
| projects/*/ | 4/5 | 프로젝트별 진행 상태 |
| daily/ | 3/5 | 회고 (재작업과 차단 정성 신호) |
| briefing/ | 3/5 | 주간 변경 흐름 |
| meetings/ | 3/5 | 의사결정과 차단 해소 맥락 |
| memo/ | 2/5 | 비공식 관찰 (비난 금지 원칙 적용) |
| auto memory | 4/5 | 교정된 사실 |

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행. 도메인 규칙 검증 생략, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob + Grep 으로 구조 추론 fallback |
| 인프라 정보 | `.local.claude/INFRASTRUCTURE.md` | 선택 | 배포와 CI/CD 관련 분석 영역 생략 + `[인프라 데이터 부재]` 안내 |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` (4절 도메인 점검 카테고리) | 선택 | Tier 1(도메인 무관 일반 점검)만 수행 |
| 팀 정보 | `.local.claude/team.md` | 선택 | git author 그대로 표기, `[담당자 미지정]` 태그 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback, `[코드 직접 확인]` 태그 |
| 이전 진단 보고서 | `.local.claude/reports/YYYY-MM-DD-*-diagnosis.md` | 선택 | 초회 진단 모드로 진행 (변화/델타 분석 생략) |
| 일일 메모 | `.local.claude/daily/` | 선택 | 선행 신호(WIP, 재작업) 포착 불가. 후행 지표(lead time, throughput)만 사용 |
| 회의록 | `.local.claude/meetings/` | 선택 | 의사결정 맥락 부재. git log 패턴으로 추정 |

## 프로젝트 컨텍스트 (필수, 호출 전 read)

다음 파일이 존재하면 우선 read:
- `CLAUDE.md` (자동 로드, 프로젝트 구조와 컨벤션)
- `bot/INDEX.md` 또는 `.local.claude/INDEX.md`
- `.local.claude/team.md` (팀 구성과 역량)
- `.local.claude/projects/*/` (진행 중 프로젝트)

## 모드 판단

| 입력 | 모드 | 예상 소요 |
|------|------|----------|
| `/delivery-diagnosis` (기본) | **종합 진단**: 6파트 전체 | ~25분+ |
| `flow` 또는 `흐름` | **워크플로우 심층**: 파트 2만 | ~10분 |
| `blockers` 또는 `블로커` | **차단 분석**: 파트 3만 | ~10분 |
| `predict` 또는 `예측` | **예측 가능성**: 파트 1만 | ~10분 |
| `delta` 또는 `변화` | **델타**: 이전 보고서 대비 변화만 | ~10분 |
| `quick` | **요약**: 2~3페이지 | ~10분 |

## 프로세스

### Phase 1: 데이터 수집

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**:
> - Read: `.local.claude/team.md`, `.local.claude/projects/*/STATUS.md`, 이전 /delivery-diagnosis + /business-diagnosis + /tech-diagnosis 보고서
> - Glob: `.local.claude/daily/*.md` (최근 14), `.local.claude/daily-todos/*.md` (최근 14), `.local.claude/briefing/*.md` (최근 4), `.local.claude/issues/*.md`
> - Bash: `git log --since="30 days ago"`, `git shortlog -sn`, `gh pr list --state merged --json number,createdAt,mergedAt`, `gh issue list --json number,createdAt,closedAt,labels`, 차단 키워드 grep 전부 동시

**1-1. 기존 보고서 확인**

```bash
# 이전 /delivery-diagnosis
ls .local.claude/reports/ 2>/dev/null | grep -iE 'delivery-diagnosis' | sort | tail -3

# 인접 진단 (자원 맥락 참조)
ls .local.claude/reports/ 2>/dev/null | grep -iE '(business|tech)-diagnosis' | sort | tail -2
```

**1-2. 전달 데이터 수집**

```bash
# 활동 측정 (지난 30일 기준)
git log --since="30 days ago" --oneline | wc -l
git shortlog -sn --since="30 days ago"

# PR 사이클 (병합 vs 미병합)
gh pr list --state merged --limit 50 --json number,createdAt,mergedAt 2>/dev/null
gh pr list --state open --limit 50 --json number,createdAt,labels 2>/dev/null

# 이슈 흐름
gh issue list --state closed --limit 50 --json number,createdAt,closedAt 2>/dev/null
gh issue list --state open --limit 50 --json number,createdAt,labels,assignees 2>/dev/null

# 일일 작업 흐름
ls .local.claude/daily-todos/ 2>/dev/null | tail -14
ls .local.claude/daily/ 2>/dev/null | tail -14
```

**[필수 Read]**
- `.local.claude/team.md`: 자원 매칭의 기준
- `.local.claude/projects/*/STATUS.md` (있으면): 프로젝트 상태
- 이전 /delivery-diagnosis (있으면)

**[기간 내]**
- `.local.claude/daily/` 최근 N건: 차단과 재작업 정성 신호
- `.local.claude/daily-todos/` 최근 N건: 작업 흐름
- `.local.claude/briefing/` 최근 4건: 주간 변경 패턴
- `.local.claude/issues/`: 약속 vs 완료 추적

**1-3. 메트릭 측정 (자동 산출)**

| 메트릭 | 산식 | 데이터 소스 |
|--------|-----|----------|
| Lead time (p50, p90) | PR createdAt 에서 mergedAt 까지 | gh pr list |
| Cycle time | 첫 커밋에서 merge 까지 | git log + PR |
| Throughput | 주당 PR merged 수 | gh pr list |
| WIP | 동시 open PR + 진행 중 issue | gh pr/issue list |
| 차단 신호 | "blocked", "stuck", "기다림" 키워드 | daily/, daily-todos/ Grep |
| 재작업률 | revert 및 핫픽스 PR / 전체 PR | PR title/label Grep |
| 추정 갭 | issue label 의 estimate vs 실제 종료 | gh issue list |

데이터 부족 시 `(근사 추정, 신뢰도 2/5)` 표기. 측정 불가 항목은 `[측정 불가]` 명시.

### Phase 2: 팩트 시트 + 사용자 검증

```markdown
## 팩트 시트: 검증 요청

### 팀 (team.md 기준)
- 인원: N명, 활동 멤버: N명 (지난 30일 git author)

### 활동 (지난 30일)
- PR merged: N건 / open: N건
- Issue closed: N건 / open: N건
- 평균 Lead time: X시간 (p50) / Y시간 (p90)

### 핵심 가정 (검증 필요)
- [ ] 현재 진행 중 주요 프로젝트 N개
- [ ] 최근 일정 미준수 사례 (있으면)
- [ ] 가장 큰 차단 요인 1~2개
- [ ] [이전 보고서 미검증 항목]

**위 내용 중 틀린 것이 있으면 알려주세요.**
```

**`AskUserQuestion`으로 검증 요청.** 사용자 응답 후 교정 반영.

### Phase 3: 6파트 분석 + 자기 검증

---

## PART 1: 예측 가능성 (전달 관점에서만 본다)

> 약속한 시점에 약속한 것이 나오는가

### 1-1. 일정 준수율

| 기간 | 약속 N건 | 정시 완료 | 지연 완료 | 미완료 | 준수율 |
|------|:------:|:------:|:------:|:----:|:----:|
| 지난 4주 | | | | | |
| 지난 12주 | | | | | |

근거: issue label 의 due date / milestone, daily-todos 의 "오늘까지" 표기

### 1-2. 추정 vs 실제 갭

| 작업 유형 | 추정 평균 | 실제 평균 | 갭 비율 | 패턴 |
|----------|:------:|:------:|:-----:|------|
| 신규 기능 | | | | |
| 버그 수정 | | | | |
| 리팩토링 | | | | |

오버런 비율 > 1.5 면 **추정 방법 자체** 점검 권고.

### 1-3. 일정 리스크 분석

- 지금 milestone 중 미달 위험 N건
- 가장 큰 일정 리스크: [건]
- 외부 의존 (디자인, 법무, 고객 응답 등) 으로 차단된 건: N건

**의사결정 포인트:** 다음 사이클에서 일정 신뢰도 회복 핵심 1줄

---

## PART 2: 워크플로우 건강도 (전달 관점에서만 본다)

> 작업이 흐르는가, 정체되는가

### 2-1. 작업 흐름 메트릭

| 지표 | 현재 | 4주 전 | 추세 | 건전 기준 |
|------|:----:|:----:|:----:|--------|
| Lead time p50 | | | | <3일 (코드 변경) |
| Cycle time p50 | | | | <2일 (코드 변경) |
| Throughput (주) | | | | 안정 |
| WIP | | | | 인원 × 1.5 이하 |

### 2-2. 정체 구간 식별

PR 라이프사이클 단계별 평균 시간:
| 단계 | 평균 시간 | 정체 신호 |
|------|:------:|---------|
| 첫 커밋에서 PR open 까지 | | |
| PR open 에서 첫 리뷰까지 | | (>24h 면 정체) |
| 첫 리뷰에서 승인까지 | | |
| 승인에서 merge 까지 | | (>4h 면 정체) |

### 2-3. WIP 한계 점검

| 멤버 | 동시 open PR | 진행 중 issue | WIP 합 | 한계 초과? |
|------|:----:|:----:|:----:|:------:|
| ... | | | | |

WIP 한계 초과 인원은 차단, 재작업, 번아웃 위험 시그널.

**의사결정 포인트:** 워크플로우에서 가장 급한 정체 구간 1줄

---

## PART 3: 차단과 블로커 분석 (전달 관점에서만 본다)

> 누가 무엇에 막혀 있는가

### 3-1. 차단 패턴

daily/, daily-todos/ 에서 `blocked`, `stuck`, `기다림`, `요청 보냄`, `응답 없음` 키워드 grep:

| 차단 유형 | 빈도 | 평균 차단 시간 | 주요 원인 |
|----------|:----:|:--------:|---------|
| 외부 응답 대기 | | | |
| 의존 작업 미완 | | | |
| 권한, 접근 부족 | | | |
| 의사결정 보류 | | | |
| 기술적 막힘 | | | |

### 3-2. 인접 팀과 외부 의존성

| 의존 대상 | 대기 중 건수 | 평균 대기 | 위험도 |
|---------|:-------:|:------:|:----:|
| ... | | | |

### 3-3. 반복 차단 패턴

같은 유형 차단이 N회 이상 반복되면 **시스템 문제**. 개선 후보:
- 권한 사전 부여 / 접근 자동화
- 의사결정 위임 명확화
- 외부 응답 SLA 합의

**의사결정 포인트:** 가장 자주 발생하는 차단 1개 + 시스템 개선 방향

---

## PART 4: 품질 vs 속도 트레이드오프 (전달 관점에서만 본다)

> 빨리 가다 부서지고 있는가, 너무 신중해 멈췄는가

### 4-1. 재작업과 핫픽스

| 지표 | 지난 4주 | 지난 12주 | 추세 |
|------|:------:|:-------:|:----:|
| Hotfix PR / 전체 PR | | | |
| Revert PR / 전체 PR | | | |
| "fix:" 커밋 / 전체 커밋 | | | |
| 같은 파일 재수정 (1주 내) | | | |

재작업률 > 20% 면 품질 손실. 0% 에 가까우면 과도한 신중 또는 테스트 부족 가능성.

### 4-2. 리뷰 깊이 vs 속도

| 지표 | 현재 | 건전 기준 |
|------|:----:|--------|
| 리뷰 의견/PR | | 1~5개 |
| Approve 즉시 비율 | | 20~50% |
| Self-merge 비율 | | <10% |

### 4-3. 기술 부채 신호 (delivery 관점)

- TODO/FIXME 증가 추세 (Grep)
- "나중에", "임시로", "일단" 키워드 daily 빈도
- 같은 영역 반복 수정 (코드 핫스팟)

> 상세 기술 부채 분석은 /tech-diagnosis. 여기선 전달 속도에 영향 주는 신호만.

**의사결정 포인트:** 품질-속도 균형에서 지금 어느 쪽으로 기울어야 하는지 1줄

---

## PART 5: 자원과 역량 매칭 (전달 관점에서만 본다)

> 일과 사람이 맞물려 있는가

### 5-1. 작업 부하 분포

| 멤버 | PR (4주) | Issue 담당 | WIP | 회고 신호 |
|------|:------:|:------:|:----:|---------|
| ... | | | | |

회고 신호: daily/ 에서 "지친다", "오래 걸린다", "혼자 하고 있다" 등.

### 5-2. 역량 갭 vs 업무

| 영역 | 필요 역량 | 가능 멤버 | 갭 |
|------|--------|--------|----|
| ... | | | |

team.md 의 멤버 역량 + 진행 작업 매칭. 가능 멤버 1명뿐인 영역은 bus factor 위험.

### 5-3. 번아웃, 중복, 놀려진 자원

- 번아웃 신호: WIP 한계 초과 + 재작업률 ↑ + daily 에 피로 표현
- 중복: 같은 영역 2명+ 동시 작업 (조율 미흡)
- 놀려진 자원: 4주 무활동 멤버 (쉬는 게 아니면 매칭 실패)

**의사결정 포인트:** 자원 매칭에서 가장 급한 조정 1줄

---

## PART 6: 사이클 권고 (다음 스프린트와 반복에서)

> "지금 무엇을 바꾸면 가장 큰 영향이 있는가"

PART 1~5 의 의사결정 포인트를 종합:

### 6-1. 가장 급한 개선 1~2개

| # | 개선 항목 | 근거 (어느 PART) | 예상 효과 | 액션 |
|---|---------|------------|--------|------|
| 1 | | | | |
| 2 | | | | |

### 6-2. 측정 약속

다음 보고서까지 추적할 메트릭:
- [ ] Lead time p50: 목표 X
- [ ] WIP: 목표 인원 × 1.5
- [ ] 차단 빈도: 목표 -50%

### 6-3. 안 할 것

- 새 프로세스 추가 X (현 프로세스도 못 따름이면 추가는 부담)
- (구체 항목)

---

## Phase 4: 자기 검증

**Adversarial Review**. 핵심 권고/판단 Top 1~2 각각에 대해:
1. **근거 재점검**: 정량 메트릭(lead time, WIP, 재작업률)인가 정성 일화인가? 단일 기간 관찰인가 추세인가?
2. **전제 검증**: 권고가 유효하려면 어떤 전제가 필요한가? (예: "WIP 축소"라면 작업 단위 분해 가능 / 외부 의존 차단 해소 가능)
3. **반대 증거 탐색**: "왜 이미 하지 않았나?" / "현재가 충분하다면?" 등 반박 1개 이상 탐색. 사람에 대한 추측이 시스템 분석으로 바뀌었는지 재점검

반박 유효 시 본문 수정, 부분 반박 시 "단, {가능성}" 인라인 추가.

```markdown
## 자기 검증 결과

1. **데이터 충실성**: 정량 메트릭 N개 / 정성 일화 N개
2. **인물 비난**: 0건 (사람 X, 시스템과 패턴 O)
3. **추정 표기**: 추정값에 모두 신뢰도(n/5) 부여
4. **다른 진단과 모순**: business / tech / product 진단과 충돌 없음
5. **실행 가능성**: 권고 1~2개가 다음 사이클에 실제 실행 가능한 크기
```

## 출력 구조

```yaml
---
type: delivery-diagnosis
date: YYYY-MM-DD
mode: full | flow | blockers | predict | delta | quick
previous: YYYY-MM-DD
parts: 1,2,3,4,5,6
data-sources:
  team: N명
  prs-merged: N건 (30일)
  issues-closed: N건 (30일)
  daily: N건
  daily-todos: N건
metrics:
  lead-time-p50: Xh
  wip-current: N
  rework-rate: X%
---

# 전달과 실행 진단 보고서

> **기간**: YYYY-MM-DD ~ YYYY-MM-DD
> **관점**: 전달 책임 시각 / Delivery Manager
> **모드**: {모드}
> **참조**: business [날짜], tech [날짜] (없으면 생략)

## TL;DR (3줄)
- 현재 국면: [예측 가능성, 흐름, 차단 종합 1줄]
- 가장 급한 것: [1줄]
- 다음 액션: [1줄]

[PART 1~6]

[참조] business [날짜], tech [날짜], product [날짜]
```

## 저장 경로

`.local.claude/reports/YYYY-MM-DD-delivery-diagnosis.md`

## 다음 스킬 연결

- 차단 패턴이 코드 의존이면 `/tech-diagnosis`
- 차단이 자원 (인원, 예산) 이면 `/business-diagnosis`
- 차단이 제품 우선순위 모호이면 `/product-diagnosis`
- 특정 인물 패턴 보이면 `/coaching` (1on1 준비)

## 분량 임계에 따른 자동 분리

| 임계 | 동작 |
|------|------|
| ≤500줄 | 단일 보고서 유지 |
| >500줄 | PART 별 분리 권장 (6개 sub-doc) |

## 제약조건

- **사람이 아니라 시스템에 집중.** 특정 인물 비난 금지. 패턴, 구조, 인센티브 분석
- **데이터 우선, 일화는 보조.** 정량 메트릭 없으면 `(근사 추정, 신뢰도 2/5)` 표기
- **선행 신호 추적.** 일정 미준수는 후행. WIP, 재작업, 차단 빈도가 선행
- **다른 진단 영역 침범 금지.** 코드 상세는 /tech, 자원 결정은 /business, 제품 우선순위는 /product
- **권고는 1~2개만.** 다음 사이클에 실제 실행 가능한 크기로
- **새 프로세스 추가 신중.** 현 프로세스도 못 따르면 추가는 부담

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT 6-1절** 참조.

### 이 스킬의 고유 실패 시나리오

**[데이터 결함]** daily/ 기록이 15일+ 공백
- 신호: 최신 daily 파일 mtime 또는 날짜 파싱 결과 15일 이상 단절
- 대응: "선행 신호 파악 제한" 안내 + 지연과 WIP 추세 분석 생략, 스냅샷 중심 진단

**[도메인 특수성]** 단일 배포 팀(역할 분리 없음)
- 신호: 팀 1명~소수 / 핸드오프 경계 부재
- 대응: WIP 한계와 핸드오프 지연 분석 생략, 리드타임과 배포 빈도만 보고
