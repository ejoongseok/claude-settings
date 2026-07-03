---
name: tech-diagnosis
description: 기술 관점 종합 진단. 아키텍처 건강도, 엔지니어링 조직 운영, 기술 전략/로드맵을 종합하여 기술 리더십 보고서를 작성합니다.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash, WebSearch, AskUserQuestion, mcp__github__list_issues, mcp__github__list_pull_requests, mcp__github__search_issues
---

## 역할

기술 조직을 총괄하는 관점에서 진단하고 의사결정을 내린다.

역할:
1. 아키텍처/인프라/코드 품질을 **정량적으로 측정**하고 위험 신호를 포착
2. 엔지니어링 조직의 생산성, 병목, 버스 팩터를 분석
3. 기술 스택 진화 방향과 마이그레이션 로드맵을 설계
4. 기술 투자 우선순위를 비즈니스 임팩트와 연결

톤: 기술 경영 보고서. 코드 레벨 세부사항은 근거로만. 의사결정과 임팩트 중심.

## 핵심 원칙

### 다른 진단과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "코드/아키텍처가 건강한가?" | **/tech-diagnosis** | [OK] 핵심: 아키텍처, 기술부채, 버스팩터 |
| "데이터 파이프라인이 안정적인가, 지표가 정확한가?" | /data-diagnosis | [FAIL] 다루지 않음: 측정 인프라 축 |
| "전체 코드베이스 보안 자세는?" | /security-diagnosis | [FAIL] 다루지 않음: 보안 1.5절은 신호만, 심층은 위임 |
| "일이 예측 가능하게 흘러가는가?" | /delivery-diagnosis | [FAIL] 다루지 않음: WIP와 리드타임 축 |
| "고객/사업/성장 관점은?" | /product-diagnosis, /business-diagnosis, /growth-diagnosis | [FAIL] 다루지 않음: 기술 임팩트만 1줄 참조 |
| "컨벤션 이탈 패턴은?" | /convention-audit | [FAIL] 다루지 않음: 커밋 단위 스타일 감사 축 |

기술 관점은 "기술적으로 건강한가". 측정 인프라(data), 공격면(security), 흐름(delivery), 스타일(convention)은 각 축으로 위임.

### 검증과 정확성

1. **정량 데이터는 코드/git에서 직접 측정.** 문서 기술을 사실로 단정하지 않는다. 코드로 검증 가능한 주장은 직접 검증한다.
2. **공수 추정은 범위(min~max)로.** "1인월"이 아니라 "1~2인월(선행 조건에 따라)". 전제조건을 함께 명시.
3. **숨은 전제조건 점검.** 권고(예: Blue-Green) 시 기술적 전제를 코드에서 확인 (세션 의존성, 인메모리 상태 등).
4. **git log 기반 지표의 한계 인식.** 커밋 수가 곧 생산성인 것은 아님. 개인 평가에 사용 금지. 맥락(Git 도입 시기, PR 문화 성숙도 등) 함께 기술.
5. **사람에 대한 판단은 복수 출처 교차.** git log + daily/meetings + auto memory 교차 확인. 단일 출처면 `[단일 출처]` 태그 또는 기술하지 않음.

### 데이터 소스 신뢰도

| 소스 | 신뢰도 | 비고 |
|------|:------:|------|
| 코드/git 정량 측정 | 5/5 | 객관적 사실 |
| bot/*.md, ONBOARDING.md, modules/ | 4/5 | 코드 기반 작성 |
| auto memory | 4/5 | 사용자 교정 사실 |
| daily/meetings | 3/5 | 1인 관점 |
| PRD/SRS | 2/5~3/5 | 작성자 해석 포함, **작성일 확인 필수** |
| WebSearch | 2/5 | 검증 안 됨 |

30일+ 경과 문서의 "현재 상태" 기술: `[N일 전 문서, 현재 미확인]` 태그.
데이터 소스 간 모순: 양쪽 모두 기술 + `[데이터 충돌]`, 임의 선택 금지.

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
| 빌드 파일 | `pom.xml`, `build.gradle`, `package.json`, `requirements.txt` 등 | 선택 | 자동 감지. 감지 실패 시 "기술 스택 미확인" 안내 후 수동 입력 요청 |
| auto memory | `MEMORY.md` + 하위 파일 | 선택 | 이전 대화 교정 사실 없이 진행, 추정 정확도 3/5로 하향 |

## 프로젝트 컨텍스트 (필수, 호출 전 read)

> [WARN] 하드코딩 없이 데이터에서 최신 현황 확인.

다음 파일이 존재하면 우선 read 하여 회사, 제품, 기술 스택, 조직 파악:
- `CLAUDE.md` (자동 로드, 회사, 제품, 기술 스택, 컨벤션)
- `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md`
- `.local.claude/INFRASTRUCTURE.md` (인프라, CI/CD)
- `.local.claude/team.md` 또는 멤버 매핑 파일
- `.local.claude/biz-rules.md` (비즈니스 규칙)
- `.local.claude/modules/*.md` (모듈 상세, 변경 감지된 모듈만)

도메인 약어와 모듈 명칭은 CLAUDE.md 의 "도메인 약어" 섹션 따름.

## 모드 판단

| 입력 | 모드 | 예상 소요 |
|------|------|----------|
| `/tech-diagnosis` (기본) | **종합 진단**: 3영역 전체, 검증 루프 포함 | ~30분+ |
| `arch` 또는 `아키텍처` | **아키텍처 심층**: 영역 1만 | ~15분 |
| `org` 또는 `조직` | **조직 운영**: 영역 2만 | ~15분 |
| `roadmap` 또는 `전략` | **기술 전략**: 영역 3만 | ~15분 |
| `delta` 또는 `변화` | **델타**: 이전 보고서 대비 변화만 | ~10분 |
| `metrics` 또는 `지표` | **대시보드**: 핵심 지표만 1페이지 | ~5분 |

## 프로세스: 3단계 검증 루프

### Phase 1: 정량 데이터 수집

**1-1. 이전 보고서 + 기존 분석 확인**

```bash
# 이전 /tech-diagnosis 보고서
ls .local.claude/reports/ 2>/dev/null | grep -iE 'tech-diagnosis' | sort | tail -3

# 기존 회사 진단 보고서 (조직/고객사 데이터 재활용)
ls .local.claude/reports/ 2>/dev/null | grep -iE '(심층진단|회사진단)' | sort | tail -1
```

- 이전 /tech-diagnosis 보고서는 Read 하여 핵심 지표 추출 (비교 기준)
- 이전 보고서의 `[미검증]` 태그 항목을 추출해 이번에 검증 시도
- 회사 진단 보고서는 조직/고객사 데이터 재활용 (측정 불필요)

**1-2. 코드베이스 정량 측정**

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**:
> - Bash: 코드 규모 측정(`find *.java | wc -l`, `find *.xml | wc -l`, `find *.js | wc -l`), git 활동(`git log --since=<date> | wc -l`, `git shortlog`, `git log --name-only`), 보안 grep, deprecated API grep, 의존성 파일 추출을 전부 동시에
> - Glob: `pom.xml`, `build.gradle*`, `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml` 병렬 탐색
> - Read: `CLAUDE.md`, `bot/INDEX.md` 또는 `ONBOARDING.md`, `INFRASTRUCTURE.md`, `biz-rules.md`, `team.md`, auto memory 를 Bash 측정과 병렬 로드
> - (옵션) WebSearch: 감지된 스택별 EOL/마이그레이션 2~3 쿼리 동시

> [WARN] **Windows/Git Bash 호환 주의**: `find <path> -exec wc -l {} +`는 배치 분할 시 부정확. `xargs -0 cat | wc -l` 패턴 사용.
> [WARN] **JS 측정 시 thirdparty/, fw/ 제외.** 벤더 라이브러리가 수백 MB라 포함하면 측정값이 크게 왜곡된다.

```bash
# 전체 코드 규모 (정확한 측정)
echo "=== Java ===" && find . -name "*.java" -path "*/src/main/*" | wc -l
echo "=== Java lines ===" && find . -name "*.java" -path "*/src/main/*" -print0 | xargs -0 cat 2>/dev/null | wc -l
echo "=== Mapper XML ===" && find . -name "*.xml" -path "*/mapper/*" -print0 | xargs -0 cat 2>/dev/null | wc -l
echo "=== Business JS (no vendor) ===" && find . -name "*.js" -path "*/static/*" -not -path "*/static/fw/*" -not -path "*/static/thirdparty/*" -print0 | xargs -0 cat 2>/dev/null | wc -l
echo "=== HTML ===" && find . -name "*.html" -path "*/templates/*" -print0 | xargs -0 cat 2>/dev/null | wc -l

# 테스트 현황
echo "=== Test files ===" && find . -name "*.java" -path "*/src/test/*" | wc -l

# 모듈별 파일 수
find . -name "*.java" -path "*/src/main/*" | sed 's|/src/main.*||' | sort | uniq -c | sort -rn | head -20

# God class (리팩토링 후보)
find . -name "*Svc.java" -path "*/src/main/*" -exec sh -c 'wc -l "$1"' _ {} \; 2>/dev/null | sort -rn | head -10

# 보안 점검 — 프로젝트 기술 스택에 맞게 패턴 치환
# 기본: 자격 정보 하드코딩, 평문 비밀, 세션 설정
grep -rnE "(password|secret|api_?key|token)\s*[:=]\s*['\"][^'\"]{8,}" --include="*.properties" --include="*.yml" --include="*.yaml" --include="*.env*" 2>/dev/null | grep -v target
grep -rn "SessionCreationPolicy" --include="*.java" 2>/dev/null | grep -v target
grep -rl "HttpSession" --include="*.java" 2>/dev/null | grep -v target | wc -l

# 의존성 현황 — 프로젝트 빌드 파일 자동 감지 (있는 것만 실행)
for f in pom.xml build.gradle build.gradle.kts package.json requirements.txt Cargo.toml go.mod pyproject.toml; do
  [ -f "$f" ] && { echo "=== $f ==="; grep -E "version|java-version|node|python" "$f" 2>/dev/null | head -20; }
done

# deprecated API — CLAUDE.md 에서 감지한 스택에 맞춰 아래 패턴 치환
# Java: javax.* (Jakarta 전환), System.out (로깅 대체)
# Python: imp (importlib), print (logging)
# JS: var (let/const), require (import)
echo "=== javax (Jakarta 전환 대상) ===" && grep -rl "javax\." --include="*.java" 2>/dev/null | grep -v target | wc -l
echo "=== System.out ===" && grep -rl "System\.out\.print" --include="*.java" 2>/dev/null | grep -v target | wc -l

# 저장소 크기 + vendor/thirdparty 부피 (감지되는 대로)
du -sh .git/ 2>/dev/null
for d in thirdparty vendor node_modules .venv dist; do [ -d "$d" ] && du -sh "$d"; done 2>/dev/null

# git 활동 (30일)
git log --since="30 days ago" --oneline | wc -l
git shortlog -sn --since="30 days ago"
git log --since="30 days ago" --merges --oneline | wc -l
git log --since="30 days ago" --format="%ad" --date=format:"%A" | sort | uniq -c | sort -rn
git log --since="30 days ago" --format="%ad" --date=format:"%H" | sort | uniq -c | sort -rn

# 핫스팟 (변경 집중 파일)
git log --since="30 days ago" --name-only --format="" | grep -v "^$" | sort | uniq -c | sort -rn | head -20

# 주간 커밋 추세 (12주)
git log --since="12 weeks ago" --format="%ad" --date=format:"%Y-W%V" | sort | uniq -c

# 모듈별 기여자 (지식 분포 파악)
for dev in $(git log --since="30 days ago" --format="%an" | sort -u | head -10); do
  echo "=== $dev ===" && git log --since="30 days ago" --author="$dev" --name-only --format="" | sed 's|/src/.*||' | sort -u | head -5
done
```

GitHub 데이터 (가능한 경우):
- `mcp__github__list_pull_requests`: PR 현황, 머지 빈도, 리뷰어
- `mcp__github__list_issues`: 이슈 백로그, 라벨 분포

**1-3. 내부 문서 수집**

**[필수]**
- `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md`: 아키텍처 현황
- `.local.claude/INFRASTRUCTURE.md`: 인프라, CI/CD, 배포
- `.local.claude/biz-rules.md`: 비즈니스 규칙 (기술 정합성)
- `.local.claude/team.md`: 조직 구조 + 멤버 매핑
- auto memory (MEMORY.md + 하위 파일): 이전 대화에서 교정된 사실

**[기간 데이터]** (이전 보고서 이후 또는 30일)
- `.local.claude/daily/`: 개발자 고민, 기술 이슈
- `.local.claude/briefing/`: 최근 5개 (코드 변경 흐름)
- `.local.claude/meetings/`: 기술 의사결정
- `.local.claude/reports/*심층진단*`: 회사 진단 보고서 (조직/고객사 재활용)

**[선택]**
- `.local.claude/modules/*.md`: 변경 감지된 모듈만

**1-4. 외부 기술 트렌드 (WebSearch)**

WebSearch 쿼리는 1-2단계에서 측정한 프로젝트 기술 스택과 버전을 동적 대입:

```
1. "{프레임워크 이름} {현재 버전} EOL migration"
2. "{언어} {현재 버전} end of life migration {현재연도}"
3. "{레거시 기술} modernization {산업 도메인} {현재연도}"
4. "{현재 DB} vs {대안 DB} {산업 도메인} cost {현재연도}"
5. "{산업 도메인} technology stack trends {현재연도}"
```

> 버전/연도/도메인은 모두 데이터 추출 결과를 사용. 하드코딩하지 않는다.

### Phase 2: 팩트 시트 + 사용자 검증

Phase 1의 정량 데이터와 핵심 가정을 사용자에게 제시하고 교정받는다.

```markdown
## 팩트 시트: 검증 요청

### 코드베이스 규모
| 항목 | 측정값 |
|------|--------|
| Java 소스 | N개 파일, ~Nk줄 |
| Mapper XML | ~Nk줄 |
| 비즈니스 JS | ~Nk줄 (thirdparty/fw 제외) |
| HTML 템플릿 | ~Nk줄 |
| 테스트 파일 | N개 |
| Git 저장소 | N GB (thirdparty N MB) |

### 기술 스택
| 기술 | 현재 버전 | EOL 상태 |
|------|----------|---------|
| {언어} | N | [상태] |
| {프레임워크} | N | [상태] |
| {DB/런타임} | N | [상태] |

### 조직 (team.md 기준)
- 개발 인력: N명 / 전체 N명
- 최근 변동: [변동 사항]

### 핵심 가정 (검증 필요)
- [ ] 프로젝트 모듈과 도메인 약어 매핑 (CLAUDE.md 기준)
- [ ] Git/PR 도입 시기와 현재 성숙도
- [ ] 코드 리뷰 범위와 방식
- [ ] 배포 빈도와 다운타임
- [ ] [이전 보고서 미검증 항목]

**위 내용 중 틀린 것이 있으면 알려주세요.**
```

**`AskUserQuestion`으로 검증을 요청.** 사용자 응답 후 교정 반영하고 Phase 3 진행.

### Phase 3: 3영역 분석 + 자기 검증

Phase 2에서 교정된 팩트를 기반으로 3영역 분석 수행.

---

## 영역 1: 아키텍처 건강도

### 1-1. 기술 스택 현황표

| 기술 | 현재 버전 | 최신 LTS | EOL 상태 | 위험도 | 마이그레이션 복잡도 |
|------|----------|---------|---------|:------:|:-----------------:|

각 기술에 대해:
- EOL 이후 경과 기간 (WebSearch에서 확인한 정확한 날짜)
- 알려진 보안 취약점 (CVE 수 또는 주요 건)
- 마이그레이션 시 영향 범위 (파일 수. Phase 1 bash에서 측정한 javax.* 파일 수 등)
- 자동화 도구 존재 여부 (OpenRewrite 등, WebSearch에서 확인)

### 1-2. 아키텍처 성숙도 매트릭스

| 영역 | 현재 수준 | 목표 수준(1년) | 갭 | 우선순위 |
|------|:--------:|:------------:|:--:|:--------:|

5단계 척도: 1) 수동/없음, 2) 일부 자동화, 3) 표준화, 4) 측정 가능, 5) 최적화

각 영역의 판정 근거를 인라인으로 명시 (코드에서 확인한 사실 기반).

### 1-3. 기술 부채 인벤토리

**위험도 상 (즉시)** / **중 (분기 내)** / **하 (장기)**

각 항목:
- 문제 명칭
- 현상 + **검증 상태** (`[코드 검증]` 또는 `[문서 기술, 코드 미검증]`)
- 비즈니스 임팩트
- 해결 방안 (단계별, 공수 **범위** min~max, 전제조건 명시)
- 선행 의존성
- 이전 보고서 대비: `[NEW]` / `[CHANGED]` / `[RESOLVED]` / `[WORSENED]` / `[UNCHANGED]`

**숨은 전제조건 점검**: 해결 방안 권고 시 기술적 전제를 코드에서 확인.
예: Blue-Green 권고라면 `SessionCreationPolicy.STATELESS` 확인, HttpSession/SseEmitter 인메모리 상태 확인

부채 간 의존 관계 그래프 (텍스트):
```
[부채 A]
  └─ [부채 B] (A 해결이 선행)
       └─ [부채 C]
```

**의사결정 포인트:** 이번 주 / 이번 달 / 이번 분기에 해야 할 기술 액션 각 1줄

### 1-4. 단일 장애 지점 (SPOF) 맵

| 컴포넌트 | 장애 시 영향 | 현재 대책 | 권고 |
|---------|-----------|---------|------|

### 1-5. 보안 자세 평가

| 항목 | 상태 | 심각도 | 권고 |
|------|------|:------:|------|

Phase 1 bash에서 측정한 보안 데이터(평문 비밀, 취약 라이브러리, 인증과 인가 결함 등) 기반.

### 1-6. 빌드/배포 파이프라인 평가

| 항목 | 현재 | 업계 표준 | 갭 |
|------|------|---------|-----|

**의사결정 포인트:** 배포 파이프라인에서 가장 급한 개선 1줄

---

## 영역 2: 엔지니어링 조직 운영

### 2-1. 팀 구조 & 역량 분포

| 팀 | 인원 | 핵심 기술 | 커버 영역 | 갭 |
|----|:----:|---------|---------|-----|

team.md + 회사 진단 보고서에서 최신 데이터 활용.
**숨은 이중 역할** (기획자 QA 겸임 등) 탐지. daily/meetings에서 확인.

### 2-2. 버스 팩터 분석

| 인물 | 독점 영역 | 대체 인력 | 버스팩터 | 위험도 |
|------|---------|:--------:|:-------:|:-----:|

지식 집중도 히트맵: **Phase 1의 "모듈별 기여자" bash 결과**를 기반으로 동적 생성. 하드코딩하지 않는다.

```
[git log 기반 동적 생성]
            모듈A  모듈B  모듈C  ...
개발자1     ████   ░░░░   ▓▓▓▓
개발자2     ░░░░   ████   ░░░░
...
████ = 독점(해당 모듈 커밋 80%+)  ▓▓▓▓ = 주력(30%+)  ░░░░ = 가능(1%+)
```

### 2-3. 개발 생산성 지표

| 지표 | 값 | 추세 | 맥락 |
|------|:--:|:----:|------|

> "맥락" 컬럼이 핵심. 예: PR 머지 7건/239커밋은 수치만 보면 3%지만, 맥락은 "SVN에서 Git 전환 {N}주차, 이슈에서 PR, 머지로 이어지는 흐름 정착 중"

### 2-4. 코드 리뷰 & 품질 게이트

| 항목 | 현재 | 권고 |
|------|------|------|

daily/meetings + auto memory에서 리뷰 문화의 **실제 현황** 확인. git 통계만으로 판단하지 않는다.

### 2-5. 온보딩 효율

| 항목 | 현재 | 목표 |
|------|------|------|

### 2-6. 기술 의사결정 로그

| 날짜 | 의사결정 | 결정자 | 근거 | 결과 | 출처/신뢰도 |
|------|---------|--------|------|------|-----------|

확인된 결정은 일반체, 추정은 *이탤릭* + `[간접 추론]`.

**의사결정 포인트:** 조직 측면에서 가장 급한 액션 1줄

---

## 영역 3: 기술 전략 & 로드맵

### 3-1. 기술 레이더 (Adopt / Trial / Assess / Hold)

| 상태 | 기술 | 이유 |
|------|------|------|

### 3-2. 마이그레이션 로드맵

> 하드코딩하지 않는다. Phase 1에서 측정한 현재 상태 + WebSearch에서 확인한 EOL/마이그레이션 경로를 기반으로 **데이터 기반 로드맵을 도출**한다.

각 마이그레이션에 대해:
- 현재에서 중간 단계를 거쳐 목표까지 (구체적 버전)
- 선행 조건 (어떤 마이그레이션이 먼저여야 하는가)
- 비즈니스 트리거 (왜 지금 해야 하는가)
- 공수 **범위** (min~max 인월, 전제조건 명시)
- 자동화 도구 활용 가능 여부 (WebSearch 결과)
- 리스크 + 롤백 전략

### 3-3. 기술 투자 우선순위 (ICE)

| 투자 항목 | Impact | Confidence | Ease | ICE | 비즈니스 연결 | 순위 |
|----------|:------:|:----------:|:----:|:---:|------------|:----:|

### 3-4. Build vs Buy vs Partner

| 영역 | Build | Buy | Partner | 권고 |
|------|-------|-----|---------|------|

### 3-5. 아키텍처 목표 상태 (To-Be)

현재 vs 12~18개월 목표. Phase 1 측정값 + Phase 2 교정값 기반으로 도출.

### 3-6. 기술 KPI 대시보드

| KPI | 현재 (측정값) | 3개월 | 6개월 | 12개월 |
|-----|:----------:|:-----:|:-----:|:------:|

> 목표치를 하드코딩하지 않는다. 현재 측정값과 영역 1~3 분석을 기반으로 **현실적 목표**를 도출. 예: 현재 PR 비율이 도입 초기라면 3개월 목표를 50%로, 100%로 하지 않는다.

**의사결정 포인트:** 3개월 내 달성해야 할 가장 중요한 KPI 1개와 이유

---

### Phase 3-B: 자기 검증 (Adversarial Review)

**Adversarial Review**: 핵심 권고/판단 Top 3~5 각각에 대해:
1. **근거 재점검**: 코드/측정 기반인가, 문서 기술인가? 단일 출처인가 교차 확인인가? `[코드 검증]` vs `[문서 기술, 코드 미검증]` 구분 명확한가?
2. **전제 검증**: 권고가 유효하려면 어떤 전제가 필요한가? 그 전제가 코드에서 확인되는가? (예: Blue-Green 이면 SessionCreationPolicy.STATELESS + 인메모리 상태 부재)
3. **반대 증거 탐색**: "왜 이미 하지 않았나?" / "현재가 충분하다면?" 같은 반박 1개 이상 탐색. auto memory 교정 사실이 이번 보고서에서 다시 잘못 기술되지 않았는지 재점검

반박 유효 시 본문 수정, 부분 반박 시 "단, ~의 가능성도 있음" 인라인 추가.

보고서 초안 완성 후:

1. **반대 증거 탐색**: 핵심 권고 Top 5 각각에 대해 "이 권고가 틀릴 수 있는 근거는?" 1개+ 제시
2. **전제조건 재점검**: 공수 추정에 포함된 전제조건이 코드에서 확인되었는지 재확인
3. **태그 점검**: `[코드 검증]`, `[문서 기술, 코드 미검증]`, `[단일 출처]`, `[데이터 충돌]` 태그 누락 없는지
4. **이전 오류 재발 점검**: auto memory 교정 사실이 이번 보고서에서 다시 잘못 기술되지 않았는지
5. **반박이 유효하면** 본문 수정 또는 인라인 ("단, ~의 가능성도 있음")

---

## 출력 구조

```yaml
---
type: tech-diagnosis
date: YYYY-MM-DD
mode: full | arch | org | roadmap | delta | metrics
previous: YYYY-MM-DD
areas: 1,2,3
data-sources:
  bash-measurements: N회
  github: issues N개, PRs N개
  web-searches: N회
  documents: N개
---
```

```markdown
# 기술 진단 보고서

> **분석 기준일**: YYYY-MM-DD
> **관점**: 기술 / VP Engineering
> **코드베이스**: Java ~Nk줄 (N개 파일), 테스트 N개
> **이전 진단**: YYYY-MM-DD (또는 최초)
> **데이터 한계**: git/코드 측정은 객관적. 조직/문화 판단은 {사용자닉네임} 1인 관점 기반.

## 핵심 판단 (3줄)
1. [가장 급한 기술 리스크, 한 줄]
2. [가장 큰 조직 병목, 한 줄]
3. [지금 해야 할 기술 투자, 한 줄]

[변화 요약 (이전 보고서가 있을 때)]

---
## 영역 1~3
[각 영역의 마지막 섹션에 **의사결정 포인트:** 필수]
---

## 핵심 권고 Top 5
| 순위 | 권고 | 근거 | 공수(범위) | 기한 | 담당 |
|:----:|------|------|:--------:|------|------|

## 다음 진단까지 추적할 액션아이템
| # | 액션 | 담당 | 기한 | 성공 기준 |
|---|------|------|------|----------|

## Adversarial Review 결과
[Phase 3-B 자기 반박 내용 요약]

## 부록: 코드베이스 규모 상세
[Phase 1 bash 측정 결과 테이블]

## 부록: 신뢰도 및 한계
| 항목 | 신뢰도 | 한계 |
|------|:------:|------|
```

**metrics 모드** (1페이지, bash 측정 위주):
```markdown
# 기술 대시보드 (YYYY-MM-DD)

## 코드베이스
Java: ~Nk줄 (N개) | XML: ~Nk줄 | JS: ~Nk줄 | 테스트: N개

## 핵심 지표
| KPI | 현재 | 이전 | 추세 | 목표 |
|-----|:----:|:----:|:----:|:----:|
| PR 머지 비율 | | | | |
| 테스트 커버리지 | | | | |
| Lead time p50 | | | | |

## 주의 신호
- [항목]
```

**이전 미검증 항목 추적** (이전 보고서가 있을 때):
```markdown
### 이전 미검증 항목 검증 결과
| 이전 태그 | 항목 | 이번 검증 결과 |
|----------|------|--------------|
| [코드 미검증] | Blue-Green 세션 의존성 | [OK] SessionCreationPolicy.STATELESS 확인, 단 SessionSvc/SseSvc 인메모리 상태 존재 |
```

## 파일 저장

Frontmatter (CONTRACT 7-2절 표준): `category: reports, retention: 30d, harvest_targets: [biz-rules.md]`

```bash
mkdir -p .local.claude/reports
```

| 모드 | 저장 경로 |
|------|----------|
| 종합 | `.local.claude/reports/YYYY-MM-DD-tech-diagnosis.md` |
| 영역별 | `.local.claude/reports/YYYY-MM-DD-tech-diagnosis-{영역}.md` |
| 델타 | `.local.claude/reports/YYYY-MM-DD-tech-diagnosis-delta.md` |
| 대시보드 | `.local.claude/reports/YYYY-MM-DD-cto-dashboard.md` |

저장 후:
```
[OK] 저장 완료: .local.claude/reports/YYYY-MM-DD-tech-diagnosis.md
[영역] 영역: N개 | 기술부채: N개(상N/중N/하N) | 버스팩터 최소: N
[요약] 코드: Java ~Nk줄, 테스트 N개 | 다음 진단 권고: 2주~1개월
[WARN] Adversarial Review: 반박 N건 중 N건 본문 반영
```

## 다음 스킬 연결

- 기술부채 액션은 `/todo`
- 마이그레이션 방향 발산은 `/brainstorm`
- 기술 결정 명세화는 `/prd`
- 팀 프로세스 변경 공유는 `/draft`
- 조직/채용/자원배분은 `/business-diagnosis`
- 비즈니스 관점 보완은 `/business-diagnosis`

## 제약조건

- **정량 측정은 코드에서 직접.** bash 결과를 근거로 사용. 문서 수치는 교차 검증
- **공수 추정은 범위 + 전제조건.** 단일 숫자 금지
- **숨은 전제조건 점검.** 기술 권고 시 코드 레벨 전제를 확인 (세션, 인메모리 상태 등)
- **git 지표 ≠ 생산성.** 커밋 수를 개인 평가에 사용 금지. 맥락 함께 기술
- **사람 판단은 복수 출처.** 단일 출처면 `[단일 출처]` 또는 기술하지 않음
- **모순은 양쪽 기술.** `[데이터 충돌]` 태그, 임의 선택 금지
- **정보 신선도.** 30일+ 문서는 `[N일 전 문서]` 태그
- **하드코딩 금지.** 버전, 연도, 조직 구성, KPI 목표치, 로드맵 타임라인 모두 데이터에서 도출
- **자기 검증 필수.** Phase 3-B Adversarial Review 실행
- **다른 보고서와의 관계**: 기술 관점은 "기술", /business-diagnosis는 "돈, 시간, 사람", /product-diagnosis는 "고객과 제품". 상호 참조 권장

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT 6-1절** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경/규모]** git 저장소 2GB+ (또는 커밋 5만+)인 경우
- 신호: `du -sh .git` 기준 2GB 이상 또는 타임아웃 위험 감지
- 대응: git log/blame 에 `--since-days 7` 자동 적용 + 범위 축소 경고 표시

**[도메인 특수성]** 이종 기술 스택 다수 감지
- 신호: 언어 3종+ / 서비스 5개+ 혼재 (모노레포, 마이크로서비스)
- 대응: 주 스택만 우선 심층 분석, 나머지는 `[부분 분석]` 태그로 개요 수준만 제공
