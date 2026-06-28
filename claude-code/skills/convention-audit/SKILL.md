---
name: convention-audit
description: 최근 커밋의 코딩 스타일을 분석하여 기존 컨벤션(fe-convention-final.md, be-convention-final.md)과 비교합니다. 이탈/추가/수정 후보를 도출하고, 승인된 항목만 컨벤션 문서에 반영합니다.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

## 역할

최근 커밋의 코딩 패턴을 분석하여, 기존 컨벤션 문서와의 괴리를 감지하고 문서를 최신 상태로 유지한다.

톤: 관찰·기록 중심. 판단보다 사실. 개발자별 차이를 부정적으로 평가하지 않음.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 최근 briefing | `.local.claude/briefing/` | 선택 | 새 패턴 후보 수집 불가, git log 로만 추론 |
| 이전 convention-audit | `.local.claude/convention-audit.md` | 선택 | 첫 실행 모드 — 이탈/추가/수정 분류의 "이탈" 기준 부재, 일반 권고만 제공 |

## 컨벤션 문서 위치

프로젝트 컨벤션 문서 위치는 다음 패턴으로 자동 탐색 (있는 것만 활용):

| 문서 유형 | 일반 경로 패턴 | 역할 |
|----------|-------------|------|
| FE 컨벤션 | `.local.claude/fe-guide/*.md` 또는 비슷한 위치 | FE 비교 기준 |
| BE 컨벤션 | `.local.claude/be-guide/*.md` 또는 비슷한 위치 | BE 비교 기준 |
| 프로젝트 컨벤션 | `CLAUDE.md` (자동 로드) | 금지 사항, 정적 분석 룰, 에디터 컨벤션 |
| paths 기반 규칙 | `.claude/rules/*.md` | 특정 경로에 적용되는 규칙 |

## 입력 파싱

| 입력 | 동작 |
|------|------|
| `/convention-audit` (기본) | 최근 2주, 전체 팀원 |
| `/convention-audit 1주` / `3일` | 기간 지정 |
| `/convention-audit 2026-04-01..2026-04-10` | 지정 기간 |
| `/convention-audit @{닉네임}` | 특정 팀원 필터 (`.local.claude/team.md` 의 매핑 표로 git author → 닉네임) |
| `/convention-audit fe` | FE만 분석 |
| `/convention-audit be` | BE만 분석 |
| `/convention-audit apply 2026-04-14` | 기존 보고서의 승인 항목을 컨벤션 문서에 반영 |

복합 입력 가능: `/convention-audit 1주 @{닉네임} be`

## 분석 모드 동작

### Phase 1: 데이터 수집

> **[1M 활용]** 다음을 **단일 메시지에서 병렬 호출**:
> - Bash: `git log --since --name-only`, `git log --stat`, 언어별 `git log -p` 전부 한 번에
> - Read: 기존 FE/BE 컨벤션 문서, `.local.claude/convention-audit.md` 이전 audit
> - Glob: `.local.claude/briefing/*.md` 최근 3건

```bash
# 기간 내 커밋에서 변경된 파일 목록
git log --since="2 weeks ago" --name-only --format="%h %an %ad %s" --date=short

# 변경 통계
git log --since="2 weeks ago" --stat --oneline

# Java diff (BE 분석)
git log --since="2 weeks ago" -p -- "*.java"

# JS diff (FE 분석) — 프로젝트의 JS 위치
git log --since="2 weeks ago" -p -- "{프로젝트 JS 디렉터리}/*.js"

# 데이터 접근 diff (프로젝트의 SQL/Mapper/Repository 파일)
git log --since="2 weeks ago" -p -- "{프로젝트 데이터 접근 패턴}"
```

팀원 필터: `--author="git실명"` 추가. `.local.claude/team.md` 에서 닉네임→실명 매핑.

**최근 briefing 참조** — 핵심 변경에 집중:
```bash
ls .local.claude/briefing/ | tail -3
```
최근 브리핑의 "코드 품질 메모"와 "작업 요약"을 읽어 분석의 출발점으로 활용.

### Phase 2: 패턴 추출 & 비교

기존 컨벤션 문서를 Read한 뒤, diff에서 추출한 패턴과 비교.

#### BE 체크 항목 (be-convention-final.md 대응)

| 섹션 | 체크 포인트 | Grep 패턴 |
|------|-----------|----------|
| 1. Service 구조 | 어노테이션 순서, DI 방식 | `@Service`, `@Autowired`, `@RequiredArgsConstructor` |
| 2. 메서드 네이밍 | CRUD 접두사 (find/save/del/get) | 신규/변경 메서드명 |
| 3. 트랜잭션 | 클래스 vs 메서드 레벨, readOnly | `@Transactional` |
| 4. Validation | 프로젝트 검증/예외 유틸 패턴 | 프로젝트 공통 검증·예외 클래스명 |
| 5. Controller | URL 패턴, 응답 래핑 | `@PostMapping`, `@GetMapping`, 프로젝트 응답 래퍼 |
| 6. 데이터 접근 (Mapper/Repository) | Read/Write 분리, SQL 문법 | 프로젝트 DB 표준 함수 (CLAUDE.md 참조) |
| 7. 이벤트 | ApplicationEventPublisher 사용 | `@EventListener`, `publishEvent` |
| 10. Save 메서드 | 헤더-디테일 순서, 검증 위치 | save 메서드 구조 |
| 11. DTO 설계 | 상속, 네이밍 규칙 | 프로젝트 DTO 베이스 클래스 상속 |
| 12. 로깅 | 표준 로거 어노테이션 vs 수동 Logger | 로거 선언 패턴 |

#### FE 체크 항목 (fe-convention-final.md 대응)

| 섹션 | 체크 포인트 | Grep 패턴 |
|------|-----------|----------|
| 2. JS 모듈 구조 | 프로젝트 모듈 패턴, var 선언 | 프로젝트 모듈 진입점 함수, 모듈 스코프 변수 |
| 3. 섹션별 상세 | URL 상수 네이밍 (UPPER_SNAKE vs camelCase) | `let.*Url =`, `const.*URL =` |
| 4. AJAX 호출 | 프로젝트 AJAX 유틸, async/await, Promise.all | 프로젝트 AJAX 유틸 호출, `async`, `Promise.all` |
| 5. 팝업 호출 | 프로젝트 팝업 유틸 패턴 | 프로젝트 팝업 호출 함수명 |
| 8. 저장/삭제 | save 함수 구조 | 저장 함수 내부 구조 |
| 14. Empty 체크 | 프로젝트 empty 유틸 vs 직접 비교 | 프로젝트 empty 유틸, `=== ''`, `== null` |
| 15. 금지 사항 | 약한 난수, eval, 전역 셀렉터 | `Math.random`, `eval(`, 모듈 스코프 외 전역 셀렉터 |

#### SQL 체크 항목

| 항목 | 체크 포인트 |
|------|-----------|
| Read/Write 분리 | SELECT와 INSERT/UPDATE/DELETE가 같은 XML에 있는지 |
| SQL 문법 | 프로젝트 DB 표준 함수 일관 사용 (CLAUDE.md 참조) |
| 페이징 | `ROW_NUMBER() OVER()` + `COUNT(*) OVER()` |
| SQL 주석 | `/* MapperName.methodId */` 패턴 |

### Phase 3: 분류 & 보고서 생성

> **[메타인지]** 이탈/추가/수정 판정 직전, 상위 후보 3건에 대해:
> 1. 근거 재점검 (git diff 실제 라인 vs 추출 패턴 서술 일치)
> 2. 전제 검증 (빈도 임계 — "2건 이상 또는 2명 이상" — 이 진짜 충족되는가)
> 3. 반대 증거 ("이 패턴이 개인 실험 아닌가? 왜 이미 컨벤션에 안 들어가 있었나?")

추출한 패턴을 3가지로 분류:

**1. 이탈 (Deviation)** — 기존 컨벤션에 명시된 규칙을 따르지 않는 코드
- **[높음]**: CLAUDE.md 금지사항 위반 (Math.random, eval, @Autowired 등)
- **[중간]**: 컨벤션 "권장" 미준수
- **[낮음]**: 스타일 차이, 또는 컨벤션에 "현실" 태그가 있는 항목의 이탈

**2. 추가 후보 (New Pattern)** — 컨벤션에 없지만 새로 등장한 패턴
- 조건: **2건 이상** 또는 **2명 이상** 사용
- 1건만 발견 시 보고만 하고 추가 후보로 올리지 않음 (개인 실험 가능성)

**3. 수정 후보 (Convention Drift)** — 컨벤션 문서의 내용이 현실과 괴리
- be-convention-final.md의 "현실" 태그 항목 비율 변화
- 컨벤션 부록의 "개발자별 스타일"과 최근 코드의 차이

## 출력 문서 구조

```markdown
# 컨벤션 감사 보고서 — YYYY-MM-DD

## 개요
| 항목 | 내용 |
|------|------|
| 분석 기간 | YYYY-MM-DD ~ YYYY-MM-DD |
| 대상 커밋 | N개 |
| 대상 개발자 | {닉네임1}, {닉네임2}, {닉네임3} (또는 전체) |
| 변경 파일 | Java N개, JS N개, XML N개 |
| 기준 문서 | fe-convention-final.md (작성일), be-convention-final.md (작성일) |

## 1. 이탈 패턴

### [높음] 금지사항 위반
| 파일:라인 | 위반 내용 | 컨벤션 근거 |
|----------|----------|------------|
| XxxSvc.java:45 | @Autowired 필드 주입 | BE 1-3: 생성자 주입 통일 |

### [중간] 권장 미준수
| 파일:라인 | 위반 내용 | 컨벤션 근거 |
|----------|----------|------------|
| (동일 형식) | | |

### [낮음] 스타일 차이
| 파일:라인 | 위반 내용 | 컨벤션 근거 |
|----------|----------|------------|
| (동일 형식) | | |

## 2. 추가 후보

| ID | 패턴 | 사용 위치 | 빈도 | 사용 개발자 | 제안 |
|----|------|----------|------|-----------|------|
| A-1 | Promise.all + async/await | {파일명}.js 외 2건 | 3건 | {닉네임1}, {닉네임2} | FE 4절에 비동기 처리 패턴 추가 |

## 3. 수정 후보

| ID | 컨벤션 항목 | 현재 문서 내용 | 실제 코드 현황 | 제안 |
|----|------------|-------------|-------------|------|
| M-1 | BE 1-2 필드 순서 | Mapper→Svc→Component "권장" | 최근 80% 준수 | "필수"로 격상 |

## 4. 코드 품질 메모
- 주석 처리된 코드: N줄 (파일 목록)
- 들여쓰기 불일치: N건
- 미사용 import/변수: N건

## 5. 승인 대기 항목

아래 항목 중 반영할 것을 선택하세요:
- [ ] A-1: FE 4절에 Promise.all + async/await 패턴 추가
- [ ] M-1: BE 1-2 필드 순서를 "필수"로 격상

> `/convention-audit apply YYYY-MM-DD` + 승인 항목 번호로 반영
```

## Apply 모드 동작

`/convention-audit apply 2026-04-14` 또는 `/convention-audit apply 2026-04-14 A-1,M-1` 으로 호출.

### 반영 흐름

```
1. 해당 날짜 보고서 Read
2. 승인 항목 확인 (인자로 지정 또는 사용자에게 질문)
3. 항목별 처리:

   추가 후보 (A-*):
     → 해당 컨벤션 문서 Read
     → 적절한 섹션에 패턴 + 코드 예시 추가
     → "(근거: convention-audit YYYY-MM-DD)" 태그

   수정 후보 (M-*):
     → 기존 내용 수정 (삭제 없이 [구패턴] 태그 + 신패턴 병기)
     → "(근거: convention-audit YYYY-MM-DD)" 태그

   이탈 (D-*):
     → 컨벤션 변경 아님. 해당 코드 수정이 필요하면 TODO 안내.

4. changelog.md에 변경 이력 추가
5. 보고서의 해당 항목에 [반영됨 YYYY-MM-DD] 표기
6. 컨벤션 문서 상단 "작성일" 줄에 업데이트 날짜 추가
```

### changelog.md 구조

```markdown
# 컨벤션 변경 이력

| 날짜 | 대상 문서 | 섹션 | 변경 내용 | 근거 |
|------|----------|------|----------|------|
| 2026-04-14 | fe-convention-final.md | 4. AJAX 호출 | Promise.all 패턴 추가 | convention-audit/2026-04-14.md A-1 |
```

## 파일 저장

Frontmatter (CONTRACT §7-2 표준): `category: reports, retention: 30d`

### 보고서
- `.local.claude/convention-audit/YYYY-MM-DD.md`
- 디렉터리 없으면 `mkdir -p`로 생성

### 변경 이력
- `.local.claude/convention-audit/changelog.md`
- 누적 기록. 삭제하지 않음.

## `/briefing` 연계

- convention-audit 실행 시 최근 3개 briefing 파일을 참조하여 "코드 품질 메모"와 패턴 변화 힌트를 수집
- briefing 하단 "다음 스킬 연결"에서 컨벤션 이탈 감지 시 이 스킬을 안내

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "최근 커밋이 팀 컨벤션을 따르나, 새 패턴이 생겼나?" | **이 스킬** | [OK] 핵심 — diff 단위 스타일 감사 + 컨벤션 문서 갱신 |
| "이 PR/변경에 버그·개선점이 있나?" | /review | [FAIL] 다루지 않음 — 정확성·로직 리뷰 축 |
| "아키텍처·기술부채가 건강한가?" | /tech-diagnosis | [FAIL] 다루지 않음 — 코드베이스 전체 정량 진단 축 |

이 스킬은 "컨벤션 일치/이탈"만 본다. 로직 버그는 /review, 구조·부채는 /tech-diagnosis 로 위임.

## 다음 스킬 연결

감사 완료 후 안내:
- 이탈 패턴 수정이 필요하면 → 직접 코드 수정 또는 PR 코멘트
- 비즈니스 규칙과 관련된 패턴이면 → `/biz-rules`
- 팀원과 논의가 필요한 항목이면 → 코드 리뷰 시 공유

## 제약조건

- **변경된 코드만 분석한다.** 전체 코드베이스 스캔이 아님. git diff 범위에 한정.
- 개발자별 스타일 차이를 **부정적으로 평가하지 않는다.** 사실만 기술.
- 컨벤션에 "현실" 태그가 있는 항목의 이탈은 심각도 "낮음".
- 패턴 빈도 1건은 보고만, 추가 후보 미분류 (개인 실험 가능성).
- apply 시 컨벤션 문서의 기존 내용을 삭제하지 않음 — [구패턴] 태그로 병기.
- 프로젝트별 도메인 약어·명칭은 CLAUDE.md "도메인 약어" 섹션 따름.

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[데이터 결함]** 이전 audit 결과와 현재 스캔이 상충
- 신호: `convention.md` 또는 이전 audit 출력에 "X는 금지"인데, 현재 코드 스캔에서 X가 우세 패턴
- 대응: 두 결과를 모두 기술 — "이전 규약: X 금지 / 현재 사용: X가 70%" → 사용자에게 규약 갱신 vs 코드 수정 선택 요청

**[환경·규모]** 분석 대상 커밋 1,000개 이상
- 신호: `git log` 대상 범위의 커밋 수가 1,000+
- 대응: 기간 축소 권장 — "최근 90일 또는 특정 모듈로 제한 권장, 현재 범위 강행 시 맥락 한계로 누락 위험"
