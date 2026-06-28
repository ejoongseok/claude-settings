---
name: on-boarding
description: "프로젝트 구조와 목적을 체계적으로 분석하여 종합적인 온보딩 정보 제공"
argument-hint: "[--depth shallow|deep] [--focus area] [--format summary|detailed]"
disable-model-invocation: true
effort: max
context: fork
allowed-tools: Read, Grep, Glob, Write, AskUserQuestion, Bash(find *), Bash(wc *), Bash(head *), Bash(cat *), Bash(ls *), Bash(mkdir *), Bash(rm *), Bash(rmdir *)
---

현재 프로젝트를 체계적으로 분석하여 신규 프로젝트 표준 산출물 (CLAUDE.md, bot/INDEX.md + bot/*.md, human/README.md, .local.claude/biz-rules.md, .local.claude/team.md) 을 생성합니다.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 대상 프로젝트 | `pwd` 의 파일들 | **필수** | "빈 디렉터리" 안내 후 종료 |
| 기존 CLAUDE.md | 프로젝트 루트 | 선택 | 존재 시 덮어쓰기 전 사용자 확인 |
| 기술 스택 감지 파일 | `package.json`, `pom.xml` 등 | 선택 | 사용자 입력 요청 |

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "신규 프로젝트 6산출물 자동 생성" | **이 스킬** | ✓ 핵심 (CLAUDE.md, bot/, human/, biz-rules·team 스켈레톤, SETUP.md) |
| "이미 만든 SETUP.md 점검·갱신·암묵지식 누적" | /setup-guide | 다루지 않음 (생성은 이 스킬, 이후 유지는 setup-guide) |
| "디렉터리 구조만 스캔·집계" | /analyze-dir | 다루지 않음 (이 스킬은 산출물 생성까지 수행) |

## 컨텍스트 관리 전략

각 단계의 분석 결과를 `.claude/tmp/onboarding/` 디렉터리에 마크다운 파일로 저장하고, 최종 단계에서 Read로 읽어 문서를 조립하세요.

준비: !`mkdir -p .claude/tmp/onboarding`

단계별 저장 파일:
- 1단계 -> .claude/tmp/onboarding/01-detect.md
- 2단계 -> .claude/tmp/onboarding/02-metadata.md
- 3단계 -> .claude/tmp/onboarding/03-structure.md
- 4단계 -> .claude/tmp/onboarding/04-deep-analysis.md (--depth deep일 때만)
- 최종 단계에서 위 파일들을 Read하여 산출물 조립 (CLAUDE.md / bot/INDEX.md + bot/*.md / human/README.md / .local.claude/biz-rules.md / .local.claude/team.md)

각 단계 파일에는 해당 단계에서 발견한 사실만 구조화하여 기록하세요.
확인하지 않은 내용은 기록하지 마세요.

## 옵션 해석 규칙

$ARGUMENTS를 파싱하여 다음 옵션을 인식하세요:

- `--depth`가 없거나 `--depth deep`이면 -> 심층 분석 수행 (기본값)
- `--depth shallow`이 명시된 경우에만 -> 기본 구조와 설정만 분석 (1~3단계만 수행)
- `--focus backend` -> 서버 사이드 코드 및 API 중심 분석
- `--focus frontend` -> 클라이언트 사이드 및 UI 중심 분석
- `--focus api` -> API 엔드포인트 및 통합 중심 분석
- `--focus database` -> 데이터 모델 및 스키마 중심 분석
- `--focus testing` -> 테스트 전략 및 커버리지 중심 분석
- `--focus devops` -> 배포 및 인프라 구성 중심 분석
- `--format summary` -> 간략한 요약만 제공
- `--format detailed` -> 상세 분석 제공 (기본값)
- 옵션이 아무것도 없으면 -> deep 깊이로 전체 프로젝트를 상세 분석

## 프로젝트 기본 정보 (자동 수집)

아래 명령은 규모와 기술 스택을 빠르게 판별하기 위한 용도입니다.
상세 탐색은 분석 프로세스에서 Glob과 Read로 수행하세요.

### 규모 파악
- 전체 파일 수: !`find . -maxdepth 4 -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/.svn/*" -not -path "*/.idea/*" -not -path "*/target/*" -not -path "*/build/*" -not -path "*/dist/*" -not -path "*/__pycache__/*" -not -path "*/.next/*" -not -path "*/.nuxt/*" | wc -l`
- 디렉터리 구조: !`find . -maxdepth 3 -type d -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/.svn/*" -not -path "*/.idea/*" -not -path "*/target/*" -not -path "*/build/*" -not -path "*/dist/*" -not -path "*/__pycache__/*" -not -path "*/.next/*" -not -path "*/.nuxt/*" | head -80`

### 기술 스택 감지용 파일
- 빌드/패키지 파일: !`find . -maxdepth 2 -type f \( -name "pom.xml" -o -name "build.gradle" -o -name "build.gradle.kts" -o -name "package.json" -o -name "requirements.txt" -o -name "pyproject.toml" -o -name "Cargo.toml" -o -name "go.mod" -o -name "Gemfile" -o -name "composer.json" -o -name "*.csproj" -o -name "*.sln" -o -name "Makefile" \)`
- 설정 파일: !`find . -maxdepth 2 -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.ini" -o -name "*.cfg" \) -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/target/*" | head -30`
- 문서 파일: !`find . -maxdepth 2 -type f \( -name "README*" -o -name "*.md" -o -name "CONTRIBUTING*" -o -name "CHANGELOG*" -o -name "docker-compose*" -o -name "Dockerfile" \)`

find 명령이 실패하거나 권한 오류가 발생하면, 해당 항목은 건너뛰고 Glob으로 대체 탐색하세요.

## 분석 프로세스

### 1단계: 기술 스택 감지 및 분류

자동 수집된 빌드/패키지 파일 목록을 보고 프로젝트 유형을 판별하세요.

판별 기준:
- pom.xml 또는 build.gradle -> Java/Kotlin (Spring Boot, Quarkus 등)
- package.json -> JavaScript/TypeScript (React, Vue, Next.js, Express 등)
- requirements.txt 또는 pyproject.toml -> Python (Django, FastAPI, Flask 등)
- go.mod -> Go
- Cargo.toml -> Rust
- *.csproj 또는 *.sln -> .NET (C#)
- Gemfile -> Ruby (Rails 등)
- composer.json -> PHP (Laravel 등)
- 복수 빌드 파일 -> 모노레포 또는 멀티 스택 (각각 분석)

해당 빌드/패키지 파일을 Read로 열어 프레임워크, 언어 버전, 주요 의존성을 파악하세요.
멀티모듈 프로젝트인 경우 모듈별 역할을 파악하세요.

결과를 .claude/tmp/onboarding/01-detect.md에 저장하세요.
형식: 프로젝트 유형, 언어/버전, 프레임워크/버전, 빌드 도구, 주요 의존성 목록

### 2단계: 프로젝트 메타데이터 및 환경 구성
- README를 Read로 읽어 프로젝트 목적과 비즈니스 도메인 파악
- 환경별 설정 파일(profiles, .env.example 등) 확인
- Docker, CI/CD 설정 확인
- 실행/빌드/테스트 명령어 파악

결과를 .claude/tmp/onboarding/02-metadata.md에 저장하세요.
형식: 프로젝트 목적, 실행 명령어, 환경 구성, 인프라 설정

### 3단계: 코드 구조 및 컨벤션 분석
- Glob으로 소스 디렉터리 구조 탐색
- 아키텍처 패턴 식별 (Layered, Hexagonal, Microservices 등)
- 패키지/디렉터리 구성 방식 파악 (레이어별 / 기능별 / 혼합)
- 코딩 컨벤션 추출 (네이밍, 포맷팅, 린트 설정)
- 에러 처리 패턴 식별
- 유틸/헬퍼/공통 모듈 위치 파악

결과를 .claude/tmp/onboarding/03-structure.md에 저장하세요.
형식: 아키텍처, 디렉터리 트리(역할 주석 포함), 컨벤션, 에러 패턴, 공통 모듈

### 4단계: 심층 분석 (--depth deep 또는 기본값일 때)

> **[1M 활용]** 서브에이전트 분할 없이 메인에서 직접 **다중 파일 동시 Read** 후 교차 분석:
> - 로드: 4개 영역(A 도메인·데이터, B API·요청 흐름, C 외부 연동·인프라, D 테스트·품질) 의 핵심 파일을 동시에 Read — 엔티티 모델, 대표 컨트롤러/라우터, 외부 연동 설정, 테스트 샘플
> - 교차 분석: {DB 스키마 vs ORM 모델 vs API 응답 DTO 일관성}, {인증 체계 vs 테스트 커버리지}, {외부 의존성 vs 배치 스케줄러 영향 범위}
> - 규모가 큰 프로젝트(파일 10만+)는 영역별 서브에이전트 병렬 모드로 전환.
> - 총 로드 추정 토큰 ~600K(1M 컨텍스트의 60%; 줄 수로 대략 가늠) 근접 시 영역별 단계 저장(append) 방식 유지.

--depth shallow이면 이 단계를 건너뛰고 최종 단계로 이동하세요.

아래 영역을 순서대로 분석하세요. 각 영역 분석 후 결과를 즉시
.claude/tmp/onboarding/04-deep-analysis.md에 누적 저장(append)하세요.
한 번에 모든 영역을 분석하지 말고, 영역별로 분석 -> 저장 -> 다음 영역 순서를 따르세요.

영역 A: 도메인 모델 및 데이터
- 핵심 엔티티/모델 식별 및 관계 파악
- DB 마이그레이션 도구 및 스키마 관리 방식
- ORM/쿼리 빌더 사용 패턴

영역 B: API 및 요청 흐름
- 주요 API 엔드포인트 목록
- 대표 API 하나의 전체 흐름 추적 (진입 -> 처리 -> 응답)
- 인증/인가 체계

영역 C: 외부 연동 및 인프라
- 외부 서비스 연동 지점
- 메시지 큐, 캐시, 검색 엔진 등 인프라 의존성
- 배치/스케줄러 작업

영역 D: 테스트 및 품질
- 테스트 프레임워크 및 전략
- 테스트 디렉터리 구조와 네이밍 규칙
- 모킹 전략

### 5단계: 문서 생성

먼저 덮어쓰기 가드:
- 프로젝트 루트에 다음 중 하나라도 존재하는지 Glob 으로 확인: CLAUDE.md, bot/, human/
- 하나라도 존재하면 AskUserQuestion 으로 사용자에게 확인:
  - 질문: "기존 {경로 목록}이(가) 있습니다. 어떻게 할까요?"
  - 옵션: "덮어쓰기" / "기존 파일을 .bak/ 디렉터리로 백업 후 생성" / "취소 (분석 결과는 .claude/tmp/onboarding/에 보존)"
- "취소" 선택 시 임시 디렉터리는 삭제하지 말고 종료하세요. 사용자가 분석 결과를 직접 활용할 수 있도록.

이 단계에서는 새로운 파일 탐색을 하지 마세요.
.claude/tmp/onboarding/ 디렉터리의 모든 파일을 Read로 읽고,
출력 형식은 ${CLAUDE_SKILL_DIR}/templates/output-format.md 를 참조하여 **6개 산출물**을 생성합니다:

1. **CLAUDE.md** (프로젝트 루트, 자동 로드, ≤200줄 엄수) — AI 빠른 참조
   - 빌드/실행 명령어, 컨벤션, 금지 사항 등
   - 마지막에 `@bot/INDEX.md`, `@human/README.md` 참조 안내

2. **bot/INDEX.md + bot/*.md** (프로젝트 루트의 bot/ 디렉터리) — AI 사실 카탈로그
   - bot/INDEX.md = 라우팅 진입점 (각 bot 파일의 용도·갱신일 표)
   - bot/*.md = 정보량에 따라 1~5개 분할 (작은 프로젝트는 1~3개로 충분)
   - 분할 후보: architecture / domain-model / api-contract / infrastructure / rules / known-issues 등 (해당 시만)
   - 각 파일 frontmatter 필수 (title, type, last-updated, source-files)
   - 코드 레퍼런스는 `경로/파일:줄번호` 완전 경로 (`...` 축약 금지)
   - dualize-docs 의 bot/ 출력 형식과 호환 — 누적되면 dualize-docs 가 보강 가능

3. **human/README.md** (프로젝트 루트의 human/ 디렉터리) — 사람 진입점
   - 3단 구조: 1. 배경 / 2. 현재 상태 (Mermaid 다이어그램 1+ 필수) / 3. 남은 질문·의사결정
   - "더 읽을 거리" 섹션에 bot/INDEX.md, CLAUDE.md 안내

4. **`.local.claude/biz-rules.md` 스켈레톤** (도메인 점검 카테고리 진입점) — 빈 템플릿 자동 생성
   - 신규 프로젝트는 도메인 규칙·점검 카테고리가 아직 없음 — 작업하며 점진 채움
   - `/review`, `/srs`, `/qa`, `/briefing`, `/deploy-checklist` 등이 §4 (도메인 점검 카테고리) 를 자동 활용
   - 스켈레톤만 생성, 사용자 안내: "이 파일 §4 를 채울수록 다른 스킬의 도메인 점검이 강화됩니다"
   - `/biz-rules` 스킬 출력 형식 따름 (4개 섹션: 변경 이력, 1.상태 전이, 2.비즈니스, 3.도메인, 4.도메인 점검 카테고리)

5. **`.local.claude/team.md` 스켈레톤** (조직 + 멤버 매핑) — 빈 템플릿 자동 생성
   - 사용자가 직접 채움 (조직 구조 + 닉네임-실명-부서-대응톤 매핑)
   - `/analyze-request`, `/draft`, `/briefing`, `/team-review`, `/cs`, `/memo` 등이 자동 활용

6. **`human/SETUP.md`** (개발 환경 셋업 가이드) — 신규 합류자가 처음부터 따라하면 환경이 준비되는 가이드
   - **자동 추출** (코드/설정에서 감지하여 채움):
     - 런타임 버전: `.nvmrc`, `.python-version`, `.tool-versions`, `pom.xml` (`<java.version>`), `build.gradle`, `go.mod`, `package.json` (`engines`), `Dockerfile` (FROM)
     - 빌드/패키지 매니저: `package.json` (npm/pnpm/yarn), `pom.xml` / `build.gradle` (Maven/Gradle), `requirements.txt` / `pyproject.toml` / `Pipfile`, `Cargo.toml`, `go.mod`
     - 데이터베이스/외부 의존: `docker-compose.yml`, application.yml/properties, `.env.example`
     - IDE 설정: `.vscode/extensions.json`, `.editorconfig`, LSP 서버 (감지된 언어별 권장)
     - Claude Code 설정: `.mcp.json`, `.claude/settings.json` (MCP 서버, hooks, 권장 skill)
     - 첫 실행 명령: `package.json` scripts, `Makefile`, README 의 "Getting Started" 섹션
   - **암묵 지식 placeholder** (`[확인 필요]` 태그로 비워둠 — 사람이 채움):
     - VPN/방화벽/사내망 접속, DB 인증 정보 발급 절차, 협업 채널 (Slack/Jira/Linear), 사내 라이선스/계정
   - **구조 (필수 섹션)**:
     ```
     # 프로젝트 셋업 가이드
     ## 빠른 시작 (역할별)         # 개발자/디자이너/PM 등 역할별 진입
     ## 1. 사전 요구사항            # OS, 하드웨어 권장사양
     ## 2. 필수 설치 (자동 추출)    # 런타임·빌드·DB — 각 행에 [확인 명령] 포함
     ## 3. 환경 변수                # .env.example 기반
     ## 4. IDE 설정                 # VS Code 권장 확장, LSP, IntelliJ 설정
     ## 5. Claude Code 설정 (선택)  # MCP, hooks, 권장 skill — 있을 시
     ## 6. 첫 실행                  # 의존성 설치 → 빌드 → 개발 서버 → 검증 명령
     ## 7. 사람에게 들어야 할 것 [확인 필요]   # 암묵 지식 placeholder
     ## 8. 트러블슈팅               # 셋업 중 발견한 문제 누적 (초기 비어있음)
     ## 9. 추정 소요 시간           # 사전 준비 / 의존성 / 첫 빌드 / 총 시간
     ```
   - **검증 명령 필수**: 각 설치 항목에 `node -v` / `mvn --version` 같은 확인 명령 포함 (셋업 후 자가 검증 가능)
   - 코드/설정에서 감지 안 된 항목은 섹션 통째로 생략 (빈 placeholder 금지). 단 §7 (암묵 지식) 은 항상 포함
   - 사용자 안내: "이 파일은 살아있는 문서입니다. 환경 변경·트러블슈팅 발견 시 `/setup-guide` 로 갱신하세요."

핵심 원칙:
- 중간 파일에 기록되지 않은 내용은 포함하지 마세요
- 분석에서 발견되지 않은 섹션은 통째로 생략하세요. 빈 섹션이나 플레이스홀더를 남기지 마세요
- CLAUDE.md 는 200줄 이내, bot/*.md 는 각 150줄 이내 권장
- [경로] 같은 플레이스홀더가 최종 문서에 남아 있으면 안 됩니다

**분량 임계 — 산출물 분리 정책 (사용자 안내 포함)**:

| 산출물 | 임계 | 분리 시 패턴 |
|--------|:----:|------------|
| `CLAUDE.md` (자동 로드) | 200줄 | optimize-claude-md 가 검사·분리 (기존) |
| `biz-rules.md` (자동 로드 후보) | 200/400줄 | `biz-rules-detail.md` 분리 — `/biz-rules` 스킬 분량 임계 참조 |
| `human/SETUP.md` | 300/500줄 | `human/SETUP-TROUBLESHOOTING.md` 분리 — `/setup-guide` 스킬 분량 임계 참조 |
| `customers/{name}.md` | 300/500줄 | `customers/{name}/` 디렉터리 분리 — `/customer-profile` 스킬 분량 임계 참조 |
| `team.md` | 300줄 (대형 조직) | `team.md` 핵심 + `team-orgchart.md` 분리, 또는 `people/{name}.md` 로 깊이 위임 |
| `bot/*.md` | 150줄/파일 | 처음부터 1~5개 분할 (이미 가이드 있음) |

산출 시점에는 작아서 분리 불필요 — 안내 문구만 각 파일 상단 주석으로 포함:
```markdown
<!-- 분량 임계: 200/400줄. 초과 시 /biz-rules 또는 /garden 이 분리 제안 -->
```

분리 검사 책임은 `/garden` Phase 3 + 각 스킬이 갱신 시 자체 검사.

문서 생성 완료 후 임시 디렉터리를 정리하세요:
- !`rm -rf .claude/tmp/onboarding`
- .claude/tmp/가 비어 있으면 디렉터리도 삭제: !`rmdir .claude/tmp 2>/dev/null || true`

## 보안 관련 주의사항

- 민감한 정보(API 키, 비밀번호, 토큰 등)는 절대 문서에 포함하지 마세요
- .env 파일은 구조만 분석하고 값은 마스킹하세요
- 인증 정보가 포함된 설정 파일은 키 이름만 언급하세요
- 중간 파일(.claude/tmp/)에도 민감 정보를 기록하지 마세요

## 분석 제외 항목

- 바이너리 파일 및 미디어 파일
- 빌드 결과물: build/, dist/, target/, out/, .next/, .nuxt/
- 패키지 매니저 캐시: node_modules/, .gradle/, .m2/, __pycache__/
- 버전 관리: .git/, .svn/
- IDE 설정: .idea/, .vscode/ (단, 공유 설정 .editorconfig 등은 참고)
- 락 파일 내용: package-lock.json, yarn.lock 등 (존재 여부만 확인)

## 다음 스킬 연결

- 6산출물 생성 완료 → `/setup-guide` 로 SETUP.md 환경 점검·갱신
- biz-rules.md 스켈레톤 채우기 → `/biz-rules` (도메인 규칙 발견 시)
- team.md 스켈레톤 채우기 → `/people` (동료 프로필), `/customer-profile` (B2B 고객)
- 계약 준수 첫 점검 → `/skill-check`
- 다음에 무엇을 할지 모를 때 → `/skills-guide --new`
- 산출물 비대·만료 정리 → `/garden`

## 제약조건

- **민감 정보 마스킹**. API 키·비밀번호·토큰은 문서·중간 파일(.claude/tmp/)에 포함하지 않습니다. .env 는 키 이름만, 값은 마스킹.
- **덮어쓰기 전 사용자 확인**. 기존 CLAUDE.md / bot/ / human/ 존재 시 AskUserQuestion 으로 덮어쓰기·백업·취소 선택.
- **확인된 사실만 기록**. 중간 파일에 없는 내용은 산출물에 포함하지 않고, 미발견 섹션은 통째로 생략합니다 (빈 placeholder 금지).
- **자동 로드 분량 준수**. CLAUDE.md 는 200줄 이내, bot/*.md 는 각 150줄 이내로 유지.
- **본문 도메인 가정 금지**. 도메인 규칙은 biz-rules.md 스켈레톤으로 위임 (§3).
- **`[경로]` 같은 플레이스홀더가 최종 문서에 남지 않게** 정리 후 완료 보고.

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경·규모]** 프로젝트 파일 10만+ 또는 저장소 초대형
- 신호: `find . -type f | wc -l` ≥ 100k 또는 분석 타임아웃
- 대응: 5단계 심층 분석을 병렬 서브에이전트 모드로 강제 분할 + 범위 축소 경고

**[사용자 개입 필요]** 기존 CLAUDE.md / domain-native 파일 존재
- 신호: 루트에 CLAUDE.md 또는 이미 도메인 지식 축적 흔적
- 대응: 덮어쓰기 전에 사용자 확인(merge / overwrite / skip 선택) 후 진행
