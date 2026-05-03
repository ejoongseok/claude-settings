# Claude-code-settings

Claude Code 를 업무에 본격 활용하기 위한 **스킬·계약·메타-인프라** 모음.

52개 스킬 + 계약 문서 + 메타-스킬 (`/skill-check`, `/skills-guide`) 로 구성. 신규 프로젝트에 바로 적용 가능하며, 받은 후 자기 도메인에 맞춰 점진 커스텀.

## 무엇이 들어있나

```
Claude-code-settings/
├── README.md         (이 파일)
├── CONTRACT.md       스킬 작성 단일 진실 원천 (12 항목)
├── skills/           52개 스킬 (CONTRACT 100% 준수)
└── agents/           특화 서브에이전트
```

### 스킬 카탈로그 (52개)

8 그룹으로 분류 (`/skills-guide` 가 자동 생성):

| 그룹 | 대표 스킬 |
|------|---------|
| **신규 프로젝트 진입** | `/on-boarding`, `/setup-guide`, `/skill-check`, `/skills-guide` |
| **진단 (관점별 정기 보고)** | `/business-diagnosis`, `/product-diagnosis`, `/tech-diagnosis`, `/delivery-diagnosis`, `/security-diagnosis`, `/growth-diagnosis`, `/data-diagnosis` |
| **작성·생성** | `/prd`, `/srs`, `/todo`, `/pr`, `/issue`, `/draft`, `/adr`, `/poc`, `/brainstorm`, `/rfc`, `/pm-brief` |
| **리뷰·검증** | `/review`, `/team-review`, `/qa`, `/qa-run-light`, `/qa-run-deep`, `/convention-audit`, `/deploy-checklist` |
| **회고·학습** | `/daily`, `/daily-todos`, `/learn`, `/memo`, `/meeting-notes`, `/briefing` |
| **데이터·고객·팀 관리** | `/biz-rules`, `/customer-profile`, `/cs`, `/people`, `/coaching`, `/leadership`, `/analyze-request` |
| **정원·정리** | `/garden`, `/absorb`, `/parse-doc`, `/dualize-docs`, `/optimize-claude-md`, `/analyze-dir` |
| **메타** | `/skill-check`, `/skills-guide` |

## 핵심 개념 4가지

### 1. CONTRACT.md = 단일 진실 원천

모든 스킬이 따라야 할 12 항목 계약. frontmatter·본문 구조·도메인 가정 외부화·분량 임계·검증 시나리오 등 정의. 신규 스킬 추가 시 이 계약을 먼저 읽고 작성.

### 2. Tier 1/Tier 2 분리 (도메인 가정 외부화)

스킬 본문에 **도메인 가정을 박지 않는다**. 외부 데이터로 위임:

| Tier | 영역 | 예시 |
|------|------|------|
| Tier 1 (도메인 무관) | 본문에 박힘 | 페이징·N+1·SQL injection·일반 워크플로우 |
| Tier 2 (도메인 특화) | `biz-rules.md` 의 도메인 카테고리 섹션 위임 | 멀티테넌트 격리·승인 연동·도메인 정합성 |

**장점**: 신규 프로젝트는 빈 `biz-rules.md` 로 시작 → 작업하며 도메인 카테고리를 채움 → review·qa·briefing 등 모든 스킬이 자동 활용.

### 3. 외부 데이터 진입점 표

각 스킬 상단에 의존 데이터 명시 + 부재 시 동작:

```markdown
| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 도메인 점검 | biz-rules.md 의 도메인 카테고리 | 선택 | "도메인 점검 생략" 안내 |
| 팀원 매핑 | team.md | 선택 | git author 그대로 표기 |
```

빈 프로젝트에서도 graceful degrade — 안내 메시지로 끝남, 강제 동작 안 함.

### 4. 분량 임계 + 자동 분리

자동 로드 문서가 비대해지지 않도록 임계 + 분리 규칙:

| 산출물 | 임계 1 (알림) | 임계 2 (강제 분리) |
|----------|:----------:|:--------------:|
| `CLAUDE.md` (자동 로드) | 200줄 | optimize-claude-md |
| `biz-rules.md` | 200 | 400 → biz-rules-detail.md |
| `human/SETUP.md` | 300 | 500 → SETUP-TROUBLESHOOTING.md |
| `customers/*.md` | 300 | 500 → 디렉터리 패턴 |
| 진단 보고서 | 500 | PART 별 분리 |

이중 안전망: 각 스킬 자체 검사 + `/garden` 전수 검사.

## 받은 후 첫 흐름 (5분)

```bash
# 신규 프로젝트 디렉터리에서:
cd {프로젝트 루트}

# 1. on-boarding — 6산출물 자동 생성
/on-boarding
# → CLAUDE.md, bot/INDEX.md+bot/*.md, human/README.md,
#    .local.claude/biz-rules.md, .local.claude/team.md, human/SETUP.md

# 2. setup-guide — SETUP.md 환경 점검
/setup-guide

# 3. skill-check — 52개 계약 준수 첫 점검
/skill-check
# → P1 0건 / P2 N건 / P3 N건 보고서

# 4. (작업하며 점진적으로)
/biz-rules               # 도메인 규칙 발견 시 카테고리 채움
/people                  # 동료 프로필 (팀 있을 때)
/customer-profile        # 고객 프로필 (B2B 시)
/learn                   # 검증된 지식 누적
/memo                    # 검증 없이 일단 적기

# 5. (월 1회)
/skill-check             # 계약 준수 재점검
/garden                  # 문서 정원 + 분량 임계 검사

# 6. (분기 1회)
/business-diagnosis      # 사업·경영
/product-diagnosis       # 제품·고객
/tech-diagnosis          # 기술·코드·인프라
/delivery-diagnosis      # 전달·실행
```

## 자기 도메인에 맞춰 커스텀

받은 직후 52개가 모두 활성. 본인 프로젝트 성격에 따라 **빼거나 비활성화** 권장:

| 프로젝트 유형 | 권장 활성화 | 보류 권장 |
|------------|----------|---------|
| **B2B SaaS** | 전부 (원래 가정) | — |
| **회사 내부 시스템** | 진단·작성·리뷰·회고 | `cs`, `customer-profile` |
| **B2C 단일 회사** | 대부분 | `customer-profile` (사용자 ≠ 고객사) |
| **팀 프로젝트 (소규모)** | 회고·작성·리뷰·학습 | 진단 (분기 단위), `coaching`, `leadership` |
| **1인 OSS/개인 프로젝트** | `on-boarding`, `setup-guide`, `learn`, `memo`, `pr`, `review`, `qa`, `daily` | 팀·고객·진단 대부분 |

비활성화는 **디렉터리 삭제 또는 `disable-model-invocation: true` 유지** (`/skills-guide` 카탈로그에 안 보이게).

## 핵심 산출물 (프로젝트별 자동 생성)

`/on-boarding` 이 만드는 6 산출물 (모든 후속 스킬이 자동 활용):

```
프로젝트 루트/
├── CLAUDE.md                  # AI 빠른 참조 (≤200줄)
├── bot/
│   ├── INDEX.md               # AI 사실 카탈로그 진입점
│   └── *.md                   # 분야별 (1~5개)
├── human/
│   ├── README.md              # 사람 진입점
│   └── SETUP.md               # 환경 셋업 가이드
└── .local.claude/
    ├── biz-rules.md           # 도메인 규칙·점검 카테고리
    └── team.md                # 조직 + 멤버 매핑
```

## 작성 원칙 (요약)

1. **신규 스킬 작성 전 `CONTRACT.md` 읽기**
2. **도메인 가정 본문 박힘 금지** — 외부 데이터 위임
3. **부재 시 동작 명시** — graceful degrade
4. **분량 임계 정의** — 누적되는 산출물은 자동 분리 규칙
5. **검증 시나리오 명시** — 빈/부분/풀 데이터 환경별 동작
6. **다른 스킬과의 경계 명시** — 영역 침범 금지
7. **신규 스킬 추가 후 `/skill-check {스킬명}` 호출**
