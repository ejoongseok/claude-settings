---
name: qa-run-deep
description: "QA-*.md 체크리스트를 MCP Playwright 로 실행하면서 관련 SRS, PRD, 구현 코드, biz-rules, git log, 과거 run 을 1M context 에 동시 맥락화. AI 시각 판정, 예측 QA, 공통 원인 클러스터링, 메타-QA, 코드와 QA 일관성, 시맨틱 우선순위 재산정, 대안 비교까지 수행. 비싸므로 추천 신호 충족 시에만."
argument-hint: "<qa-md-path> [--stop-on-fail] [--dry-run] [--only P1|P1-P2] [--sample N] [--since-days 30]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(mkdir *, ls *, date *, wc *, dirname *, grep *, test *, du *, git log *, git diff *, git show *, head *, tail *), mcp__playwright__browser_navigate, mcp__playwright__browser_navigate_back, mcp__playwright__browser_snapshot, mcp__playwright__browser_click, mcp__playwright__browser_type, mcp__playwright__browser_fill_form, mcp__playwright__browser_hover, mcp__playwright__browser_select_option, mcp__playwright__browser_press_key, mcp__playwright__browser_wait_for, mcp__playwright__browser_evaluate, mcp__playwright__browser_console_messages, mcp__playwright__browser_network_requests, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_file_upload, mcp__playwright__browser_handle_dialog, mcp__playwright__browser_drag, mcp__playwright__browser_resize, mcp__playwright__browser_tabs, mcp__playwright__browser_close
effort: max
disable-model-invocation: true
---

**핵심 원칙** (어기면 스킬 실패):

1. MCP 도구는 **이 세션이 직접** 호출. 서브에이전트 위임 금지. 1M context 교차 분석이 이 스킬의 존재 이유
2. 인사이트 각 항목은 **6필드** (발견, 근거, 액션, 공수, 신뢰도, 우선순위) 누락 시 삭제
3. `[확신]` 은 측정치 인용만. `[추정]`, `[가설]` 과 흐리면 신뢰 붕괴
4. 자기 검증 루프 **1회 고정**
5. 원본 `QA-*.md`, SRS, 코드는 **절대 수정 금지**. 읽기 전용

---

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| QA 매트릭스 | `{QA-prefix}-QA*.md` | **필수** | "/qa 로 먼저 QA 매트릭스 생성 필요" 안내 후 종료 |
| 과거 QA 실행 기록 | 같은 디렉터리의 `*-qa-run-*.md` | 선택 | 회귀 트렌드 분석 생략, 단일 실행 모드 |
| Playwright MCP | `.mcp.json` | **필수** | MCP 미설치 시 설치 가이드 후 종료 |
| git 히스토리 | `.git/` | 선택 | 예측 QA 스킵 |

---

## 1단계: 입력 파싱 + 추천 모드 확인

`$ARGUMENTS` 공백 분리:
- **1번째 토큰** = `QA-*.md` 경로 (필수)
- 플래그: `--stop-on-fail`, `--dry-run`, `--only P1|P1-P2`, `--sample N`, `--since-days N` (기본 30)

### 1.1 추천 모드 충돌 확인

QA frontmatter `recommended-runner` 읽기:
- `deep` 이면 그대로 진행
- `light` 면 AskUserQuestion: "이 QA 는 light 권장 ({recommended-runner-reason}). Deep 으로 진행하면 시간과 비용 증가. 그래도 진행?"
  - 옵션: **Deep 강행** / **`/qa-run-light` 으로 전환** / **중단**

frontmatter 미존재 시 안내 출력 후 진행.

---

## 2단계: QA 파일 파싱

`Read` 로 전체 로드. Step, 선수 조건, 공통 체크 추출.

### 2.1 Step 헤더 정규식

```regex
^#{3,4}\s+Step\s+([0-9]+(?:\.[0-9]+|-[0-9]+)?)\s*:\s*\[([^\]]+)\]\s*(.+?)\s*[-—]\s*Level\s+([0-9]+)
```

캡처: `(step-id, category, title, level)`. 우선순위 태그([URGENT]P1/[참고]P2/[정상]P3) 별도 추출.

### 2.2 MCP 체크박스 / 기대값 분류 / 입력 매트릭스

(`/qa-run-light` 의 2.2~2.4절과 동일)

기대값 분류에서 **Deep 만의 차이**:
- **natural-language**: `ai-vision-check`. 스크린샷 + 기대값을 multimodal 이 직접 판정 (5.3절)

### 2.3 수동 Step / 우선순위 / 도메인 (`/qa-run-light` 의 2.5절과 동일)

### 2.4 파서 매치율

Step 헤더 매치율 < 80% 이면 AskUserQuestion (재생성/강행/중단).

---

## 3단계: Deep 맥락 수집

> **[1M 활용]** 서브 분할 없이 메인에서 직접 **다중 파일 동시 로드** (L80~98 가드레일 강화):
> - 로드: `SRS-*.md` + `PRD-*.md` + `TODO-*.md` + 관련 controller/service/mapper 경로 + `.local.claude/biz-rules.md` + `.local.claude/biz-rules-detail.md` + 최근 `QA-RUN-*.md` {since-days}일치 + `git log --since` 결과
> - 교차: {SRS 기대 동작 vs 실제 코드 구현 불일치}, {biz-rules 도메인 카테고리 vs QA 매트릭스 커버 공백}, {과거 run 의 만성 flaky vs 이번 Step 예측 리스크}
>
> 이 섹션의 맥락 축적이 Deep 모드의 존재 이유. 서브에이전트 위임하면 교차 분석 자체가 불가능해짐.

다음을 Read 하여 메인 컨텍스트에 올림:

**문서 축**:
- 같은 `dirname(QA)` 의 `SRS-*.md`, `PRD-*.md`, `TODO-*.md` 전부 (Glob)
- 필요 시 상위 디렉터리의 `README.md`, `STATUS.md`, `AS-IS.md`
- `.local.claude/biz-rules.md` (자동 로드지만 Deep 에선 `biz-rules-detail.md` 도 Read)
- `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` (project-native 시)

**코드 축**:
- QA Step 에 언급된 경로 (controller, service, mapper) 는 Grep 으로 추출 후 Read
- 없으면 Step 제목 키워드로 `Grep -r <키워드> {프로젝트 코드 디렉터리}` 실행 후 상위 3개 파일 Read

**히스토리 축**:
- `git log --since={since-days}.days.ago -- {관련 경로}` 로 커밋 해시, 메시지, 변경 파일 수집
- `Glob {dirname(QA)}/QA-RUN-*.md` 후 mtime 으로 {since-days}일 필터, 과거 run N개 Read

**맥락 총량 가드**: Read 한 파일 총 로드 추정 토큰 ~600K(1M의 60%; 줄 수로 대략 가늠) 근접 시 AskUserQuestion ("범위 축소: 7일 / 14일 / 유지 / 중단").

### 3.1 예측 QA (실행 순서 재정렬)

수집한 git log + 과거 run 으로 **이번 run 의 위험 Step** 예측:

- 지난 {since-days}일 커밋이 건드린 파일 집합 ∩ 각 Step 이 간접 참조하는 도메인, 이 교집합이 높은 Step 에 `predicted-risk: high` 태그
- 과거 run 에서 flaky 또는 fail 이 2회 이상이면 `historical-risk` 태그
- `high-risk` Step 을 **실행 큐 앞으로 재정렬** (P1 내 우선, P2 내 우선)

---

## 4단계: 선수 조건 체크 + 비용 체크포인트

### 4.1 선수 조건 (`/qa-run-light` 3단계와 동일)

### 4.2 비용 체크포인트

Step 수 + Deep 맥락 비용 함께:
- Step ≤ 20 + 맥락 적음: 진행
- Step 20~50: 로그만
- Step > 50 또는 맥락 추정 토큰 ~600K(1M의 60%; 줄 수로 대략 가늠) 근접: AskUserQuestion ("Deep 진행 / Light 전환 / `--only P1` / 중단")

`--dry-run` 종료 (Step 목록 + 맥락 요약 + 예상 소요 출력).

**예상 소요**: `step × 3s + 2s evidence + 5s AI 시각 판정(자연어 기대값당) + 인사이트 생성 60~180s`

---

## 5단계: Step 순차 실행 (예측 순서)

`run-id = date +%Y%m%d-%H%M`. `runs_dir = dirname(QA)/runs/{run-id}/`. `mkdir -p` 선행.

### 5.1 실행 루프

각 Step (예측 순서):
1. 시작 로그 (`[Step X.Y] 실행 중... (risk: {predicted-risk})`)
2. MCP 시퀀스 순차 호출
3. assertion 비교:
   - `assertion-eval` / `network-contract`: 기계 판정 (Light 와 동일)
   - `natural-language`: **`ai-vision-check`** (5.3절)
4. 결과: `pass` / `fail` / `flaky` / `manual-pending` / `ai-vision-pass` / `ai-vision-fail` / `blocked-manual` / `pass-after-manual` / `fail-after-manual` / `skip-after-block`

### 5.2 Retry (5.4절 막힘 감지 우선)

Light 와 동일. 단, 막힘 감지 신호 시 retry 즉시 중단 (5.4절이 우선).

### 5.3 AI 시각 판정 (Deep 핵심 차이)

자연어 기대값을 가진 Step:
1. Step 종료 시 `browser_take_screenshot` 으로 화면 캡처 (이미 증거 계층에 포함)
2. 이 스크린샷을 **Read 도구로 메인 컨텍스트에 올림** (multimodal)
3. 기대값 자연어와 비교하여 판정:
   - "자연스럽게 정렬됨" / "깨지지 않음" / "특수문자 정상 표시" 등
4. 판정 결과 + **근거** (이미지 어느 부분이 기대와 일치/불일치) Step 결과에 기록 + `[시각판정]` 태그
5. 판정 불가 시 `manual-pending` 으로 fallback

**제약**: AI 시각 판정은 **자연어 기대값에만** 적용. `assertion-eval`, `network-contract` 는 기계 판정 유지. CSS 픽셀 단위 정합은 한계 있음.

### 5.4 막힘 감지 + 사용자 개입

(`/qa-run-light` 의 5.4절과 동일)

### 5.5 stop-on-fail + 격리

(`/qa-run-light` 의 5.3절과 동일)

---

## 6단계: 증거 수집 (4계층)

(`/qa-run-light` 6단계와 동일)

추가:
- `step-{id}-vision.md`: AI 시각 판정한 Step 의 판정 근거 텍스트

---

## 7단계: 결과 집계 + 회귀 트렌드

### 7.1 Step 결과 테이블

필드: `step-id, category, level, priority, result, duration-ms, evidence, fail-summary, predicted-risk, historical-risk`.

카운트: Light 카운트 + `ai-vision-pass, ai-vision-fail`.

### 7.2 회귀 트렌드 (Deep = 지난 {since-days}일 모든 run)

지난 {since-days}일 모든 `QA-RUN-*.md` 를 조인해 트렌드 산출:
- 각 Step 의 **Pass 비율 변화** (%)
- **만성 flaky** (3회 이상 연속 flaky)
- **반복 회귀** (지난 5 run 중 fail 에서 pass 로 갔다가 다시 fail 로 2회 이상 왕복)
- **한 번도 pass 없는 Step** (신호: QA 작성 자체가 잘못됐거나 기능 미구현)

### 7.3 공통 원인 클러스터링

> **[1M 활용]** 서브 분할 없이 메인에서 직접 **다중 run 동시 로드** 후 교차:
> - 로드: 이번 run 의 모든 `step-*-console.txt` + `step-*-network.json` + 과거 `QA-RUN-*.md` {since-days}일치
> - 교차: {콘솔 에러 문자열 클러스터링 × 과거 run 동일 문자열}, {네트워크 URL 실패 × 과거 백엔드 배포 타임라인}, {DOM selector stale × 최근 FE 커밋}

실패와 flaky 증거 교차 분석:
- **콘솔 에러 메시지 클러스터링**: 동일 에러 문자열이 N개 Step 에 나타나면 공통 원인 1건
- **네트워크 URL 클러스터링**: 같은 엔드포인트 다수 실패면 백엔드 공통 원인
- **DOM selector 클러스터링**: 같은 selector 다수 stale 이면 프론트 공통 원인
- **소요 시간 이상치**: P90 > P50 × 3 이면 외부 의존성 지연

클러스터 결과는 8.4절 반복 실패 패턴의 근거로 재사용.

---

## 8단계: 인사이트 생성 (10카테고리)

**Light 7 + Deep 전용 3 = 10카테고리**.

각 항목 6필드 전부 필수 (Light 와 동일).

### 8.1 놓친 케이스 (Light + Deep)

**트리거**: 실행 매트릭스 행 ≠ 이론적 카디널리티, 또는 입력 필드 타입 체크리스트에서 빠진 것.

**Deep 강화**: QA 매트릭스뿐만 아니라 **실제 코드** 를 Grep 해서 QA 에 빠진 분기 탐지. 예: 코드에 `if (userType === 'ADMIN')` 인데 QA 에 ADMIN 케이스가 없으면 누락.

### 8.2 숨은 의존성

**Deep 강화**: 네트워크와 DOM 교차 분석 + **코드에서 실제 의존성 그래프** 추출 (Grep `import` / `@Autowired` / `@Inject`).

### 8.3 맹점

**Deep 강화**: `biz-rules.md` 상태 전이 표와 대조해 **도메인 규칙상 필요하나 QA 에 빠진 전이** 자동 탐지.

### 8.4 반복 실패 패턴

**Deep 강화**: 7.3절 공통 원인 클러스터링 결과와 과거 run 을 매칭해 **만성 패턴** 식별.

### 8.5 도메인 규칙 구멍 (domain-native 전용)

**트리거**: 격리 키(있는 프로젝트만) 미확인, 상태 전이 미전수, 승인 반려 케이스 누락, 이벤트 리스너 반영 미확인.

**standalone**: "해당 없음" 한 줄.

### 8.6 인프라와 E2E 조건

(Light 와 동일)

### 8.7 다음 릴리즈 개선 액션

8.1~8.6절 + 8.8~8.10절의 액션을 **P1/P2/P3 재분류** + 중복 해소 + 의존 순서 명시.

### 8.8 [Deep 전용] 코드와 QA 일관성 구멍

**트리거**: 3단계에서 수집한 코드와 QA 가 어긋남.

**탐지 방법**:
- 실패 Step 의 증거가 가리키는 코드 경로 Read
- QA 의 기대값과 실제 코드 로직 대조
- SRS 규격과 구현 대조

**출력 예**:
```
- **[확신][P1]** Step 3.2 의 기대값 "0건 안내 노출" 과 실제 코드 불일치
  - 근거: QA-xxx.md:234 기대 vs `{모듈}/web/app.js:45-52` 에서 0건일 때 안내 미구현
  - 액션: app.js 에 `.empty-state` 렌더 추가 (SRS의 예외흐름 섹션과 일치 필요)
  - 공수: 30분
```

### 8.9 [Deep 전용] 시맨틱 우선순위 재산정

**트리거**: 원본 P 등급이 비즈니스 컨텍스트로 재평가 가능.

**탐지 방법**:
- 수집한 PRD, 고객사 프로필, 마일스톤, 데모 일정 맥락
- 원본 P1/P2/P3 와 재산정 우선순위 비교

**출력 예**:
```
- **[추정][P1 재산정]** Step 5.1 i18n 검색은 원본 P2 였지만, {고객사} 시연이 이번 주라서 P1 승격
  - 근거: `.local.claude/customers/samsung-ena.md:12`, `.local.claude/daily/2026-04-16.md` 시연 일정
  - 액션: Step 5.1 실패 시 즉시 블로킹 처리
  - 공수: (의사결정만)
```

### 8.10 [Deep 전용] 메타-QA (QA 자체의 stale 판정)

**트리거**: QA 파일이 작성된 이후 N일 경과, 또는 가정한 전제가 변경.

**탐지 방법**:
- QA frontmatter `created` vs 오늘
- QA 가 참조한 TODO, SRS 의 최종 수정일 vs QA created
- 수집한 git log 에서 QA 가 가정한 엔티티 변경 여부

**출력 예**:
```
- **[추정][P2]** QA 가 2주 전 작성. 그 사이 TODO-08 이 "X 동작" 에서 "Y 동작" 으로 변경되어 QA Step 2.4 기대값 stale
  - 근거: QA-{name}.md frontmatter created=2026-04-03 vs TODO-{name}.md git log 2026-04-12
  - 액션: `/qa <원본>` 재생성
  - 공수: 15분
```

### 8.11 사용자 개입 회고: 다음 run 자동화 제안

(`/qa-run-light` 의 8.8절과 동일)

**Deep 강화**:
- 과거 run 의 개입 기록도 조인해 **반복 개입 패턴** 식별
- 같은 유형 3회 이상 누적 시 8.7절 다음 릴리즈 개선 액션에 **P1 자동화 액션** 강제 편입
- 예: "지난 5 run 중 4회 로그인 개입. 세션 seed 자동화는 선택 아닌 필수"

### 8.12 인사이트 부재 시

(Light 와 동일)

---

## 9단계: 대안 비교 테이블 (Deep 핵심 차이)

8.7절의 P1 액션에 대해 **2~3 대안** 제시.

포맷:
```markdown
#### P1-액션-1: FILES.js 생성 누락 해소

| 대안 | 방법 | 장점 | 단점 | 공수 | 되돌림 | 추천 |
|------|------|------|------|------|--------|------|
| A | index.html 에 인라인 삽입 | 즉시 동작 | 재사용 불가 | 10분 | easy | (추천) (데모용) |
| B | 별도 FILES.js 파일 생성 | TODO-02 설계대로 | 추가 파일 관리 | 30분 | easy | 운영용 |
| C | mock 서버 구동 | 실제 API 유사 | 셋업 비용 | 2시간 | medium | 과대 |

**유사 과거 사례**: `.local.claude/projects/{project-name}/human/lessons.md:45`. 같은 패턴 (인라인 vs 분리) 에서 B 선택으로 나중에 TODO 일치 시점에 이득
```

**규칙**: 모든 P1 액션 + 상위 3 P2 액션. 나머지는 8단계 인사이트에 공수만.

---

## 10단계: 자기 검증 + AskUserQuestion

### 10.1 체크리스트

> **[메타인지]** 핵심 결론 Top 3 (P1 액션, 코드와 QA 일관성 구멍, 시맨틱 우선순위 재산정)에 대해:
> 1. 근거 재점검 (측정치, 코드 경로:라인, git 커밋 해시가 실제 인용되는가 vs 일반 서술로 흐려지는가)
> 2. 전제 검증 (Deep 전용 3카테고리가 맥락 축적의 산물인가 vs Light 도 낼 수 있는 수준인가)
> 3. 반대 증거 ("이 재산정이 왜 원본 `/qa` 에서 이미 반영되지 않았나? 이 일관성 구멍이 사실은 QA 기대값 오기 아닌가?")

- [ ] 각 인사이트 6필드 전부
- [ ] `[확신]` 측정치 기반
- [ ] `[가설]` 남발이면 `[추정]` 으로 강등
- [ ] 행동 가능한 액션
- [ ] 회귀 섹션이 지난 {since-days}일 run 조인했는가
- [ ] 대안 비교 테이블이 P1 액션마다 있는가
- [ ] 8.8~8.10절 Deep 전용 3카테고리가 적절히 채워져 있는가
- [ ] 한눈에 (배너) 가 30초 내 상태 파악 가능
- [ ] 사용자 개입 1건 이상이면 8.11절 회고 + "자동화 가능성 + 다음 run 개선안"

### 10.2 AskUserQuestion

질문: "리포트와 인사이트 재읽기 완료. 문제 발견?"
옵션: 없음(저장) / 실패 원인 재분석 / 인사이트 근거 부족 / 회귀 비교 오류 / 대안 비교 부실 / Deep 전용 카테고리 재검토 / 기타

2~기타 답변 시 **해당 섹션만** 수정. 1회만.

---

## 11단계: 리포트 저장

### 11.1 파일 경로

```
dirname(QA-*.md)/QA-RUN-{기능명}-{YYYYMMDD-HHMM}.md
```

### 11.2 Frontmatter

```yaml
---
created: <ISO-8601 with timezone>
category: qa-run
retention: 90-days
run-id: <YYYYMMDD-HHMM>
mode: deep
source: <QA-*.md 상대경로>
source-qa-version: <QA frontmatter created>
domain: standalone | domain-native
recommended-runner-was: light | deep
summary:
  total: N
  pass: N
  fail: N
  flaky: N
  skip-manual: N
  not-run: N
  manual-pending: N
  ai-vision-pass: N
  ai-vision-fail: N
  blocked-manual: N
  pass-after-manual: N
  fail-after-manual: N
  skip-after-block: N
  interventions: N
  p1-fail: N
context:
  docs-loaded: [SRS-xxx.md, PRD-xxx.md, biz-rules.md, ...]
  code-files-loaded: N
  git-log-range: "YYYY-MM-DD..YYYY-MM-DD"
  prior-runs-joined: N
previous-run: <있을 때만>
regression:
  new-failures: N
  fixed: N
  chronic-flaky: N
  trend-improving: N
  trend-degrading: N
---
```

### 11.3 본문 구조

```markdown
# [기능명] QA 실행 리포트 - run-{run-id} (DEEP)

> `/qa-run-deep`. 원본 QA: [...](./...)
> 증거: `runs/{run-id}/`
> 맥락: docs-loaded {n}, code {n}, git-log {days}일, prior-runs {n}

## 0. 한눈에 (배너)
## 1. Step 별 결과 (테이블)
## 2. 실패 상세
## 3. Flaky Step
## 4. 수동 / 개입 기록
## 5. 회귀 트렌드 (지난 {since-days}일)
## 6. 공통 원인 클러스터 요약
## 7. 예측 QA 결과 검증 (예측 vs 실제)
## 8. 인사이트: 메타 분석 (10카테고리)
   8.1 놓친 케이스
   8.2 숨은 의존성
   8.3 맹점
   8.4 반복 실패 패턴
   8.5 도메인 규칙 구멍 (standalone: "해당 없음")
   8.6 인프라와 E2E 조건
   8.7 다음 릴리즈 개선 액션 (P1/P2/P3)
   8.8 [Deep] 코드와 QA 일관성 구멍
   8.9 [Deep] 시맨틱 우선순위 재산정
   8.10 [Deep] 메타-QA (QA stale 판정)
   8.11 사용자 개입 회고
## 9. 대안 비교 테이블 (P1 + Top 3 P2)
## 10. 스킬이 판단 못 한 것
```

---

## 12단계: 최종 콘솔 출력

```
[OK] qa-run-deep 완료 (run-id: {run-id})

소스: {QA 파일} (recommended: {light|deep})
실행: {pass}/{total} Pass, {fail} Fail, {flaky} Flaky, {skip-manual} 수동대기
[URGENT] P1 실패: {p1-fail}건
**사용자 개입**: {interventions}건 (자동화 가능 {A} / 수동 유지 {M}). 리포트 8.11절 회고 참조

**회귀 트렌드** (지난 {since-days}일 {prior-runs}회 대비):
  trend-improving {n}, trend-degrading {n}, chronic-flaky {n}

**맥락**: docs {n}, code {n}, git-log {days}일, prior-runs {n}

**Deep 전용 발견**:
  - 코드와 QA 일관성: {n}
  - 우선순위 재산정: {n}
  - 메타-QA stale: {n}

**P1 액션 상위 3개** (대안 비교는 리포트 9절):
  1. {액션} ({공수}) - {확신/추정/가설}
  2. ...
  3. ...

**리포트**: {경로}
**증거**: {경로}
```

부분 실행은 제목에 `[PARTIAL]`.

---

## 에러와 엣지 케이스

| 상황 | 탐지 | 대응 |
|------|------|------|
| MCP Playwright 미설치 | 첫 `browser_navigate` 에러 | 안내 후 중단 |
| 로그인, CAPTCHA, 세션만료, 블로킹모달 | 5.4절 막힘 감지 | 즉시 AskUserQuestion + 8.11절 회고 |
| 같은 막힘 3회 이상 | 카운터 per 유형 | 일괄 처리 모드 |
| QA 포맷 위반 | Step 매치 < 80% | AskUserQuestion |
| Deep 맥락 과다 | Read 추정 토큰 ~600K(1M의 60%; 줄 수로 가늠) 근접 | AskUserQuestion (범위 축소) |
| 세션 끊김 | 컨텍스트 한계 | 부분 리포트, `[PARTIAL]` |
| 스크린샷 용량 폭발 | du > 20MB | AskUserQuestion |
| 만성 flaky 3회 연속 | 과거 run 조인 | `chronic-flaky` 로 표시, 8.7절 P2 강제 |
| AI 시각 판정 실패 | Read 이미지 부적절 | `manual-pending` fallback |
| git log 없음 (repo 아님) | `git rev-parse` 실패 | 히스토리 축 스킵 |
| prior-runs 0건 | 최초 실행 | 회귀 섹션 생략 |
| `--deep` 강행 + standalone | 도메인 규칙 구멍 "해당 없음" | 나머지 Deep 카테고리는 정상 수행 |
| recommended-runner: light 인데 deep 호출 | 1.1절 추천 모드 확인 | AskUserQuestion (Deep 강행 / Light 전환 / 중단) |

---

## 주의 사항

- **원본 QA-*.md 불변**: 읽기 전용
- **서브에이전트 위임 금지**: 1M context 교차 분석이 존재 이유
- **측정 vs 추론 구분**: `[확신]` 인용, `[추정]` 과 `[가설]` 해석
- **인사이트 비어 있을 수 있음**: 8.12절 인사이트 부재 처리로 정직하게
- **Deep 비용 인식**: 매 실행 1M 사용. Light 가 기본인 이유
- **AI 시각 판정 한계**: multimodal 강력하지만 CSS 픽셀 단위 정합 어려움. `[시각판정]` 태그 명시
- **dry-run 권장**: 처음 QA 는 `--dry-run` 으로 맥락과 Step 확인
- **권한 모드**: MCP 호출이 연쇄되므로 사전 자동 허용 권장

---

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬 |
|---|---|---|
| QA 체크리스트(매트릭스) 설계와 생성 | `/qa` | [다루지 않음] |
| 빠른 경량 MCP 실행 + 7카테고리 리포트 | `/qa-run-light` | [다루지 않음] |
| MCP 실행 + 1M 맥락 교차(코드, SRS, git, 과거 run) + AI 시각 판정, 예측 QA, 메타 분석 | 이 스킬 | [핵심] |

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT 문서의 6-1절** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경/규모]** 1M 맥락 로드 대상 추정 토큰 ~600K(1M의 60%) 근접
- 신호: 대상 코드베이스와 문서 합산 추정 토큰 ~600K+ (합산 라인 수로 대략 가늠)
- 대응: 사용자에게 범위 축소 옵션 제시. (a) 모듈별 분할 실행 (b) 상위 10% 크리티컬 경로만 (c) 강행

**[의존성 부재]** Playwright MCP 미연결
- 신호: `mcp__playwright__*` 도구 호출 시 연결 에러 또는 브라우저 실행 실패
- 대응: 설치 가이드(`npx @playwright/mcp@latest` 또는 `.claude/mcp.json` 설정) 출력 후 종료
