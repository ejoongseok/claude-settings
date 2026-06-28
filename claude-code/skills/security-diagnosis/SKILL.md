---
name: security-diagnosis
description: 보안·컴플라이언스 관점 정기 진단 — 자격 정보 관리, 인증·인가, 입력 검증, 의존성 CVE, 로깅·모니터링, 정책 준수를 종합. /security-review (PR 단위) 의 정기 버전 — 코드베이스 전체 보안 자세를 진단.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash, WebSearch, AskUserQuestion, mcp__github__list_issues, mcp__github__list_pull_requests, mcp__github__search_issues
---

## 역할

**공격면을 본다.** `/security-review` 가 PR 단위라면, 이 스킬은 **코드베이스 전체의 보안 자세를 정기 진단**한다. 분기·반기 단위 호출.

역할:
1. **자격 정보·비밀 관리** — 평문 시크릿, 환경 변수 누설, 시크릿 회전 정책
2. **인증·인가** — 인증 메커니즘, 세션 관리, RBAC, 권한 우회 가능성
3. **입력 검증·주입** — XSS, SQL/NoSQL injection, CSRF, SSRF, 파일 업로드
4. **의존성·CVE** — 알려진 취약점, 미사용 의존성, 라이선스 리스크
5. **로깅·모니터링** — 민감 정보 로그 노출, 감사 로그 무결성, 알림 체계
6. **컴플라이언스·정책** — 개인정보 처리, 데이터 보존, 사내 보안 정책 준수

톤: 보안 컨설턴트. 위협 모델 기반, 우선순위 명확, 비난 대신 시스템 개선 제안.

## 핵심 원칙

### 다른 진단·리뷰와의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "이 PR 에 보안 문제 있나?" | /security-review | [FAIL] 다루지 않음 — PR 단위 즉시 검토 |
| "이 코드 리팩토링이 안전한가?" | /review | [FAIL] 다루지 않음 |
| "전체 코드베이스의 보안 자세는?" | **/security-diagnosis** | [OK] 핵심 |
| "지난 분기 대비 보안 자세 변화는?" | **/security-diagnosis** | [OK] 핵심 |
| "어떤 보안 투자를 먼저 해야 하나?" | **/security-diagnosis** | [OK] 핵심 |

### 검증과 편향 방지

1. **위협 모델 명시.** "누가 공격자이고, 무엇을 노리는가" 가정을 보고서 상단에 적시
2. **악용 가능성 vs 이론적 취약점 구분.** CVSS 점수만으로 판단 금지. 실제 노출 경로 확인
3. **공개 보고 금지.** 보고서에 구체 exploit 페이로드 포함 금지. 패턴·위치만
4. **민감 정보 마스킹.** 발견된 시크릿·키는 마스킹하여 보고서에 기록 (보고서 자체가 유출원이 안 되게)
5. **의존성은 자동 도구 보조.** 수동 점검 한계 명시 — npm audit / pip-audit / OWASP DC 등 권고

### 데이터 소스 신뢰도

| 소스 | 신뢰도 | 보안 관점에서의 가치 |
|------|:------:|-----------------|
| 코드 (Grep) | ★★★★★ | 객관적 사실 (위치·패턴) |
| 의존성 파일 | ★★★★★ | CVE 매칭 가능 |
| .env / config | ★★★★ | 시크릿 관리 상태 |
| biz-rules.md | ★★★★ | 권한·접근 정책 명시된 곳 |
| WebSearch CVE DB | ★★★ | 공개 취약점 정보 (실제 노출은 별도 검증) |
| auto memory | ★★★ | 사용자가 교정한 보안 사실 |
| 인시던트 이력 (issues/) | ★★★★ | 과거 실제 사건 |

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행. 도메인 규칙 검증 생략, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob + Grep 으로 구조 추론 fallback |
| 인프라 정보 | `.local.claude/INFRASTRUCTURE.md` | 선택 | 배포·CI/CD 관련 분석 영역 생략 + `[인프라 데이터 부재]` 안내 |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` (§4 도메인 점검 카테고리) | 선택 | Tier 1(도메인 무관 일반 점검)만 수행 |
| 팀 정보 | `.local.claude/team.md` | 선택 | git author 그대로 표기, `[담당자 미지정]` 태그 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback, `[코드 직접 확인]` 태그 |
| 이전 진단 보고서 | `.local.claude/reports/YYYY-MM-DD-*-diagnosis.md` | 선택 | 초회 진단 모드로 진행 (변화/델타 분석 생략) |
| 환경 설정 예시 | `.env.example`, `application-*.properties` | 선택 | 자격정보 하드코딩 점검을 파일 grep 만으로 수행 — 신뢰도 ★★ |
| 의존성 현황 | 빌드 파일 + `package-lock.json` / `pnpm-lock.yaml` 등 | 선택 | 취약 의존 목록 분석 생략, CVE 검토 수동 |

## 프로젝트 컨텍스트 (필수 — 호출 전 read)

다음 파일이 존재하면 우선 read:
- `CLAUDE.md` (자동 로드, 보안 코딩·금지사항)
- `bot/INDEX.md` 또는 `.local.claude/INDEX.md`
- `.local.claude/biz-rules.md` (권한·인증 규칙)
- 의존성 파일: `package.json`, `pom.xml`, `requirements.txt`, `go.mod`, `Cargo.toml`
- 설정: `application.yml`, `.env.example`, `docker-compose.yml`

## 모드 판단

| 입력 | 모드 | 예상 소요 |
|------|------|----------|
| `/security-diagnosis` (기본) | **종합 진단** — 6파트 전체 | ~30분+ |
| `secrets` | **자격 정보 심층** — 파트 1만 | ~10분 |
| `auth` | **인증·인가** — 파트 2만 | ~15분 |
| `injection` | **주입·입력 검증** — 파트 3만 | ~15분 |
| `deps` | **의존성·CVE** — 파트 4만 | ~10분 |
| `delta` | **델타** — 이전 보고서 대비 | ~10분 |
| `quick` | **요약** — 2~3페이지 | ~10분 |

## 프로세스

### Phase 1: 위협 모델 + 데이터 수집

**1-1. 위협 모델 정의 (사용자 검증)**

```markdown
## 위협 모델 (검증 요청)

### 자산
- (검출된 자산: 사용자 데이터·결제·내부 API·관리자 기능 등)

### 공격자 가정
- 외부 익명: ✓ / 외부 인증된 사용자: ✓ / 내부 직원: ?
- 자동화 봇: ✓ / 표적 공격자: ?

### 가장 두려운 시나리오 (top 3)
- (자동 추출 + 사용자 보강)
```

**`AskUserQuestion`으로 위협 모델 확정.** 이 가정이 분석의 기준.

**1-2. 기존 보고서 확인**

```bash
ls .local.claude/reports/ 2>/dev/null | grep -iE 'security-diagnosis' | sort | tail -3
ls .local.claude/cs/ .local.claude/incidents/ 2>/dev/null | head
```

**1-3. 코드 보안 스캔 (read-only Grep)**

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**:
> - Grep 병렬: 자격 정보(`password|api_key|secret|token`), 위험 함수(`eval|exec|Runtime.exec`), DOM XSS(`innerHTML|document.write`), SQL 동적 구성, 약한 암호화(`MD5|SHA1|DES`), 권한 어노테이션(`@PreAuthorize|@PermitAll`), 로그 민감 정보(`log.*password|token`) 을 동시에 수행
> - Read: `CLAUDE.md`, `biz-rules.md`, `application.yml`/`application-*.properties`, `.env.example`, `docker-compose.yml`, 의존성 파일(`package.json`, `pom.xml` 등), auto memory 병렬 로드
> - Bash: `ls -la .env*`, `find . -name "*.example"`, `grep "ENC\["` 등 환경 점검 명령 병렬

```bash
# 자격 정보 노출
git grep -nE "(password|api_key|secret|token)\s*=\s*[\"']" -- ':!*.md' ':!*.test.*' | head -50
git grep -nE "(BEGIN RSA|BEGIN PRIVATE KEY|-----BEGIN)" | head

# 위험 함수
git grep -nE "(eval\(|exec\(|system\(|Runtime\.exec|os\.popen)" | head
git grep -nE "(innerHTML|dangerouslySetInnerHTML|document\.write)" | head

# SQL 동적 구성
git grep -nE "(SELECT.*\+|FROM.*\+|WHERE.*\+).*\$|\$\{" | head

# 약한 암호화
git grep -nE "(MD5|SHA1\(|DES|RC4)" | head

# 권한·인증 패턴
git grep -nE "(@PreAuthorize|@PermitAll|isAdmin|hasRole)" | head -30

# 로그 민감 정보
git grep -nE "(log|logger|console\.log).*(password|token|secret)" | head
```

**1-4. 의존성 스캔 (자동 도구 권고)**

```bash
# 사용자에게 권고 (자동 실행 안 함 — 외부 네트워크)
echo "다음 명령으로 의존성 CVE 점검 권장:"
echo "- npm audit --json (Node)"
echo "- pip-audit (Python)"
echo "- mvn dependency-check:check (Maven)"
echo "- gh dependabot alerts list (GitHub)"
```

사용자가 결과 파일 경로 제공하면 Read 로 분석.

**1-5. 환경·설정 점검**

```bash
ls -la .env* 2>/dev/null
find . -name "*.example" -path "*env*" 2>/dev/null
grep -rn "ENC\[" --include="*.yml" --include="*.properties" 2>/dev/null | head
```

### Phase 2: 6파트 분석 + 자기 검증

---

## PART 1: 자격 정보·비밀 관리

| 항목 | 발견 N건 | 위치 (마스킹) | 위험도 | 권고 |
|------|:------:|---------|:----:|------|
| 평문 시크릿 | | | | Vault/KMS 이전 |
| .env 누설 (git 추적) | | | | git-filter-repo, 회전 |
| 하드코딩 API 키 | | | | 환경 변수화 |
| 시크릿 회전 정책 부재 | | | | 회전 SOP 수립 |

**→ 의사결정 포인트:** 가장 급한 시크릿 위험 1줄

---

## PART 2: 인증·인가

### 2-1. 인증 메커니즘
- 인증 방식: (JWT / Session / OAuth 등)
- 비밀번호 해시: (bcrypt/argon2/...)
- 세션 만료·갱신 정책
- MFA 지원 여부

### 2-2. 인가·RBAC
| 보호 대상 | 인가 방식 | 우회 가능성 |
|---------|--------|---------|
| 관리자 기능 | | |
| 결제·민감 데이터 | | |
| 다른 사용자 데이터 | | |

### 2-3. 권한 우회 패턴 검사
- IDOR (Insecure Direct Object Reference): 사용자 ID 기반 직접 접근
- 격리 키(있는 프로젝트만) 우회: 테넌트 격리 SQL/API 검증
- 권한 상승: 일반 사용자 → 관리자 경로

**→ 의사결정 포인트:** 가장 급한 인가 갭 1줄

---

## PART 3: 입력 검증·주입

| 카테고리 | 발견 패턴 N건 | 대표 위치 | 위험도 |
|---------|:--------:|---------|:----:|
| SQL/NoSQL Injection | | | |
| XSS (Reflected/Stored/DOM) | | | |
| CSRF (상태 변경 API) | | | |
| SSRF (외부 URL 호출) | | | |
| 파일 업로드 (타입·크기·경로) | | | |
| 디시리얼라이제이션 | | | |
| 명령어 주입 | | | |
| Path Traversal | | | |

검증 라이브러리 사용 현황: (Bean Validation / Joi / Pydantic 등)

**→ 의사결정 포인트:** 가장 광범위한 주입 카테고리 1줄

---

## PART 4: 의존성·CVE

### 4-1. 직접 의존성 현황
- 총 N개 (직접) / 추정 N개 (전이)
- 패키지 매니저: (npm/pip/maven/...)
- 자동 업데이트 도구: (Dependabot/Renovate 사용 여부)

### 4-2. 알려진 취약점 (도구 결과 기반)
| 패키지 | 버전 | 취약점 | 심각도 | 패치 가능 |
|--------|----|------|:----:|:------:|
| ... | | | | |

### 4-3. 라이선스 리스크
- 카피레프트 (GPL 등) 의존 여부
- 라이선스 명시 없는 패키지

**→ 의사결정 포인트:** 가장 급한 패치 1건 + 자동화 도입 여부

---

## PART 5: 로깅·모니터링

### 5-1. 민감 정보 로그 노출
| 패턴 | 발견 N건 | 위치 | 위험도 |
|------|:------:|----|:----:|
| 비밀번호·토큰 로그 | | | |
| PII 평문 로그 | | | |
| 스택트레이스 사용자 노출 | | | |

### 5-2. 감사 로그 (Audit Log)
- 관리자 행동 기록 여부
- 권한 변경 기록 여부
- 로그 무결성 (변조 방지)

### 5-3. 모니터링·알림
- 인증 실패 임계 알림
- 비정상 트래픽 감지
- 데이터 유출 시그널 (대량 다운로드 등)

**→ 의사결정 포인트:** 모니터링에서 가장 큰 사각지대 1줄

---

## PART 6: 컴플라이언스·정책

### 6-1. 개인정보·데이터 보존
- 수집하는 PII 카테고리
- 보존 기간 정책 명시 여부
- 삭제 요청 처리 흐름

### 6-2. 사내 보안 정책 준수
- CLAUDE.md `보안` 섹션 준수도 (자체 컨벤션)
- 코드 스캔 자동화 (SAST/DAST/SCA)
- 보안 교육 이력 (인접 데이터)

### 6-3. 외부 컴플라이언스
- GDPR / CCPA / 개인정보보호법 적용 여부
- 산업별 (PCI-DSS, HIPAA 등) 적용 여부

**→ 의사결정 포인트:** 컴플라이언스 갭 1줄

---

## Phase 3: 자기 검증

**Adversarial Review** — 핵심 발견 P1 Top 3 각각에 대해:
1. **근거 재점검**: 코드 패턴 매치만인가, 실제 노출 경로까지 확인했는가? 단일 위치인가 다수인가?
2. **전제 검증**: 이 발견이 "악용 가능한 취약점" 이려면 어떤 전제가 필요한가? (예: 평문 시크릿 → git 히스토리 노출 or 실제 접근 가능 경로)
3. **반대 증거 탐색**: "이미 보호 레이어가 있는가?" / "false positive 가능성?" — 반박 1개 이상 탐색. 위협 모델 자산·공격자 가정과 정합성 재확인

반박 유효 시 P1→P2 강등 또는 본문 수정, 부분 반박 시 "단, {전제}" 인라인 추가.

```markdown
## 자기 검증

1. **위협 모델 정합성**: 위협 모델의 자산·공격자가 모든 PART 에 반영
2. **악용 가능성 평가**: 단순 패턴 매칭이 아닌 실제 노출 경로 확인
3. **민감 정보 마스킹**: 발견된 시크릿·키 모두 마스킹
4. **다른 진단과 중복**: tech-diagnosis 의 보안 섹션과 중복 없음 (이 보고서가 더 깊음)
5. **권고 우선순위**: P1 (즉시) / P2 (분기 내) / P3 (반기 내) 분류
```

## 출력 구조

```yaml
---
type: security-diagnosis
date: YYYY-MM-DD
mode: full | secrets | auth | injection | deps | delta | quick
threat-model:
  assets: [...]
  attackers: [...]
  scenarios: [...]
findings:
  p1: N건  # 즉시
  p2: N건  # 분기 내
  p3: N건  # 반기 내
data-sources:
  code-files-scanned: N
  dependencies: N
---

# 보안·컴플라이언스 진단 보고서

> **기간**: YYYY-MM-DD
> **위협 모델**: [요약 1줄]

## TL;DR (3줄)
- 보안 자세: [한 줄 평가]
- 가장 큰 위험: [P1 1건]
- 다음 액션: [1줄]

[PART 1~6]

## 우선순위 표
| # | 발견 | PART | 위험도 | 액션 | 데드라인 |
|---|----|:----:|:----:|------|--------|
| ... | | | | | |
```

## 저장 경로

`.local.claude/reports/YYYY-MM-DD-security-diagnosis.md`

[WARN] **민감 정보 검출 시**: 보고서 저장 전 마스킹 검증. 시크릿 값 자체를 보고서에 기록 금지.

## 다음 스킬 연결

- P1 발견 → `/review` 로 즉시 PR 단위 보안 리뷰 진행 (보안 중심 관점으로 수행)
- 의존성 패치 다수 → 별도 패치 PR
- 컴플라이언스 갭 → `/business-diagnosis` 와 연계 (예산·리스크)
- 인증·인가 재설계 필요 → `/srs` 로 요구사항 정의

## 분량 임계 — 자동 분리

| 임계 | 동작 |
|------|------|
| ≤500줄 | 단일 보고서 |
| >500줄 | PART 별 분리 + 우선순위 표만 메인 |

## 제약조건

- **공개 exploit 페이로드 금지.** 패턴·위치만 기록
- **민감 정보 마스킹 필수.** 발견된 시크릿 값 자체를 보고서에 쓰지 않음
- **악용 가능성 vs 이론 구분.** 단순 CVSS 점수보다 실제 노출 경로 우선
- **위협 모델 합의 후 분석.** 자산·공격자 가정 없으면 모든 발견이 중요해 보여 우선순위 무의미
- **자동 도구 결과 보조.** 수동 점검은 한계 — npm audit / OWASP DC 등 결과를 사용자가 제공하면 통합
- **인접 진단 영역 침범 금지.** 코드 품질은 /tech, PR 단위는 /security-review

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[의존성 부재]** npm audit / pip-audit / trivy 등 스캐너 미설치
- 신호: `which npm-audit` / `pip-audit --version` 실패
- 대응: 설치 가이드 안내 후 사용자에게 기존 결과 파일 경로 질문 → 수동 입력으로 진행

**[데이터 결함]** CVE DB WebSearch 실패·응답 부재
- 신호: CVE 조회 중 네트워크 오류 또는 결과 0건
- 대응: `[CVE 미검증]` 태그 병기 + 오프라인 룰(의존성 버전·관용적 위험) 기반 간이 판정
