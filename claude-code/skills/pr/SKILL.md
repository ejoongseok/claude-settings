---
name: pr
description: 현재 브랜치의 변경 내용을 기반으로 프로젝트 PR 템플릿(`.github/PULL_REQUEST_TEMPLATE.md` 자동 감지)에 맞춘 PR 제목과 본문을 마크다운으로 생성합니다.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
---

> **외부-가시 문서** — [`rules/external-doc.md`](../../rules/external-doc.md) 10원칙(가독성 5 + 정직성 5) 준수. PR은 동료·리뷰어·후임자 참조 전제. 내부 경로(`.claude/*`, `.local.claude/*`) 금지, 내부 상수·플래그명 금지, 추측/확정 구분.

## 역할

현재 브랜치의 변경 사항(git diff, commit log, 변경 파일)과 대화 맥락을 분석하여 프로젝트 PR 템플릿(있을 시 `.github/PULL_REQUEST_TEMPLATE.md`, 없으면 CONTRACT 상 기본 구조)에 맞춘 제목과 본문을 마크다운으로 생성합니다.

**출력만 합니다. PR을 직접 생성하거나 push하지 않습니다.**

## 레포지토리 정보

GitHub owner/repo/base branch 는 프로젝트 컨텍스트에서 추출:
- `git remote -v` 로 remote URL 확인 → owner/repo 추출
- `git symbolic-ref refs/remotes/origin/HEAD` 또는 프로젝트 CLAUDE.md 의 브랜치 컨벤션에서 base branch 확인
- 추출 불가 시 사용자에게 확인 요청

## 정보 수집

> **[Opus 4.7 / 1M 활용]** 다음을 **단일 메시지에서 병렬 호출**:
> - Bash: `git branch --show-current`, `git status`, `git diff develop --stat`, `git log develop..HEAD --oneline`, `git diff develop`
> - GitHub MCP: `mcp__github__list_pull_requests` (최근 PR 3~5개)
> - Read: `.github/PULL_REQUEST_TEMPLATE.md`, `CLAUDE.md`

아래 순서로 현재 상태를 파악한다:

1. **현재 브랜치명**: `git branch --show-current`
2. **base 브랜치와의 diff 요약**: `git diff develop --stat` (또는 main)
3. **커밋 로그**: `git log develop..HEAD --oneline`
4. **변경된 파일의 상세 diff**: `git diff develop` (핵심 변경만 Read)
5. **이슈 번호**: 브랜치명에서 추출 (`Feature/#123` → `#123`)
6. **기존 PR 스타일 참고**: GitHub MCP `mcp__github__list_pull_requests`로 최근 PR 3~5개를 읽어 팀의 실제 작성 스타일(제목 형식, 본문 상세 수준) 확인

`$ARGUMENTS`가 제공되면 추가 맥락으로 활용 (예: `/pr {기능명} 구현`)

## PR 템플릿

`.github/PULL_REQUEST_TEMPLATE.md` 기반:

```markdown
## PR 제목

Feature/#이슈번호 변경 내용 요약

---

## 변경 내용

이번 PR에서 변경된 내용을 간단히 설명해주세요.

- 변경1
- 변경2

---

## 관련 이슈

Close #이슈번호

---

## 주요 변경 사항

- 주요 변경1 (파일 경로 포함)
- 주요 변경2

---

## 테스트 방법

1. 테스트 단계1
2. 테스트 단계2

---

## 영향 범위

- [ ] API 변경
- [ ] DB 스키마 변경
- [ ] 기존 기능 영향 있음
- [ ] 설정 파일 변경
- [ ] 없음

---

## 참고 사항

리뷰 시 참고 사항
```

## 작성 규칙

> **외부-가시 문서 공통 원칙 준수** — `rules/external-doc.md` (가독성 5 + 정직성 5 원칙). 아래는 PR 고유 가이드.

### 톤 & 수준
- **내부 문서 참조 금지** — `.local.claude/...`, `STATUS.md §10.4`, `ANALYSIS.md` 같은 내부 전용 문서 경로를 PR 본문에 넣지 않음. GitHub PR은 팀 외부에도 보일 수 있고, 내부 문서 경로는 의미 없는 소음
- **자기 완결적** — PR 본문만 읽고 변경 의도·테스트 방법·영향을 이해할 수 있어야 함. 외부 문서로 보내지 않고 필요한 맥락을 본문에 직접 서술

### PR 제목
- 형식: `Feature/#이슈번호 변경 내용 요약`
- 기존 커밋/PR 스타일과 일관성 유지
- 한국어 또는 영문 (기존 패턴 따름)

### 변경 내용
- git diff에서 **무엇이 바뀌었는지**를 비개발자도 이해할 수 있게 요약
- 신규 파일 추가 / 기존 파일 수정 / 삭제를 구분

### 주요 변경 사항
- 핵심 변경을 파일 경로와 함께 구체적으로 나열
- Controller, Service, Mapper, HTML, JS 등 레이어별로 정리하면 가독성 좋음

### 테스트 방법
- 리뷰어가 따라할 수 있는 구체적 단계
- URL 경로, 입력 데이터, 예상 결과 포함

### 영향 범위
- git diff에서 변경된 파일 유형을 분석하여 자동 체크
  - `*Ctrl.java`, `*Svc.java` 변경 → API 변경
  - `*.sql`, DDL 파일 → DB 스키마 변경
  - `application*.yml` → 설정 파일 변경
  - 기존 메서드 시그니처 변경 → 기존 기능 영향 있음

### 다이어그램

**항상 포함:**

| 다이어그램 유형 | 용도 |
|---------------|------|
| sequenceDiagram | 변경 범위에 맞는 요청 흐름 |

변경된 파일 범위에 따라 시작점을 결정:
- **풀스택** (FE + BE): `프론트 페이지 → 컨트롤러 → 서비스 → 데이터 접근`
- **백엔드만**: `컨트롤러 → 서비스 → 데이터 접근`
- **프론트만**: `프론트 페이지 → AJAX 호출 → API 엔드포인트`

- 변경된 API가 여러 개면 대표 1~2개만 그린다
- 기존 흐름에서 달라진 부분이 있으면 Note로 표시

**조건부 포함 (해당할 때만):**

| 조건 | 다이어그램 유형 | 예시 |
|------|---------------|------|
| 모듈 간 이벤트 흐름 변경 | flowchart | {모듈A} →\|Event\| {모듈B} |
| 상태 전이 로직 변경 | stateDiagram-v2 | {상태1} → {상태2} → {상태3} |
| DB 테이블 관계 변경 | erDiagram | {부모} \|\|--o{ {자식} |

- 조건에 해당하지 않으면 생략 (무조건 넣지 않는다)
- 노드 5개 이하로 간결하게 — 복잡하면 핵심 흐름만 추출
- 기존 흐름 → 변경 흐름 비교가 필요하면 Before/After로 나눠서 표현
- 다이어그램은 `## 주요 변경 사항` 또는 `## 참고 사항` 섹션에 배치

### 참고 사항
- 대화 맥락에서 리뷰어가 알아야 할 배경이 있으면 추가
- PoC/임시 코드가 있으면 명시

## 파일 저장

Frontmatter (CONTRACT §7-2 표준): `category: prs, retention: 30d`

PR 마크다운을 화면 출력과 동시에 파일로 저장한다.

### 저장 경로
- `.local.claude/prs/YYYY-MM-DD-#이슈번호-{간략설명}.md`
- 이슈 번호가 없으면: `.local.claude/prs/YYYY-MM-DD-{간략설명}.md`
- 디렉터리 없으면 `mkdir -p`로 생성

### 저장 시점
- PR 마크다운 생성 완료 시 자동 저장
- 저장 후 파일 경로 안내

## 출력

> **[Opus 4.7 / 메타인지]** 출력 전 자기 검증 (external-doc 10원칙 준수):
> 1. 근거 재점검 — 주요 변경사항이 실제 diff 기반인가? 추측·과장 없는가?
> 2. 전제 검증 — 내부 경로(`.local.claude/*`, `.claude/*`)·내부 상수·내부 플래그명이 본문에 노출되지 않았는가?
> 3. 반대 증거 — "리뷰어가 본문만 읽고 변경 의도·테스트 방법·영향을 이해할 수 있는가?" 자기 완결성 반박 1개 이상

화면에 마크다운으로 출력 (사용자가 복사하여 PR에 붙여넣기) + 파일로 저장.

사용자가 원하면 GitHub MCP (`mcp__github__create_pull_request`)로 PR을 직접 생성할 수도 있다고 안내. 단, 직접 생성은 사용자가 명시적으로 요청한 경우에만.

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경·규모]** diff 가 100 파일 이상
- 신호: `git diff --stat` 결과 변경 파일 100개 초과, 또는 라인 수 5000+
- 대응: 요약 모드로 전환(파일별 상세 생략, 디렉터리/모듈 단위 요약) + 분할 PR 권장 + 리뷰 부담 경고

**[의존성 부재]** `.github/PULL_REQUEST_TEMPLATE.md` 부재
- 신호: 저장소에 PR 템플릿 파일이 없음
- 대응: CONTRACT 기본 구조(요약/변경사항/테스트/체크리스트) 사용 + "템플릿 파일을 만들어두면 팀 일관성 향상" 안내
