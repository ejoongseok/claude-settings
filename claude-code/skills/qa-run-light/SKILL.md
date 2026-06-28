---
name: qa-run-light
description: "QA-*.md 체크리스트를 MCP Playwright 로 빠르게 실행하고 경량 리포트를 생성합니다. 단일 QA 파일 + 실행 증거만으로 7카테고리 인사이트 도출. Deep 모드의 AI 시각 판정·예측 QA·메타 분석은 미포함 — 그게 필요하면 /qa-run-deep 사용."
argument-hint: "<qa-md-path> [--stop-on-fail] [--dry-run] [--only P1|P1-P2] [--sample N]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(mkdir *, ls *, date *, wc *, dirname *, grep *, test *, du *), mcp__playwright__browser_navigate, mcp__playwright__browser_navigate_back, mcp__playwright__browser_snapshot, mcp__playwright__browser_click, mcp__playwright__browser_type, mcp__playwright__browser_fill_form, mcp__playwright__browser_hover, mcp__playwright__browser_select_option, mcp__playwright__browser_press_key, mcp__playwright__browser_wait_for, mcp__playwright__browser_evaluate, mcp__playwright__browser_console_messages, mcp__playwright__browser_network_requests, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_file_upload, mcp__playwright__browser_handle_dialog, mcp__playwright__browser_drag, mcp__playwright__browser_resize, mcp__playwright__browser_tabs, mcp__playwright__browser_close
effort: medium
disable-model-invocation: true
---

**핵심 원칙**:

1. MCP 도구는 **이 세션이 직접** 호출. 서브에이전트 위임 금지
2. 인사이트 각 항목은 **행동 가능** 해야 함 — 6필드(발견·근거·액션·공수·신뢰도·우선순위) 누락 시 삭제
3. `[확신]` 은 **측정치 인용**만. `[추정]`·`[가설]` 과 흐리면 리포트 신뢰 붕괴
4. 자기 검증 루프 **1회 고정**
5. 원본 `QA-*.md` 는 **절대 수정 금지** — 읽기 전용

---

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| QA 매트릭스 | `<qa-md-path>` (1번째 인자) | **필수** | "/qa 로 먼저 QA 매트릭스 생성 필요" 안내 후 종료 |
| Playwright MCP | `.mcp.json` | **필수** | 첫 `browser_navigate` 에러 시 "Playwright MCP 서버 active 확인" 안내 후 종료 |
| 직전 QA 실행 기록 | `dirname(QA)/QA-RUN-*.md` (최근 1건) | 선택 | 회귀 비교 생략, 단일 실행 모드로 진행 |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | §8.5 도메인 규칙 구멍 카테고리를 "해당 없음" 한 줄로 대체 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |

---

## 1단계: 입력 파싱 + 추천 모드 확인

`$ARGUMENTS` 공백 분리:
- **1번째 토큰** = `QA-*.md` 경로 (필수)
- 플래그: `--stop-on-fail`, `--dry-run`, `--only P1|P1-P2`, `--sample N`

인자 없으면 사용법 출력 후 중단.

### 1.1 추천 모드 충돌 확인

QA frontmatter 의 `recommended-runner` 읽기:
- `light` → 그대로 진행
- `deep` → AskUserQuestion: "이 QA 는 deep 권장 ({recommended-runner-reason}). 그래도 Light 로 진행?"
  - 옵션: **Light 강행** / **`/qa-run-deep` 으로 전환** / **중단**

frontmatter 미존재 시 안내만 출력하고 진행.

---

## 2단계: QA 파일 파싱

`Read` 로 전체 로드. Step·선수 조건·공통 체크 추출.

### 2.1 Step 헤더 정규식

```
^#{3,4}\s+Step\s+([0-9]+(?:\.[0-9]+|-[0-9]+)?)\s*:\s*\[([^\]]+)\]\s*(.+?)\s*—\s*Level\s+([0-9]+)
```

캡처: `(step-id, category, title, level)`. 우선순위 태그([URGENT]P1/[참고]P2/[정상]P3) 는 별도 정규식으로 title 끝에서 추출.

### 2.2 MCP 체크박스

```
^- \[ \] `?(browser_[a-z_]+)`?
```

도구명은 allowed-tools 화이트리스트 대조. 인자는 `[key=value]` / 백틱 코드 / 인라인 JSON 지원.

### 2.3 기대값 분류

```
\*\*기대(?:\s*\([^)]+\))?\*\*:\s*(.*)
```

분류:
- **assertion-eval**: `>= 3`, `=== X` 등 → `browser_evaluate` 결과와 비교
- **network-contract**: `HTTP 200`, `POST /api/...` → `browser_network_requests` 필터 검증
- **natural-language**: 자연어 기대 → **Light 모드에선 `manual-pending`** (사용자 확인 섹션)

자연어 기대값이 5건 이상이면 §1.1 과 별도로 한 번 더 안내: "자연어 기대값 N건 — Deep 의 AI 시각 판정 권장".

### 2.4 입력 매트릭스

```
\*\*입력\s*값\s*매트릭스\*\*:
```

직후 표의 각 행 → Step 반복 실행. Step 본문 `{변수}`·`{케이스}` 치환. 결과 ID 에 `-row1`, `-row2` suffix.

### 2.5 수동 Step / 우선순위 / 도메인

- `\(MCP\s+밖,\s*수동\)` → `skip-manual` 태그
- `[URGENT]P1` → P1, `[참고]P2` → P2, `[정상]P3` → P3, 미지정 → P2 기본 (경고 출력)
- Frontmatter `domain: standalone` vs `domain-native` — §5 도메인 규칙 구멍 카테고리 분기에 사용

### 2.6 파서 매치율

Step 헤더 매치율 < 80% → AskUserQuestion (재생성 권장 / 강행 / 중단).

---

## 3단계: 선수 조건 체크

`## 0. 선수 조건` 체크박스 순회:
1. 파일 경로 → `test -f` / `ls`
2. HTTP URL → `browser_navigate` + `browser_console_messages(level=error)` 로 404/CORS 탐지
3. 프로세스 기동 여부 → 자동 검증 불가 → 사용자 확인 요청 리스트

실패 ≥ 1 건 → AskUserQuestion (강제 진행 / 중단 / 수동 Step 만 출력).

---

## 4단계: 비용 체크포인트

Step 수 평가:
- ≤ 20: 진행
- 20 < n ≤ 50: 로그만
- > 50: AskUserQuestion ("Step {N}개. Light 로 진행 / `/qa-run-deep` 권장 / `--only P1` / 중단")

`--only`, `--sample` 플래그 있으면 즉시 적용.

`--dry-run` 은 여기서 종료 (Step 목록·예상 소요 출력).

**예상 소요**: `step × 3s + 2s evidence`

---

> **[1M 활용]** 다음을 **단일 메시지에서 병렬 호출**:
> - Read: `QA-*.md` (본체), 같은 디렉터리의 가장 최근 `QA-RUN-*.md` 1건
> - Glob: `.mcp.json`, `dirname(QA)/runs/*/` (과거 run 폴더)
> - Bash: `test -f {선수조건 파일}` + `date +%Y%m%d-%H%M`
>
> 순차 호출 대신 병렬로 실행 전 맥락 완성 + 회귀 비교 축을 미리 확보.

## 5단계: Step 순차 실행 + Retry

`run-id = date +%Y%m%d-%H%M`. `runs_dir = dirname(QA)/runs/{run-id}/`. `mkdir -p` 선행.

### 5.1 실행 루프

각 Step:
1. 시작 로그 (`[Step X.Y] 실행 중...`)
2. MCP 시퀀스 순차 호출 (navigate → snapshot → click → wait_for → evaluate 등)
3. assertion 비교:
   - `assertion-eval`: 결과 ↔ 기대값
   - `network-contract`: 네트워크 로그 필터
   - `natural-language`: `manual-pending` 태그 (사용자 확인 섹션으로)
4. 결과: `pass` / `fail` / `flaky` / `manual-pending` / `blocked-manual` / `pass-after-manual` / `fail-after-manual` / `skip-after-block`

### 5.2 Retry

assertion 실패 또는 MCP 예외 → **1회 자동 재시도** (단, §5.4 막힘 감지 신호 시 retry 즉시 중단):
- 2회 모두 실패 → `fail`
- 1실패 + 1성공 → `flaky`
- 2회 모두 성공 → `pass` (재시도 발생은 경고 기록)

### 5.3 stop-on-fail + 실행 간 격리

- `--stop-on-fail` + P1 fail → 즉시 중단, 나머지 `not-run`
- Step 간 페이지 상태 누수 방지: 매 Step 시작 시 초기화 (연속 Step 이 상태 유지 가정 시 생략)

### 5.4 막힘 감지 + 사용자 개입 요청

Step 실행 중 **사람 개입 없이는 진행 불가** 상황 감지 시 즉시 AskUserQuestion. retry 로 우회 금지 — 같은 실패 무한 반복이 가장 큰 반패턴.

**막힘 감지 신호**:
- 로그인 요구 (`/login` URL, password input, "로그인" 텍스트)
- CAPTCHA / reCAPTCHA
- 2FA / OTP
- HTTP 403 연속 3건 이상
- 세션 만료 (401, "세션 만료" 메시지)
- 블로킹 모달 (handle_dialog 누락)
- 파일 업로드 경로 부재
- 외부 SSO 리다이렉트

**대응 플로우**:
1. **Retry 즉시 중단** (§5.2 보다 우선)
2. 현재 상태 기록: URL, 감지 신호, 최근 콘솔 에러 3건
3. AskUserQuestion 즉시:
   - "Step X.Y 에서 {감지 유형} 감지 (`{URL}`). 브라우저에서 수동 처리 후 선택:"
   - 옵션: **수동 완료** (Step 처음부터 1회 재실행) / **이 Step skip** (`blocked-manual`) / **남은 P1 만 실행** / **전체 중단**
4. "수동 완료" 재실행:
   - 성공 → `pass-after-manual`
   - 실패 → `fail-after-manual` (추가 retry 없음)
5. **개입 기록** 수집 (§8.8 회고 입력): Step ID · 감지 신호 · 타임스탬프

**반복 감지 제한**: 같은 유형 3회 이상 → 일괄 처리 모드 ("일괄 수동완료 / 일괄 skip / 전체 중단")

---

## 6단계: 증거 수집 (4계층)

### 6.1 성공 Step
- `screenshot` 1장 (`step-{id}-ok.png`)

### 6.2 실패 Step (4종 전부)
1. `step-{id}-fail.png` — 스크린샷
2. `step-{id}-console.txt` — `console_messages(level=error)`
3. `step-{id}-network.json` — `network_requests` 중 status >= 400 필터
4. `step-{id}-dom.yaml` — `snapshot()` 결과

### 6.3 Flaky Step
- 실패 시도 증거 4종 + 성공 시도 스크린샷

### 6.4 용량 제어

Step 10 마다 `du -sh runs/{run-id}/`. 20MB 초과 시 AskUserQuestion (계속 / 성공 Step 스크린샷 생략 / 중단).

---

## 7단계: 결과 집계 + 회귀 비교 (간이)

### 7.1 Step 결과 테이블

필드: `step-id, category, level, priority, result, duration-ms, evidence, fail-summary`.

카운트: `total, pass, fail, flaky, skip-manual, not-run, manual-pending, blocked-manual, pass-after-manual, fail-after-manual, skip-after-block, interventions, p1-fail`.

### 7.2 회귀 비교 (Light = 최근 1건만)

`dirname(QA)/QA-RUN-*.md` 중 가장 최근 1건만 조인. Deep 의 트렌드 분석은 별도 (`/qa-run-deep`).

비교 결과:
- 새 회귀 (이전 pass → 이번 fail): N건
- fix (이전 fail → 이번 pass): N건
- 만성 flaky (이번 + 이전 모두 flaky): N건

회귀가 누적되어 보이면 안내: "Light 의 회귀 비교는 1회분 한정. 트렌드는 `/qa-run-deep`."

---

> **[메타인지]** 인사이트 집계 직전, 상위 후보 3건에 대해:
> 1. 근거 재점검 (측정치 인용이 `[확신]` 태그를 실제 뒷받침하는가)
> 2. 전제 검증 (6필드가 누락 없이 채워지는가 — 특히 신뢰도·우선순위가 증거로 환원되는가)
> 3. 반대 증거 ("이 발견이 flaky 1회짜리 우연 아닌가? 왜 이미 조치되지 않았나?")

## 8단계: 인사이트 생성 (7카테고리)

각 항목 **6필드 전부** 있어야 리포트 포함:
- 발견 (한 문장)
- 근거 (파일 경로:줄번호 또는 Step ID 집합)
- 액션 (구체 동사)
- 공수 (N시간 / 다음 스프린트)
- 신뢰도 (`[확신]` / `[추정]` / `[가설]`)
- 우선순위 (`[P1]` / `[P2]` / `[P3]`)

### 8.1 놓친 케이스

**트리거**: 실행 매트릭스 행 ≠ 이론적 카디널리티, 또는 입력 필드 타입 체크리스트에서 빠진 것.

### 8.2 숨은 의존성

**트리거**: 서로 다른 Step 이 같은 URL·DOM·전역 state 참조.

### 8.3 맹점

**트리거**: 카테고리 × Level 커버리지 매트릭스의 빈 셀.

### 8.4 반복 실패 패턴

**트리거**: N ≥ 2 Step 이 공통 원인.

### 8.5 도메인 규칙 구멍

**트리거**: 격리 키(있는 프로젝트만) 미확인, 상태 전이 미전수, 승인 반려 경로 누락, 이벤트 리스너 반영 미확인 등 (`.local.claude/biz-rules.md` 의 도메인 카테고리 자동 활용).

**해당 없음**: biz-rules.md 가 비어있거나 도메인 카테고리가 없으면 "해당 없음" 한 줄 대체.

### 8.6 인프라·E2E 조건

**트리거**: 외부 API 응답 지연, 소요 분산 큼, 다국어·모바일 미검증.

### 8.7 다음 릴리즈 개선 액션

§8.1~§8.6 의 액션을 **P1/P2/P3 재분류** + 중복 해소 + 의존 순서 명시. "P1 2건 이상이면 블로킹 순서 명시".

### 8.8 사용자 개입 회고 — 다음 run 자동화 제안

**트리거**: 이번 run 에서 `blocked-manual`, `pass-after-manual`, `fail-after-manual`, `manual-pending`, `skip-manual`, `skip-after-block` 중 1건 이상.

**개입 유형별 자동화 가능성**:
| 개입 유형 | 자동화 가능성 | 권장 조치 |
|---------|-------------|----------|
| 로그인 | 높음 | QA §0 에 "세션 미리 확보" + seed 명시 |
| CAPTCHA | 낮음 | dev/local 에선 비활성 플래그 요청 |
| 2FA / OTP | 중간 | OTP 시크릿 환경변수 + TOTP 자동 생성 |
| 권한 부족 연쇄 | 높음 | seed 계정 권한 매트릭스 |
| 세션 만료 | 높음 | run 시작 시 세션 유효성 선행 체크 |
| 블로킹 모달 (QA 누락) | 높음 | QA 에 `handle_dialog(true)` 추가 |
| 파일 업로드 경로 부재 | 중간 | QA §0 에 fixture 경로 명시 |
| 자연어 기대값 | 중간 | Deep 의 AI 시각 판정 사용 또는 구체 assertion 으로 재작성 |

**항목 포맷** (개입 1건당):
```
- **[개입-N][확신|추정][P1|P2|P3]** Step X.Y {감지 유형} (YYYY-MM-DD HH:MM)
  - 유형: {로그인|CAPTCHA|...}
  - 자동화 가능성: {높음|중간|낮음}
  - 근거: {QA 선수 조건 경로 / 감지 신호 인용}
  - 다음 run 개선안 (QA): ```{체크박스 또는 Step 초안}```
  - 공수: QA 수정 N분 + 환경 셋업 M분
```

### 8.9 인사이트 부재 시

모든 카테고리 비어 있으면:
> 이번 run 에서는 측정 기반 인사이트를 뽑을 만한 신호가 없었습니다. 모든 Step 이 증거만으로 설명 가능.

---

## 9단계: 자기 검증 + AskUserQuestion

초안 작성 직후 **검토자 관점** 재읽기 (1회 고정).

### 9.1 체크리스트
- [ ] 각 인사이트 6필드 전부 있는가
- [ ] `[확신]` 이 측정치 기반인가
- [ ] `[가설]` 남발 → `[추정]` 강등
- [ ] 행동 가능한 액션인가 ("검토하자" 금지)
- [ ] 회귀 섹션이 실제로 이전 run 조인했는가 (있을 시)
- [ ] 한눈에 (배너) 가 30초 내 상태 파악 가능한가
- [ ] 사용자 개입 1건 이상이면 §8.8 회고가 작성됐는가

### 9.2 AskUserQuestion

질문: "리포트·인사이트 재읽기 완료. 문제 발견?"
옵션: 없음(저장) / 실패 원인 재분석 / 인사이트 근거 부족 / 회귀 비교 오류 / 기타

2~기타 답변 시 **해당 섹션만** 수정. 1회만.

---

## 10단계: 리포트 저장

### 10.1 파일 경로
```
dirname(QA-*.md)/QA-RUN-{기능명}-{YYYYMMDD-HHMM}.md
```

### 10.2 Frontmatter

```yaml
---
created: <ISO-8601 with timezone>
category: qa-run
retention: 90-days
run-id: <YYYYMMDD-HHMM>
mode: light
source: <QA-*.md 상대경로>
source-qa-version: <QA frontmatter created>
domain: standalone | domain-native
recommended-runner-was: light | deep   # QA 가 권장한 모드 (실제 실행과 다를 수 있음)
summary:
  total: N
  pass: N
  fail: N
  flaky: N
  skip-manual: N
  not-run: N
  manual-pending: N
  blocked-manual: N
  pass-after-manual: N
  fail-after-manual: N
  skip-after-block: N
  interventions: N
  p1-fail: N
previous-run: <있을 때만>
regression:
  new-failures: N
  fixed: N
  chronic-flaky: N
---
```

### 10.3 본문 구조

```markdown
# [기능명] QA 실행 리포트 · run-{run-id} (LIGHT)

> `/qa-run-light`. 원본 QA: [...](./...)
> 증거: `runs/{run-id}/`
> Deep 분석 필요 시: `/qa-run-deep {QA 경로}`

## 0. 한눈에 (배너)
## 1. Step 별 결과 (테이블)
## 2. 실패 상세
## 3. Flaky Step
## 4. 수동 / 개입 기록
   4.1 수동 Step 체크리스트 (skip-manual)
   4.2 실시간 개입 기록 (blocked-manual — 시각·유형·URL·Step ID)
## 5. 회귀 비교 (이전 1건)
## 6. 인사이트 — 7카테고리
   6.1 놓친 케이스
   6.2 숨은 의존성
   6.3 맹점
   6.4 반복 실패 패턴
   6.5 도메인 규칙 구멍 (standalone: "해당 없음")
   6.6 인프라·E2E 조건
   6.7 다음 릴리즈 개선 액션 (P1/P2/P3)
   6.8 사용자 개입 회고
## 7. 스킬이 판단 못 한 것
```

---

## 11단계: 최종 콘솔 출력

```
[OK] qa-run-light 완료 (run-id: {run-id})

소스: {QA 파일} (recommended: {light|deep})
실행: {pass}/{total} Pass, {fail} Fail, {flaky} Flaky, {skip-manual} 수동대기
[URGENT] P1 실패: {p1-fail}건
**사용자 개입**: {interventions}건 — §6.8 회고 참조

**회귀** (이전 1회 대비): {new-failures} 회귀, {fixed} fix

**P1 액션 상위 3개**:
  1. {액션} ({공수}) — {확신/추정/가설}
  2. ...
  3. ...

**리포트**: {경로}
**증거**: {경로}

**Deep 분석 권장 신호** N건 감지 — 다음에 /qa-run-deep 고려
```

부분 실행은 제목에 `[PARTIAL]`.

---

## 에러·엣지 케이스

| 상황 | 탐지 | 대응 |
|------|------|------|
| MCP Playwright 미설치 | 첫 `browser_navigate` 에러 | "Playwright MCP 서버 active 확인" 안내 후 중단 |
| 로그인·CAPTCHA·세션만료·블로킹모달 | §5.4 막힘 감지 | **즉시** AskUserQuestion (재시도 금지) + §8.8 회고 입력 |
| 같은 막힘 3회 이상 반복 | 개입 카운터 per 유형 | 일괄 처리 모드 |
| 서버 미기동 | `console_messages` 에 `Failed to fetch` 다수 | 선수 조건 재검토 AskUserQuestion |
| QA 포맷 위반 | Step 매치 < 80% | AskUserQuestion (재생성/강행/중단) |
| 세션 끊김 | 컨텍스트 한계 | 부분 리포트 저장, `[PARTIAL]` |
| 스크린샷 용량 폭발 | du > 20MB | AskUserQuestion |
| 매트릭스 확장 실패 | `{변수}` 매칭 없음 | 행 skip + 경고 |
| natural-language 기대 다수 | 5건 이상 | Deep 권장 안내 |
| recommended-runner: deep 인데 light 호출 | §1.1 | AskUserQuestion (Light 강행 / Deep 전환 / 중단) |

---

## 주의 사항

- **원본 QA-*.md 불변** — 읽기 전용
- **서브에이전트 위임 금지**
- **측정 vs 추론 구분** — `[확신]` 은 인용, `[추정]`·`[가설]` 은 해석
- **인사이트 비어 있을 수 있음** — §8.9 로 정직하게 표기
- **dry-run 권장** — 처음 실행하는 QA 는 `--dry-run` 으로 Step 확인

---

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬 |
|---|---|---|
| QA 체크리스트(매트릭스) 설계·생성 | `/qa` | [다루지 않음] |
| 1M 맥락 교차·AI 시각 판정·예측 QA·메타 분석 (심층) | `/qa-run-deep` | [다루지 않음] |
| 단일 QA 파일 + 실행 증거로 빠른 MCP 실행 + 7카테고리 경량 리포트 | 이 스킬 | [핵심] |

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[사용자 개입 필요]** 로그인·CAPTCHA 감지
- 신호: Playwright 스냅샷에 로그인 폼·OTP·CAPTCHA 요소 또는 302 인증 리다이렉트
- 대응: 실행 중단 → 사용자에게 직접 로그인 요청 → 재개 후 해당 스텝 재시도 (최대 2회)

**[데이터 결함]** QA 매트릭스 `manual-pending` 비율 50% 이상
- 신호: 매트릭스 행 중 `manual-pending` 또는 미분류 자동화 가능 여부가 과반
- 대응: 실행 전 경고 출력 — "자동화 가능 시나리오가 적습니다, `/qa` 재실행으로 매트릭스 보강 권장"
