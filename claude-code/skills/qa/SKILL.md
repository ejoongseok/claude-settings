---
name: qa
description: "PRD/SRS/TODO 산출물을 읽어 Playwright MCP로 재현 가능한 QA 체크리스트를 생성합니다. Happy·경계·예외·부정·데이터변형·보안·동시성·i18n 카테고리와 입력 필드별 카디널리티 변형까지 자동 도출하는 QA 전문가 수준의 검증 시퀀스."
argument-hint: "<srs-or-prd-or-todo-path> [--level 1|2|3|4|5|6] [--categories happy,boundary,exception,...]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(mkdir *, ls *, date *, wc *, dirname *, grep *, find *)
effort: max
disable-model-invocation: true
---

체크리스트 생성 전담. 실제 MCP 호출 실행은 `/qa-run-light` 또는 `/qa-run-deep` 가 담당.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| PRD/SRS | `.local.claude/prd/`, `.local.claude/srs/` | 선택 | 기능 요구사항 부재 — 일반 QA 매트릭스만 |
| 이전 QA | `.local.claude/qa/` 또는 같은 디렉터리 | 선택 | 신규 QA 기본 모드 |
| 기존 테스트 | `**/tests/`, `**/test/` | 선택 | 회귀 매트릭스 생략 |

## 경쟁 스킬과 역할 경계

| 이럴 때 | 어떤 스킬 |
|--------|---------|
| 회의·요청·아이디어 → 비즈니스 맥락 문서 | `/prd` |
| PRD → 기술 명세 + 경계·예외 조건 | `/srs` |
| SRS → Outside-In 개발 순서 | `/todo` |
| **PRD/SRS/TODO → QA 체크리스트 (Happy·경계·예외·부정·변형·보안·동시성·i18n)** | **`/qa` (본 스킬)** |
| 배포 전 수동 체크리스트 | `/deploy-checklist` |
| 누적 문서 → AI/사람 두 독자층 재구성 + 메타 분석 | `/dualize-docs` |

## 설계 원칙

- **QA 전문가 관점**: "기능이 돌아가는가" 에서 멈추지 않음. "얼마나 깨뜨릴 수 있는가"·"사용자가 할 수 있는 모든 입력 변형을 처리하는가" 까지
- **카테고리 × Level 매트릭스**: 하나의 기능에 대해 여러 축에서 Step 을 전개 (단일 시나리오 아님)
- **입력 필드별 체계적 변형**: 필드 타입마다 Happy/Boundary/Exception/Negative/Special 자동 생성
- **카디널리티 축**: 조회·선택·업로드 기능마다 0/1/N/Max 변형
- **도메인 분리 감지**: 프로젝트 본 시스템과 무관한 독립 컴포넌트(데모·포털·크롤러 등)면 `biz-rules.md` 의 도메인 점검 카테고리 자동 활용 **생략**하고 대체 체크 삽입
- **수동 Step 허용**: 제목에 `(MCP 밖, 수동)` 표기 시 MCP 시퀀스·실패 대응 요구 면제 (빌드·촬영·OS 조작 등)

---

## 1단계: 입력 파싱

`$ARGUMENTS` 분리:
- 첫 번째 토큰 = 파일 경로 (필수). `SRS-*.md` / `PRD-*.md` / `TODO-*.md`
- `--level N` (선택, 1~6)
- `--categories ...` (선택, 아래 카테고리 CSV. 미지정 시 기능 성격에 따라 자동)

사용법 안내:
```
사용법: /qa <file-path> [--level N] [--categories A,B,C]
Level:      1 조회 / 2 CRUD / 3 상태 전이 / 4 이벤트 / 5 워크플로우(승인·검토·배포 등) / 6 E2E
카테고리:   happy / boundary / exception / negative / data-variation
           security / concurrency / i18n / accessibility
미지정 시: 기능 성격에 맞는 카테고리 자동 선택
```

---

## 2단계: 파일 유형 판별 + 관련 문서 + 도메인 분리 감지

### 2.1 파일명 prefix 분기

| Prefix | 주 활용 |
|--------|--------|
| `SRS-` | 경계조건 / 예외흐름 / 데이터 명세 / 품질 (QA 금맥) |
| `PRD-` | §4 시나리오 / §5 요구사항 / §6 성공 기준 |
| `TODO-` | Phase 별 "확인" + "작업" 설명 |

**TODO 입력 시 PRD 는 배경 맥락만 참조**. QA Step 은 TODO 기준. (SRS 가 없으면 경계/예외 자동 추론 필요)

### 2.2 관련 문서 수집

같은 프로젝트 디렉터리에서 자동 Glob:
```bash
PROJECT_DIR=$(dirname "<input>")
find "$PROJECT_DIR" -maxdepth 1 -name "PRD-*.md" -o -name "SRS-*.md" -o -name "TODO-*.md" -o -name "POC-*.md" -o -name "AS-IS.md" -o -name "STATUS.md"
find .local.claude/projects -name "*regression*.md" 2>/dev/null
```

### 2.3 **도메인 분리 감지**

다음 신호 감지 시 "독립 컴포넌트"로 판정하고 프로젝트 공통 검증 생략:
- 문서에 "독립 프로젝트", "별도", "본 시스템 코드 수정 없음", "standalone" 문구
- 기술 스택이 프로젝트 기본 스택과 무관 (WinForms/Electron/순수 HTML 등)
- API 호출이 아닌 `file://` 또는 mock 데이터
- 프로젝트의 도메인 점검 카테고리 (`biz-rules.md`) 와 무관 — 격리·이벤트·상태 전이 등 용어 부재

독립 프로젝트 판정 시 §2 공통 검증이 다음으로 대체:
- 콘솔 에러 0건
- 리소스 404 0건
- 한글 렌더 정상
- 빈 상태 안내

### 2.4 기존 QA 파일 존재 시 덮어쓰기 확인

AskUserQuestion: "기존 QA-*.md 가 있습니다. 덮어쓸까요?" → 승인 시 진행.

---

> **[Opus 4.7 / 1M 활용]** 서브 분할 없이 메인에서 직접 **다중 파일 동시 로드** 후 교차:
> - 로드: `PRD-{기능}.md`, `SRS-{기능}.md`, 기존 `QA-{기능}.md` (있으면), `.local.claude/biz-rules.md`
> - 교차: {PRD 시나리오 vs SRS 경계조건 누락 탐지}, {biz-rules 도메인 카테고리 vs 기존 QA 커버리지 갭}

## 3단계: 통합 이해 (메인 컨텍스트 Read)

서브에이전트 위임 금지. Opus 4.7 1M context 로 입력 + 관련 문서 + 필요 시 관련 컨트롤러·Svc·DTO 코드까지 Grep 후 Read.

추출 타겟 (QA 관점):
- [ ] 모든 **입력 필드** (이름·타입·제약·기본값·유효성 규칙)
- [ ] **상태 전이 경로** (허용 전이 + 허용 안 된 전이)
- [ ] **경계값** (길이·수량·크기·시간·페이지)
- [ ] **예외 흐름** (에러 코드·메시지·복구 경로)
- [ ] **의존 외부 시스템** (메신저 연동·검색 엔진·파일 저장소·승인 엔진 등)
- [ ] **권한 조건** (역할별 가시성·CRUD 권한)

---

## 4단계: QA 카테고리 체계

### 4.1 카테고리 8종

| # | 카테고리 | 의도 | 전형적 Step |
|---|---------|------|-----------|
| 1 | **Happy** | 정상 흐름이 끝까지 동작 | 중간값 입력 → 저장 → 목록 반영 |
| 2 | **Boundary** | 경계값 근처에서 정확 | Max 길이, MIN 수량, 페이지 경계 |
| 3 | **Exception** | 실패 경로가 올바른 에러 메시지 반환 | 중복 등록·권한 없음·타임아웃 |
| 4 | **Negative** | 비정상 입력을 적절히 거부 | 빈값·null·잘못된 형식·금지 문자 |
| 5 | **Data Variation** | 입력 개수·조합 다양성 | 0건·1건·N건·중복·혼합 |
| 6 | **Security** | 권한·주입 공격 방어 | 격리 우회·SQL 주입·XSS·CSRF |
| 7 | **Concurrency** | 동시성·경쟁 상태 | 동시 저장·락·이벤트 재입력 |
| 8 | **i18n** | 다국어·특수문자 | 한글·영문·이모지·유니코드 |

### 4.2 카테고리 × Level 기본 매트릭스

공란은 기본 생략. `--categories` 로 강제 추가 가능.

```
           L1 조회  L2 CRUD  L3 전이  L4 이벤트  L5 워크플로우  L6 E2E
Happy         ✓       ✓       ✓        ✓          ✓       ✓
Boundary      ✓       ✓       ·        ·          ·       ·
Exception     △       ✓       ✓        ✓          ✓       ✓
Negative      ✓       ✓       △        △          △       △
DataVar       ✓       ✓       ·        △          ·       △
Security      ✓       ✓       ✓        ✓          ✓       ✓
Concurrency   ·       △       ✓        ✓          ✓       ✓
i18n          ✓       ✓       ·        ·          ·       ·
```
(`✓` 기본 포함, `△` 기능에 해당 시, `·` 생략 권장)

### 4.3 입력 필드별 변형 자동 생성 규칙

입력 필드를 식별하면 **필드 타입별 표준 변형** 자동 생성:

#### String
- Happy: 정상 값 (예: "홍길동")
- Boundary: 길이 1 / Max / Max+1 (거부 확인)
- Negative: `""` / `" "` (공백만) / `null`
- Special: 한글·영문·숫자 혼합 / 특수문자(`'<>/\&`) / 이모지(`[이모지]`)
- Injection (Security): `'; DROP TABLE ...` / `<script>alert(1)</script>`

#### Number
- Happy: 중간값
- Boundary: 0 / MIN / MAX / MIN-1 / MAX+1
- Negative: 음수(양수 필드) / 소수(정수 필드) / 지수 표기(`1e10`)
- Invalid: 문자 혼입 / 천단위 구분자 / 통화 기호

#### Date / DateTime
- Happy: 오늘
- Boundary: 과거 100년 / 미래 100년 / 2월 29일(윤년) / 2월 30일(존재 안 함)
- Invalid: 31일인 2·4·6·9·11월 / 잘못된 형식(`2026-13-01`)
- Timezone: UTC vs KST 경계 (09시 전후)

#### Select / Dropdown
- Happy: 첫 옵션 / 중간 / 마지막
- Boundary: 미선택 상태로 제출
- Negative: 비활성(disabled) 옵션 강제 선택 시도
- DataVar: 옵션 없음 상태 (로딩 실패)

#### Radio / Checkbox
- Happy: 각 선택지 1회씩
- Boundary (Checkbox): 0개 / 1개 / 전체 / "전체 선택" 토글
- Negative: 필수인데 미선택

#### File Upload
- Happy: 허용 확장자·중간 크기
- Boundary: 0 bytes / Max 크기 / Max+1 bytes (거부)
- Negative: 금지 확장자 (`.exe`) / 손상 파일 / 확장자 위조(매직바이트 다름)
- Security: 경로 조작 (`../../etc/passwd`) / 거대 파일 (DoS)

#### Textarea (자유 입력)
- Happy: 일반 문장
- Boundary: Max 길이 / 개행 문자 다수
- Negative: 빈 상태 (필수 시)
- Special: 긴 URL / 마크다운 / HTML 태그

### 4.4 카디널리티 변형 (조회·선택·업로드)

| 시나리오 | 0건 | 1건 | N건 | 페이지 경계 | Max | 중복 |
|---------|-----|-----|-----|-----------|-----|------|
| 목록 조회 | "결과 없음" 안내 | 단일 행 | 여러 행 | pageSize ± 1 | 10,000건 | - |
| 다중 선택 → 일괄 처리 | 버튼 disabled | - | 여러 선택 | 최대 선택 수 | - | 같은 ID 2번 |
| 파일 업로드 | - | 단일 | 복수 | 최대 n개 | 용량 Max | 같은 파일명 |
| 검색 | "결과 없음" | - | - | 페이지 경계 | - | - |

### 4.5 상태 전이 변형 (Level 3~5)

- Happy: 허용 전이 순차 (예: 요청 → 검토 → 합의 → 승인)
- Exception: **허용 안 된 전이 시도** — 서버 거부 확인 (예: 요청 → 승인 직행)
- Concurrency: 동시에 두 사용자가 같은 건 전이 → 낙관적 락 충돌
- Rollback: 중간 실패 시 이전 상태 복귀 확인

### 4.6 우선순위 결정 (Step 헤더에 텍스트 마커 표기 필수)

각 Step 생성 시 다음 규칙으로 P 등급 결정. Step 제목 끝에 `[URGENT]P1` / `[참고]P2` / `[정상]P3` 표기:

| 등급 | 표기 | 조건 |
|------|------|------|
| P1 | [URGENT]P1 | Happy + Level 1·2 (조회/CRUD 정상 흐름) / 워크플로우 (승인·검토 등) 핵심 경로 / 보안 (격리 키·권한·주입 — biz-rules.md 도메인 카테고리 자동 활용) / 데이터 손실 가능 케이스 |
| P2 | [참고]P2 | Boundary / Exception (정상 운영 중 재현 빈도 있음) / 상태 전이 (Happy 외) / 카디널리티 0·N |
| P3 | [정상]P3 | i18n / 이모지 / 접근성 / Negative 중 극단값 (지수표기·금지문자 등) / 카디널리티 Max·중복 |

**미지정 시 P2 기본값** — qa-run 의 우선순위 필터링이 동작하지 않으므로 반드시 표기.

---

## 5단계: 프로젝트 특화 공통 체크 (도메인 분리 시 생략)

### 5.1 프로젝트 본 시스템일 때 (도메인 점검 카테고리 자동 활용)

프로젝트 컨텍스트 (`CLAUDE.md`, `biz-rules.md`) 가 정의한 공통 체크를 모든 Step 에 암묵 적용:
- **도메인 점검 카테고리** (`biz-rules.md` 의 도메인 규칙): 격리·승인·정합성·이벤트 등 프로젝트가 정의한 모든 항목 자동 검증. 부재 시 이 항목 생략
- **콘솔 에러**: 0건
- **네트워크 5xx**: 0건 (의도된 에러 케이스 제외)
- **불필요 중복 호출**: 같은 GET 3회 이상 반복 시 경고
- **이벤트 발행** (Level 4~): `browser_network_requests` 또는 내부 로그로 리스너 트리거 확인
- **상태 전이 후 DB 일치성**: `browser_evaluate` 로 화면 상태 확인 + (가능 시) 관리자 페이지로 DB 반영 재확인

### 5.2 독립 컴포넌트일 때

대체 공통 검증:
- 콘솔 에러 0건
- 리소스 404 0건 (CSS·JS·이미지)
- 한글 렌더 정상
- 빈 상태 안내 문구
- 폰트 폴백 (특수 문자 깨지지 않음)
- 키보드 접근성 (Tab 키로 주요 버튼 순회, `--categories accessibility` 시)

---

## 6단계: 체크리스트 구조 설계

### QA-*.md 전체 구조

```markdown
---
created: YYYY-MM-DD
category: qa-automation
retention: project-end
source: {입력 경로}
related: [...]
level-range: 1~N
categories: [happy, boundary, exception, ...]
domain: project-native | standalone
recommended-runner: light | deep        # qa-run-light/qa-run-deep 추천
recommended-runner-reason: "..."        # 추천 근거 한 문장
---

# [기능명] QA 체크리스트 · Playwright MCP 시퀀스

> 이 문서는 `/qa` 스킬 산출. MCP Playwright 로 재현 가능.
> 추천 실행기: `/qa-run-{recommended-runner}` (근거: {recommended-runner-reason})
> 원본: ... | 관련: ...

## 0. 선수 조건
## 1. 검증 목표 + 카테고리 커버리지 매트릭스
## 2. 공통 검증 (프로젝트 본 / 독립 컴포넌트 분기)
## 3. Step 별 검증 시퀀스
  ### 3.1 Happy Path
  ### 3.2 Boundary
  ### 3.3 Exception
  ### 3.4 Negative
  ### 3.5 Data Variation (카디널리티)
  ### 3.6 Security
  ### 3.7 Concurrency (해당 시)
  ### 3.8 i18n (해당 시)
## 4. 상태 전이 추적 (Level 3+)
## 5. 실패 패턴 카탈로그
## 6. 수동 Step (MCP 밖)
## 7. 회귀 시나리오 연계
## 8. 스킬이 판단 못 한 것
```

### Step 단위 포맷

```markdown
### Step X-N: [카테고리] - [이름] — Level L [URGENT]P1
**목적**: {SRS §Y 근거 + 한 문장}
**카테고리**: Happy / Boundary / Exception / Negative / ...
**우선순위**: P1 (블로킹) / P2 (중요) / P3 (보강) — 텍스트 마커 표기 필수
**사전 상태**: DB 상태 / UI 진입점

**MCP 시퀀스**:
- [ ] `browser_navigate`: {URL}
- [ ] `browser_snapshot` — ref 확보
- [ ] `browser_fill_form`: 각 필드 입력 값 명시
  - `#userId` = "test01"
  - `#password` = "..."
- [ ] `browser_click` [ref=submit]
- [ ] `browser_wait_for` [text="완료" or textGone="로딩중"]
- [ ] `browser_evaluate`: `() => ...`
  - **기대**: ...
- [ ] `browser_network_requests` → POST /api/...
  - **기대**: HTTP 200, 도메인 점검 카테고리 (biz-rules.md) 모두 통과
- [ ] `browser_take_screenshot` [filename=qa-X-N.png]

**성공 판정**: 위 체크 전부
**실패 시 대응**:
- 증상 A → 원인 B → 조치 C

**입력 값 매트릭스** (해당 Step 이 여러 변형 테스트 시):
| 케이스 | 입력 | 기대 |
|--------|-----|------|
| 정상 | "홍길동" | 성공 |
| 빈값 | "" | 400 "이름 필수" |
| Max+1 | "가" × 51 | 400 "50자 이내" |
| 이모지 | "홍[이모지]길동" | 성공 (지원 여부 확인) |
```

### 수동 Step 표기

제목에 `(MCP 밖, 수동)` 포함 시 스킬 자체 검증에서 MCP 시퀀스·실패 대응 요구 면제. 수동 체크리스트만 허용:
```markdown
### Step Z: 빌드·배포 (MCP 밖, 수동)
**수동 체크리스트**:
- [ ] `mvn install -DskipTests`
- [ ] `dotnet publish -c Release`
- [ ] exe 더블클릭 → 앱 실행 확인
```

### 6.1 실행기 추천 결정

체크리스트 작성 직후, 다음 신호로 `recommended-runner` 자동 결정:

**`deep` 권장 조건** (하나라도 해당):
- 도메인 = `project-native` AND Level ≥ 4 Step 존재 (이벤트·결재 흐름)
- P1 Step 3개 이상 (블로킹 다수 → Deep 의 예측 QA·대안 비교 가치 큼)
- 자연어 기대값 다수 ("자연스럽게 정렬", "깨지지 않음" 등 5건 이상 → AI 시각 판정 필요)
- 결재 경로 (Level 5) Step 존재
- 예상 Step 수 > 50

**그 외**: `light` 권장 (기본값)

**근거 문구 (`recommended-runner-reason`)**:
- deep 사례: `"project-native + Level 5 결재 경로 + 자연어 기대값 7건"`
- light 사례: `"standalone + Step 18 + 모든 기대값이 assertion-eval 형식"`

**한 줄 안내 출력**:
```
**추천 실행기**: /qa-run-{light|deep} <QA-*.md 경로>
   근거: {recommended-runner-reason}
   다른 모드 강제: /qa-run-{반대} <경로>
```

---

## 7단계: 출력 저장

```bash
PROJECT_DIR=$(dirname "<input>")
FEATURE_NAME={입력 파일에서 prefix 제거}
OUT="$PROJECT_DIR/QA-${FEATURE_NAME}.md"
```

파일명:
- `SRS-{기능명}.md` → `QA-{기능명}.md`
- `TODO-{기능명}.md` → `QA-{기능명}.md`

---

> **[Opus 4.7 / 메타인지]** 최종 매트릭스 완성 직전, 핵심 결론 Top 3(P1 Step 선정·필드 커버리지 판단·도메인 분리 판정)에 대해:
> 1. 근거 재점검 (SRS의 경계조건·예외흐름 인용 vs 생성 Step의 실제 매핑)
> 2. 전제 검증 (6필드 — 목적·카테고리·우선순위·사전 상태·MCP 시퀀스·실패 대응 — 이 Step마다 모두 있는가)
> 3. 반대 증거 ("왜 이 케이스를 P2 가 아닌 P1 으로 올렸나? 현재 커버리지가 충분하다면 빠진 필드 변형은 없나?")

## 8단계: 자체 검증

### 8.1 구조 체크 (Bash) — 정규식 개선

```bash
# MCP 도구 추출 (백틱 이스케이프 문제 해결)
grep -oE 'browser_[a-z_]+' "$OUT" | sort -u

# 화이트리스트 대조
WHITELIST="browser_navigate browser_navigate_back browser_click browser_type browser_fill_form browser_snapshot browser_take_screenshot browser_evaluate browser_wait_for browser_console_messages browser_network_requests browser_hover browser_select_option browser_press_key browser_drag browser_file_upload browser_handle_dialog browser_tabs browser_resize browser_close"

# Step 제목 유연 매칭 (괄호 보조 허용)
grep -nE '^### Step [A-Z0-9-]+(\s+\([^)]+\))?(\s*:)' "$OUT"

# 수동 Step 은 면제
grep -nE '\(MCP 밖, 수동\)' "$OUT"

# 카테고리 커버리지
for cat in Happy Boundary Exception Negative "Data Variation" Security Concurrency i18n; do
  count=$(grep -c "^### Step .*\[$cat\]\|\*\*카테고리\*\*: $cat" "$OUT")
  echo "  $cat: $count Steps"
done
```

### 8.2 입력 필드 커버리지

입력 파일에 언급된 필드 목록을 추출(`DTO`/`ReportParameters`/"입력"/"파라미터")하고, QA 내에 각 필드가 **최소 Happy + 1개 이상 변형 케이스**로 등장하는지 체크:
```
필드 `userId`:
  - Happy 커버 ✓
  - Boundary 커버 ✓
  - Negative 커버 ✗ ← 경고: null/빈값 케이스 누락
```

### 8.3 카디널리티 커버리지

조회·선택·업로드 기능 감지 시 0/1/N 변형 모두 있는지:
```
조회 "drive-list":
  - 0건 ✓
  - 1건 ✓
  - N건 ✓
  - 페이지 경계 ✗ ← 경고
```


### 8.4 LLM 자기 검증 재읽기 (강제 체크포인트)

AskUserQuestion 으로 명시 확인:
```
산출물 재읽기 완료. 문제 발견:
  - "없음 (리포트 진행)"
  - "Happy 케이스만 있고 경계/예외 부족"
  - "입력 필드별 변형 누락"
  - "수동 Step 이 MCP 시퀀스로 잘못 작성됨"
  - "도메인 점검 카테고리 (biz-rules.md) 적용 상태 확인 필요"
  - "기타"
```

---

## 9단계: 결과 리포트

```
[OK] /qa 완료

입력: <path>
유형: SRS / PRD / TODO
도메인: 프로젝트 본 시스템 / 독립 컴포넌트
관련 참조: N 파일

→ 산출: {PROJECT_DIR}/QA-{기능}.md
  Step M개 (Level L~M, 카테고리: Happy·Boundary·Exception·...)
  우선순위: [URGENT]P1 N건 / [참고]P2 N건 / [정상]P3 N건
  입력 필드 N개 × 평균 K 변형
  카디널리티 커버: 0/1/N/Max

**추천 실행기**: /qa-run-{light|deep} {QA 경로}
  근거: {recommended-runner-reason}

**자체 검증**:
  ✓ MCP 도구 화이트리스트 통과
  ✓ Step 완전성 (카테고리·목적·시퀀스·성공·실패)
  ✓ 우선순위 표기 100% ([URGENT]P1/[참고]P2/[정상]P3)
  ✓ 필드 커버리지 (각 필드 Happy + 1 변형 이상)
  ✓ 카디널리티 커버리지 (조회 0/1/N/경계)
  ✓ 공통 검증 (도메인 분기 자동)
  [WARN] {발견된 경고 나열}

**다음 단계**:
  - MCP 실측: /qa-run-{light|deep} {QA 경로}
  - 재생성: /qa <path>
```

---

## 주의 사항

- 스킬은 MCP 를 직접 호출하지 않음 — 체크리스트 생성만
- 기존 QA 덮어쓸 때 사용자 확인 필수
- 독립 프로젝트 감지는 휴리스틱 — 오분류 시 `--categories` 로 명시 수정
- 입력 필드 추출이 어려운 문서(TODO 만 있고 SRS 없음)는 PRD 시나리오에서 추정


## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[도메인 특수성]** standalone 모드 감지
- 신호: `biz-rules.md` 부재 또는 도메인 규칙 섹션 전체가 "도메인 규칙 없음"으로 명시
- 대응: biz-rules 도메인 규칙 점검 스킵, 기능 명세 기반 QA 매트릭스만 생성

**[데이터 결함]** SRS/PRD 작성일이 30일 이상 경과
- 신호: 스펙 문서 `updated` 메타가 오늘(2026-04-21) 기준 30일+ 또는 `[stale]` 태그
- 대응: "SRS stale — 현재 동작과 확인 필요" 태그를 매트릭스 상단에 추가, 불일치 의심 항목은 `[need-verify]` 표시
