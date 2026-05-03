---
name: dualize-docs
description: "디렉터리 내 모든 Markdown을 통합 이해해 AI 전용 bot/ + 사람 전용 human/ 으로 재구성하고, 메타 분석(모순·맹점·향후 방향)을 human/insights.md 로 도출합니다. 프로젝트 문서가 누적되어 읽기 비용이 커졌을 때 사용하세요."
argument-hint: "<directory-path> [--archive-source]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(mkdir *, ls *, find *, mv *, rm -rf *, wc *, date *, grep *, test *, sort *, head *, basename *, [ *)
effort: max
disable-model-invocation: true
---

대상 디렉터리의 `.md` 문서들을 **통합 이해**한 뒤, 세 가지 산출물을 생성합니다.

- `bot/` — **AI 에이전트 단독 참조 사실 레이어**. 표·코드경로·상태전이·규칙, 중복 0, 1파일 1주제
- `human/` — **사람용 설명 레이어**. Mermaid 다이어그램, 스토리텔링, AS-IS/TO-BE
- `human/insights.md` — **메타 분석**. 원본에는 없지만 여러 문서를 한꺼번에 봤기에 드러나는 모순·맹점·반복 패턴·향후 방향

**설계 원칙**:
- 사실은 `bot/` 에 단일 소스로 존재. `human/` 은 "왜"만, `human/insights.md` 는 "그래서 앞으로 어떻게"
- Opus 4.7 (1M context) 환경 전제 — **수집한 모든 원본을 메인 컨텍스트에 직접 Read** 하여 통합 이해. 서브에이전트 분할 금지. 1M context 의 진짜 강점은 여러 문서 간 **상호 참조·모순·반복 패턴** 을 한꺼번에 포착하는 것이고, 이 능력이 Pass 3 에서 가장 빛남
- 원본은 **기본 유지**. `--archive-source` 플래그 시에만 `archive/YYYY-MM-DD/` 로 이동
- **Windows + mingw bash 환경 전제**. 경로 구분자 `/`, `find`/`wc`/`grep` mingw 내장

**사용자 전역 CLAUDE.md 와 연결**: `bot/INDEX.md` 는 "디렉터리에 bot/ 있으면 무조건 거기부터" 규칙의 진입점.

---

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 원본 디렉터리 | 대상 경로의 실제 파일들 | **필수** | "대상 디렉터리 부재" 안내 후 종료 |
| 기존 bot/human 구조 | `{path}/bot/`, `{path}/human/` | 선택 | 처음부터 생성, 누적 병합 모드 비활성 |
| absorb-log | `.local.claude/docs/absorb-log.md` | 선택 | 증분 처리 불가 — 전체 재처리 |

---

## 경쟁 스킬과의 역할 경계

사용자·에이전트가 헷갈릴 수 있는 네 스킬의 명확한 분기:

| 이럴 때 | 어떤 스킬 | 왜 |
|--------|---------|-----|
| 만료 문서 식별·아카이브·`INDEX.md` 갱신 | `/garden` | 문서 수명 관리 전담 |
| 새 지식을 기존 메모리·CLAUDE.md·규칙에 통합 | `/absorb` | 지식 베이스 자동 반영 |
| CLAUDE.md 진단·최적화 | `/optimize-claude-md` | 메모리 설정 점검 전담 |
| 누적된 프로젝트 문서를 AI·사람 두 독자층에 재구성 + 메타 분석 | **`/dualize-docs`** | 출력 포맷 재구조화 + 1M context 기반 인사이트 |

**조합 권장**:
- `/dualize-docs` 후 `/garden` — 재구성 후 원본 아카이브 정리
- `/absorb` 후 `/dualize-docs` — 지식 통합 후 프로젝트 문서 재구성
- `/optimize-claude-md` 는 독립적 — 메모리 설정 전용

---

## 1단계: 입력 파싱

`$ARGUMENTS` 에서 분리:
- 첫 번째 토큰 = **대상 디렉터리 경로** (필수)
- `--archive-source` 플래그 (선택)

인자 비었으면 중단:
```
사용법: /dualize-docs <directory-path> [--archive-source]
예시:   /dualize-docs .local.claude/projects/{project-name}
       /dualize-docs .local.claude/projects/{project-name} --archive-source
```

---

## 2단계: 입력 검증

1. 경로 존재·디렉터리·쓰기 가능: `ls -ld <path>` + `test -w <path>`
2. `.md` 파일 1개 이상 존재: `find <path> -name "*.md" -not -path "*/bot/*" -not -path "*/human/*" -not -path "*/archive/*" | head -1`
3. 0개면 "Markdown 파일이 없습니다" 안내 후 중단

---

## 3단계: 재실행 감지 (사용자 확인 필수)

`<path>/bot/` 또는 `<path>/human/` 존재 시 AskUserQuestion:
- 질문: "대상 디렉터리에 이미 bot/ 또는 human/ 이 있습니다. 전면 재생성하시겠어요?"
- 옵션: "재생성" / "취소"

승인 시 `rm -rf <path>/bot <path>/human` 후 진행.

`--archive-source` 플래그 시 추가 확인: "원본 .md 를 archive/YYYY-MM-DD/ 로 이동합니다. 진행할까요?"

---

## 4단계: 소스 수집

```bash
find <path> -name "*.md" -not -path "*/bot/*" -not -path "*/human/*" -not -path "*/archive/*" | sort
```

목록과 줄 수 사용자에게 공유:
```
수집: N 파일, X 줄
  Y줄 <path>/STATUS.md
  ...
```

---

## 5단계: 통합 이해 (메인 컨텍스트 직접 Read)

**서브에이전트 위임 금지**. 모든 파일 순차 Read 후 mental model 에 확정:

- [ ] 모든 **표·상태전이·코드경로** 를 한 번은 맥락에 올렸는가
- [ ] **문서 간 상호 참조·모순·중복** 식별 (동일 사실이 2개 이상 파일에 등장하는 케이스 기록)
- [ ] **의사결정 타임라인** 복원 가능
- [ ] **미해결·차단 요소** 구분
- [ ] **반복 패턴** 포착 (여러 회의록·리뷰에서 되풀이되는 고민·결정·실수)
- [ ] **원본에 명시 안 된 맹점** 후보 (Pass 3 에서 활용)

파일 수 많으면 상위 개괄 파일(STATUS/README/INDEX) 먼저 → 나머지 그룹 순.

---

## 6단계: 삼중 분리 추출

### Pass 1 — 사실 레이어 → bot 후보

- 상태 전이 표 (코드값·이름·설명·트리거)
- 파일 경로 + 줄 번호 레퍼런스 — **완전 경로 필수, `...` 축약 금지**
- 심볼, API 엔드포인트, HTTP 메서드, 스키마
- 의존 관계·모듈 그래프
- 규칙·경계·금지
- 설정값·환경변수·프로퍼티 키
- 데이터 스키마·테이블 컬럼
- 외부 URL·사내 사본 경로

### Pass 2 — 설명 레이어 → human 후보

- 문제 정의·배경·촉발 요인
- 의사결정 이유·트레이드오프
- AS-IS vs TO-BE
- Mermaid·sequenceDiagram·ASCII 다이어그램
- 실패 사례·교훈
- 타임라인·의사결정 히스토리

### Pass 3 — 메타 분석 → `human/insights.md`

1M context 로 여러 문서 한꺼번에 봤기에 보이는 것들을 모읍니다. **원본 어떤 단일 문서에도 없는 내용**입니다. 7 카테고리:

- **모순·부정합**: 문서 A 와 문서 B 가 같은 주제에 다른 값 제시. 갱신 누락 or 상호 인식 차이
- **숨어있는 것**: 문서에 **잠재되어 있지만 아무도 연결 안 한** 관계·의존성·인과. 같은 원인을 다른 증상으로 다루거나, 서로 다른 문서의 개별 사실을 합쳐야 보이는 숨은 사실
- **놓친 것**: 했어야 하는데 **원본 어디에도 결과 기록 없는** 액션·확인·검증. 액션 아이템은 있지만 "완료" 표시만 있거나, 미수행 상태로 시간이 지나 잊힌 것들
- **맹점**: 모든 원본에서 **생각해본 적 없는 관점** (확장 시나리오·숨은 가정·외부 조건 변화)
- **아쉬운 점**: 문서 관리 관례·의사결정 속도·역할 분담의 구조적 개선 여지
- **반복 패턴**: 여러 회의록·리뷰·코멘트에서 **되풀이되는** 고민·결정·실수 → 구조적 교훈
- **향후 방향 제안**: 운영 맥락 + 실측 결과 바탕 우선순위 액션

**추출 규칙**:
- 각 항목에 **근거 출처** 필수 (원본 파일명:섹션 또는 줄번호)
- "확신 / 추정 / 가설" 신뢰도 태그 필수
- 비판 톤 아닌 건설적 제안 톤
- **스킬이 결정하지 않음** — 사용자가 판단·채택 여부 결정
- 해당 없는 카테고리는 섹션 자체 생략 가능 (빈 섹션 금지)

> **[Opus 4.7 / 메타인지]** Pass 3 insights.md 작성 완료 직후 Adversarial Review — 핵심 발견(모순·숨어있는 것·맹점·향후 방향 P1) Top 3 각각에 대해:
> 1. **근거 재점검**: 여러 원본을 실제로 교차 대조한 결과인가, 단일 문서 해석인가? 인용 위치(`파일:섹션`)가 실제로 해당 주장을 뒷받침하는가?
> 2. **전제 검증**: 이 insight 가 성립하려면 어떤 전제가 필요한가? (예: "모순" → 두 문서가 실제로 같은 대상·시점을 다룸이 확인)
> 3. **반대 증거 탐색**: "내가 해석을 잘못 연결하지 않았나?" / "원본 저자가 이미 알고 있었나?" — 반박 1개 이상 탐색. `[확신/추정/가설]` 태그가 실제 근거 강도와 일치하는지 재점검
>
> 반박 유효 시 insight 강등(`[확신]` → `[추정]`) 또는 섹션에서 제거, 부분 반박 시 "단, {가능성}" 인라인 추가.

### 주제 추출 휴리스틱 (bot/ 용)

| 성격 | bot 파일 후보 |
|------|-------------|
| 의사결정 기록 (시간순) | `decisions-timeline.md` |
| 구조·흐름 | `architecture.md` |
| 구현 파일·경로·코드 레퍼런스 | `implementation.md` |
| API·엔드포인트·스키마 | `api-contract.md` |
| 외부 호출자 가이드 | `caller-integration.md` |
| 카탈로그·인벤토리 | `modules.md`, `screens-catalog.md` 등 |
| 라이선스·계약·비용 | `license-and-constraints.md` |
| 외부 의사결정·액션 | `blockers.md` |
| 운영 함정·해결된 문제 | `known-issues.md` |
| 규칙·금지·컨벤션 | `rules.md` |

bot 파일 수는 **주제 수에 따라 자연스럽게**. 같은 주제를 두 파일로 쪼개거나 (과분할) 다른 주제를 한 파일에 섞지 (혼합) 않으면 됨. 작은 프로젝트는 3~5개, 큰 프로젝트는 10개 이상도 정상.

---

## 7단계: bot/ 산출

`mkdir -p <path>/bot` 후 생성.

### 파일 규칙

1. 주제 하나당 파일 하나. 혼합 금지
2. 크기: **150줄 이내 권장, 200줄 경고**
3. 파일명: kebab-case
4. Frontmatter 필수:
   ```yaml
   ---
   title: 주제 제목
   type: state-table | api-map | rule-set | decision-log | reference | catalog | known-issues | ...
   last-updated: YYYY-MM-DD
   source-files: [원본 상대 경로들]
   ---
   ```
5. 본문 첫 줄 INDEX 링크: `> 진입점: [INDEX.md](./INDEX.md)`
6. 우선순위: 표 > 불릿 > 서술
7. 코드 레퍼런스: `경로/파일.확장자:시작[-끝]` 완전 경로
8. 중복 금지: 같은 사실 두 파일 등장 → 한쪽 통합 + 반대쪽 링크

### `bot/INDEX.md` (READ FIRST 라우팅)

```markdown
# bot/ — AI 에이전트 진입점

> 이 디렉터리는 /dualize-docs 스킬로 YYYY-MM-DD 생성.
> 설명·배경은 ../human/README.md, 메타 분석·향후 방향은 ../human/insights.md 참조.

## 라우팅

| 파일 | 내용 | 갱신 |
|------|------|------|
| [decisions-timeline.md](./decisions-timeline.md) | ... | YYYY-MM-DD |
| ... | ... | ... |
```

---

## 8단계: human/ 산출

### `human/README.md` — 3단 구조 강제

```markdown
# {디렉터리 이름}

> 이 디렉터리는 "왜"를 담습니다. "무엇"은 [../bot/INDEX.md](../bot/INDEX.md), "그래서 어떻게"는 [insights.md](./insights.md) 참조.

## 1. 배경
## 2. 현재 상태
(요약 + **Mermaid 다이어그램 1개 이상** — README 에만 필수)

## 3. 남은 질문 · 의사결정

## 더 읽을 거리
- [architecture.md](./architecture.md) — ...
- [decisions.md](./decisions.md) — ...
- [insights.md](./insights.md) — 메타 분석·개선점·향후 방향
- [lessons.md](./lessons.md) — ...
```

### 보조 파일 (선택)

- `human/architecture.md` — AS-IS vs TO-BE 다이어그램 중심
- `human/decisions.md` — 의사결정 타임라인 스토리라인
- `human/lessons.md` — 실패 사례·교훈
- **`human/insights.md`** (아래 8.1)

### 8.1 `human/insights.md` — Pass 3 산출

```markdown
# 인사이트 — 메타 분석과 향후 방향

> 이 문서는 원본 N 파일을 한꺼번에 읽어서 드러난 것들입니다. 각 원본 단일 문서에는 없는 내용이라 **스킬이 1M context 로 추론한 것**이 섞여 있습니다. **[확신/추정/가설] 태그** 를 확인 후 사용자가 판단하세요.
> 사실은 [../bot/INDEX.md](../bot/INDEX.md), 배경·의도는 [README.md](./README.md) 참조.

## 1. 발견된 모순·부정합
- **[확신]** 근거: A.md:L34 vs B.md:L89 — 같은 주제 다른 값. 갱신 누락으로 추정
- **[추정]** ...

## 2. 숨어있는 것 (잠재된 연결·인과)
- **[가설]** C.md 의 X 와 D.md 의 Y 는 같은 이슈의 다른 증상일 가능성. 시기·담당자·키워드가 겹침. 두 문서를 개별로 읽을 때는 보이지 않음
- **[추정]** ...

## 3. 놓친 것 (미수행·미검증)
- **[확신]** E.md §3 의 "Z 를 제이에게 확인" 액션 — 이후 문서 어디에도 결과 기록 없음
- **[추정]** 회의 액션 #N — 완료 표시 없이 14일 경과

## 4. 맹점 (생각해본 적 없는 관점)
- **[가설]** 모든 원본에서 "X 동시성" 이 언급 안 됨 — 배포 후 병목 가능
- **[가설]** ...

## 5. 아쉬운 점
- **[확신]** 회의록 포맷 제각각 — 2개 회의가 서로 다른 템플릿. 통일 권장
- **[추정]** ...

## 6. 반복 패턴
- **[확신]** 여러 문서에서 "요구사항 철회 → 재작업" 패턴 2회 — 구조적 교훈: 불확실 외부 의사결정 시 PoC 선행
- **[추정]** ...

## 7. 향후 방향 제안 (우선순위순)
1. **[P1]** 근거 + 왜 중요한지 + 구체 액션 + 예상 공수
2. **[P2]** ...
3. **[P3]** ...

## 8. 스킬이 판단 못 한 것
- X 근거를 원본에서 못 찾음 — 도메인 전문가 확인 필요
- Y 는 문서화 안 됐지만 존재 가능 — 코드 직접 확인 권장
```

해당 없는 섹션은 **그 섹션 자체를 생략** (빈 헤더만 두지 말 것).

---

## 9단계: 원본 처리

`--archive-source` 없으면 건너뜀. 있고 사용자 승인이면 **하위 디렉터리 구조를 보존**하며 archive 로 이동 (같은 파일명 충돌 방지):

```bash
TODAY=$(date +%Y-%m-%d)
mkdir -p <path>/archive/$TODAY

# 각 .md 파일을 원본 상대 경로 그대로 archive 아래에 재현
find <path> -maxdepth 3 -name "*.md" \
  -not -path "*/bot/*" -not -path "*/human/*" -not -path "*/archive/*" \
  | while read f; do
      rel=${f#<path>/}
      dest=<path>/archive/$TODAY/$rel
      mkdir -p "$(dirname "$dest")"
      mv "$f" "$dest"
    done
```

이동 전 `find <path> -type d` 스냅샷 → `archive/$TODAY/_ORIGINAL_TREE.txt`.

---

## 10단계: 자체 검증 (다중 레이어)

### 10.1 구조 체크 (Bash)

```bash
# bot 파일 줄 수
for f in <path>/bot/*.md; do
  lines=$(wc -l < "$f")
  [ $lines -gt 200 ] && echo "[WARN] 200줄 초과: $(basename $f) ($lines 줄)"
done

# human README mermaid 유무
grep -c '```mermaid' <path>/human/README.md
# 0 이면 경고

# human/insights.md 존재 필수
[ -f <path>/human/insights.md ] || echo "[WARN] insights.md 누락"

# insights.md 의 확신/추정/가설 태그 존재 확인
grep -cE '\*\*\[(확신|추정|가설)\]\*\*' <path>/human/insights.md
# 0 이면 경고 (근거 표시 누락)

# 코드 레퍼런스 축약(`...`) 검출
grep -nE '\.\.\..*\.(java|html|js|json|ts|py|xml|yml)' <path>/bot/*.md
# 매치 있으면 경고

# 코드 레퍼런스 유효성 샘플 5개
grep -rhEo '[A-Za-z0-9/._-]+\.(java|html|js|json):[0-9]+' <path>/bot/*.md \
  | sort -u | head -5

# bot ↔ human 표 중복
for bf in <path>/bot/*.md; do
  header=$(grep -m1 -E '^\| [^|]+ \| [^|]+ \|' "$bf" | head -c 60)
  [ -z "$header" ] && continue
  grep -l -F "$header" <path>/human/*.md 2>/dev/null \
    && echo "[WARN] $(basename $bf) 표가 human 에 등장"
done
```

### 10.2 LLM 자기 검증 재읽기 (CLAUDE.md "산출물 자기 검증" 원칙, **강제 체크포인트**)

AskUserQuestion 으로 체크포인트 강제:

```
AskUserQuestion:
  question: "산출물 재읽기 완료. 다음 중 문제 발견되셨습니까?"
  options:
    - "없음 (리포트 진행)"
    - "bot 내 누락·중복 발견"
    - "human 내 다이어그램·설명 부족"
    - "insights.md 의 근거 출처 부족"
    - "코드 레퍼런스 불일치"
    - "기타 (자유 서술)"
```

"없음" 아니면 **해당 파일만 추가 수정 후 한 번 더 재읽기**. 전체 재작성 금지 (무한 루프 방지).

재읽기 대상:
- [ ] `bot/INDEX.md` 라우팅 테이블이 실제 파일만 가리키는가
- [ ] 각 bot 파일 자기 주제 집중 (혼합 금지)
- [ ] 원본 핵심 다이어그램이 `human/architecture.md` 에 이식됐는가
- [ ] `human/README.md` 3단 구조 완전
- [ ] **`human/insights.md` 각 항목에 [확신/추정/가설] 태그 + 근거 출처**
- [ ] 원본 결정적 사실이 bot 에 빠짐없이 보존

---

## 11단계: 소스 맵 생성

`<path>/.dualize/source-map.json` 자동 생성:

```json
{
  "generated-at": "2026-04-17T15:30:00Z",
  "source-files": [
    {"path": "STATUS.md", "lines": 183, "bytes": 9835},
    {"path": "ANALYSIS.md", "lines": 908, "bytes": 56297},
    ...
  ],
  "bot-files": {
    "decisions-timeline.md": {
      "source-files": ["ANALYSIS.md", "ARCHITECTURE.md", "meetings/2026-04-15-뷰어-데이터바인딩.md"],
      "lines": 56
    },
    ...
  },
  "human-files": {
    "README.md": {"mermaid-count": 1, "lines": 66},
    "architecture.md": {"mermaid-count": 3, "lines": 163},
    "insights.md": {"confidence-tags": {"확신": N, "추정": N, "가설": N}, "lines": Z},
    ...
  }
}
```

목적:
- 재실행 시 변경된 원본이 어느 bot 파일에 영향을 주는지 역추적 — 다음 dualize-docs 실행이 자체 참조
- 외부 도구(garden 등)와 연계 가능성 — 현재 미연동, 미래 옵션

주의: `.dualize/` 는 gitignore 후보. 사용자에게 "커밋할지 결정" 안내만.

---

## 12단계: 결과 리포트

```
[OK] dualize-docs 완료

대상: <path>
소스: N 파일 (X 줄)

→ bot/ : M 파일 (Y 줄)
  ...

→ human/ : K 파일 (Z 줄)
  - README.md (Z줄, mermaid N)
  - architecture.md (Z줄, mermaid N)
  - decisions.md (Z줄)
  - lessons.md (Z줄)
  - **insights.md (Z줄, 확신 N / 추정 N / 가설 N)**

→ .dualize/source-map.json 생성 — 재실행 시 변경 추적용

원본: {유지 | archive/YYYY-MM-DD/ 로 이동}

경고:
  - (경고 있으면 나열)

주요 제안: insights.md 가 제안한 P1 액션 N건 — 사용자 판단·반영 여부 결정

다음 단계:
  - 에이전트 작업 시: <path>/bot/INDEX.md 부터 (사용자 CLAUDE.md "문서 탐색 우선순위" 원칙)
  - 사람 리뷰 시: <path>/human/README.md → <path>/human/insights.md 순
  - 재실행: /dualize-docs <path>
```

---

## 주의 사항

- `.local.claude/`, `memory/`, `archive/` 자체가 인자면 경고 (광범위 파괴 위험)
- `.git/`, `node_modules/`, `target/` 경로 포함 시 사용자 확인
- 매 실행 git 변경 큼 → 실행 전 커밋 권장 안내
- `.html` 등은 수집 대상 아님. `.md` 만
- **insights.md 는 스킬의 판단이 섞인 문서** — 사용자가 채택 여부 결정. 스킬은 플래그만 세움

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경·규모]** 원본 파일 총합 60만줄+ (1M context 한계 접근)
- 신호: `wc -l` 합계 ≥ 600k 또는 토큰 추정치 임계치 초과
- 대응: 사용자 확인 후 파일·섹션 기준으로 분할 처리 + 각 파트 insights 생성 후 merge

**[데이터 결함]** 원본 문서 간 내용 모순 감지
- 신호: 동일 사실에 대해 서로 다른 값·결론 존재
- 대응: insights.md 에 `[모순]` 태그로 양쪽 명시 + 해결 필요 항목을 별도 섹션으로 분리
