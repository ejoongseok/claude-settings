---
name: skill-check
description: 모든 스킬을 CONTRACT.md 기준으로 자동 점검 — frontmatter 필수 필드, 본문 도메인 가정 박힘, 외부 데이터 의존 표, 분량 임계, 검증 시나리오 부재 검출. 신규 스킬 추가 시·정기 점검 시 호출.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
---

## 역할

`claude-config/CONTRACT.md` 기준으로 모든 스킬 (`skills/*/SKILL.md`) 을 점검하여 위반 항목을 P1/P2/P3 로 보고한다.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 계약 문서 | `claude-config/CONTRACT.md` 또는 `~/.claude/CONTRACT.md` | **필수** | "CONTRACT.md 부재 — 점검 불가. 먼저 작성 권장" 안내 후 종료 |
| 점검 대상 | `skills/*/SKILL.md` | **필수** | "점검 대상 스킬 없음" 안내 |

## 모드 판단

| 입력 | 모드 | 소요 |
|------|------|----|
| `/skill-check` (기본) | **전체 점검** — 모든 스킬 전수 검사 | ~5분 |
| `/skill-check {스킬명}` | **단건 점검** — 특정 스킬만 | ~1분 |
| `/skill-check --p1` | **P1 만** — frontmatter 위반 등 즉시 수정 필요 항목 | ~2분 |
| `/skill-check --new` | **신규 점검** — git status 기준 추가/변경된 스킬만 | ~2분 |

## 프로세스

### Phase 1: 사전 확인

1. `CONTRACT.md` 존재 확인 (claude-config/ 우선, 없으면 ~/.claude/)
2. 점검 대상 스킬 디렉터리 목록 수집:
   ```bash
   ls -d skills/*/ 2>/dev/null
   ```
3. 각 스킬의 SKILL.md 존재 확인

### Phase 2: 자동 점검 (스킬당)

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**:
> - Glob 병렬: `skills/*/SKILL.md`, `skills/*/templates/*`, `.local.claude/skill-check-domain-words.md`
> - Read 병렬: `CONTRACT.md`, 모든 `skills/*/SKILL.md` 를 한 번에 로드 (40~60개 스킬도 1M context 내)
> - Grep 병렬:
>   - frontmatter 필수 필드(`^name:`, `^description:`, `^allowed-tools:`, `^disable-model-invocation:`)
>   - 도메인 가정 키워드(B2B/SaaS·결제·의료 등 프로젝트 사전 등록 키워드)
>   - 구조 섹션(`## 외부 데이터 의존`, `## 검증 시나리오`, `다음 스킬 연결`)
>   - 코드 축약(`\.\.\./`)
>   - **H1 사용**(`^# ` 매칭 — frontmatter 닫힘 `^---$` 이후 첫 `#` 단일 발생)
>   - **Frontmatter 프롤로그 반복**(`생성하는 파일 상단에 아래 frontmatter를 포함한다`)
>   - **이모지 사용** — 유니코드 범위 `[\U0001F300-\U0001F9FF][\U00002600-\U000027BF]` 매칭
> 을 전체 스킬에 동시 수행.
>
> **검출 시 필수 예외 처리**:
> - **코드 블록·템플릿 내부 제외**: ` ``` ` 로 둘러싸인 블록 안의 `#` 은 마크다운 주석·bash 주석·산출물 템플릿 제목이므로 H1 검출에서 제외
> - **이모지 예외**: 유니코드 기호 `→ ← ↔ ★ ✓ ✗`, GitHub 체크박스 `- [ ]` / `- [x]`, 원본 인용(` > ` 인용 블록 내부) 은 §13 예외로 제외
> - **자기 참조 예외**: 이 파일(`skills/skill-check/SKILL.md`)은 검출 패턴 문자열을 **본문에 인용**하고 있으므로 §7-2·§13 검출 대상에서 자기 자신 제외. (CONTRACT.md 본체도 동일하게 검출 대상에서 제외)

각 SKILL.md 에 대해 다음 점검 수행:

#### P1 (즉시 수정 필요)

| 항목 | 검사 방법 | 위반 신호 |
|------|--------|---------|
| frontmatter 필수 필드 | `head -10` | name, description, allowed-tools, disable-model-invocation 누락 |
| 디렉터리명 ≠ name | 디렉터리명 vs `name:` 비교 | 불일치 |
| disable-model-invocation 누락 | grep `^disable-model-invocation` | 누락 시 자동 호출 위험 |

#### P2 (주의 — 구조적 결손)

| 항목 | 검사 방법 | 위반 신호 |
|------|--------|---------|
| 본문 도메인 가정 박힘 | grep 도메인 키워드 | 프로젝트 자기 사전에 등록된 도메인 키워드 박힘 (예외: biz-rules·on-boarding·CONTRACT 자체 + 프로젝트 자기 사전 등록 스킬) |
| 외부 데이터 의존 표 부재 | grep "## 외부 데이터 의존" 또는 유사 표 | 표 부재 |
| 다른 스킬과의 경계 명시 부재 | grep "다른 스킬과의 경계" 또는 영역 표 | 표 부재 (인접 스킬 있는 경우만) |

#### P3 (개선 권장)

| 항목 | 검사 방법 | 위반 신호 |
|------|--------|---------|
| 검증 시나리오 부재 | grep "## 검증 시나리오" | 부재 |
| 분량 임계 명시 부재 | grep "분량 임계" | 부재 (산출물 누적형 스킬만) |
| 다음 스킬 연결 부재 | grep "다음 스킬 연결" | 부재 |
| 코드 레퍼런스 축약 | grep `\.\.\./` | `...` 사용 (완전 경로 권장) |
| 본문 ≥600줄 | wc -l | 분리 검토 권장 |
| **본문 H1 사용** (CONTRACT §2) | frontmatter 닫힘 `^---$` 이후 `^# ` 매칭 | H1 검출 — frontmatter `name` 과 중복 |
| **Frontmatter yaml 블록 본문 반복** (CONTRACT §7-2) | grep `"생성하는 파일 상단에 아래 frontmatter를 포함한다"` | 문구 존재 — §7-2 참조 한 줄로 압축 권장 |
| **본문 이모지 사용** (CONTRACT §13) | 유니코드 이모지 범위 매칭 (예외: `→ ← ↔ ★ ✓ ✗`, GitHub 체크박스, 인용 원본) | 허용 예외 외 이모지 1개 이상 검출 |

### Phase 3: 보고

```markdown
## /skill-check 보고서 — YYYY-MM-DD

### 요약
| 등급 | 위반 수 | 영향 받는 스킬 |
|------|:------:|------------|
| P1 | N | [목록] |
| P2 | N | [목록] |
| P3 | N | [목록] |

### P1 (즉시 수정 필요)
| 스킬 | 위반 | 라인 | 권고 |
|------|------|:---:|------|
| {skill} | frontmatter `disable-model-invocation` 누락 | 5 | 한 줄 추가 |

### P2 (구조적 결손)
| 스킬 | 위반 | 위치 | 권고 |
|------|------|----|------|
| {스킬} | 본문에 도메인 사전 등록 키워드 박힘 | L75 | biz-rules.md 위임으로 |

### P3 (개선 권장)
| 스킬 | 위반 | 권고 |
|------|------|------|
| {skill} | 검증 시나리오 부재 | "## 검증 시나리오" 섹션 추가 |

### 통계
- 총 스킬: N
- 계약 100% 준수: N (X%)
- P1 발생: N (X%)
- 평균 위반/스킬: X.X
```

### Phase 4: 자동 수정 옵션 (선택)

P1 의 일부는 자동 수정 가능:
- `disable-model-invocation: true` 자동 추가 (사용자 승인 후)
- 디렉터리명 vs name 불일치 → 사용자에게 어느 쪽으로 통일할지 질문

P2·P3 는 자동 수정 안 함 — 본문 의미 변경 위험. 사용자가 확인 후 수동 정리.

## 도메인 가정 키워드 사전 (P2 검출 기준)

본문 grep 대상 키워드 (예외 처리 필요한 스킬: `biz-rules`, 자기 자신):

```
# 일반 B2B/SaaS 도메인 가정 (보편 기본)
멀티테넌트, 테넌트 키
승인 연동, 워크플로우
고객사, 고객 응대, 온콜, B2B
회사 PR 템플릿, 회사 이슈 템플릿, 회사 양식

# 특정 프레임워크·스택 단독 가정
특정 ORM·뷰·DB 접두사·프레임워크 단독 가정 (프로젝트별 사전에 등록)

# 프로젝트별 도메인 특화 키워드 (자기 사전)
# → `.local.claude/skill-check-domain-words.md` 에서 확장
#   예시 (도메인별로 자유 등록):
#     - 결제 도메인: 정산, 수수료, 환불 정책
#     - 의료 도메인: 차트, 수가
#     - 제조 도메인: 발주·수주·BOM 등
#     - 본인 프로젝트의 핵심 비즈니스 용어
```

매치 시 P2. 단 다음 패턴은 OK:
- "(예: ~)" 형태로 예시 표시
- "프로젝트의 X" / "{X}" placeholder
- 인용 (큰따옴표)
- 프로젝트 자기 사전(`.local.claude/skill-check-domain-words.md`)에 등록된 키워드는 자기 프로젝트 스킬 본문에서는 허용 (자기 도메인 스킬이므로)

## 출력 구조

`.local.claude/reports/YYYY-MM-DD-skill-check.md` 또는 `claude-config/.skill-check/YYYY-MM-DD.md`

```yaml
---
type: skill-check
date: YYYY-MM-DD
mode: full | single | p1 | new
contract-version: (CONTRACT.md 의 git hash 또는 mtime)
total-skills: N
violations:
  p1: N
  p2: N
  p3: N
---
```

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[의존성 부재]** CONTRACT.md 파일 자체가 부재
- 신호: `claude-config/CONTRACT.md` 및 `~/.claude/CONTRACT.md` 둘 다 없음
- 대응: 즉시 중단 + "CONTRACT.md 부재 — 작성 권장. 위치: claude-config/CONTRACT.md 또는 ~/.claude/CONTRACT.md" 안내

**[환경·규모]** 점검 대상 스킬이 100개 이상
- 신호: `ls -d skills/*/ | wc -l` ≥ 100
- 대응: Agent 분할(서브에이전트 병렬) 권장 모드로 전환 + 예상 소요 시간 미리 경고

## 다른 스킬과의 경계

| 질문 | 담당 |
|------|------|
| 스킬 작성·신규 추가 | 사용자 (CONTRACT.md 참조) |
| 스킬 위반 점검 | **/skill-check** (핵심) |
| 스킬 자동 수정 | /skill-check (P1 일부만) + 사용자 |
| 스킬 본문 일반화 (도메인 제거) | 사용자가 보고서 보고 수동 |

## 다음 스킬 연결

- P1 발생 → 즉시 본문 수정
- P2 다수 → 일괄 정리 시간 확보
- 위반 패턴 반복 → CONTRACT.md 강화 검토
- 신규 스킬 작성 후 → 항상 `/skill-check {새스킬명}` 호출

## 분량 임계

이 스킬 자체는 작음 (점검 로직만). 분리 불필요.

## 제약조건

- **CONTRACT.md 없으면 점검 불가.** 먼저 작성 권장 안내 후 종료
- **자동 수정은 P1 일부만.** P2/P3 은 본문 의미 변경 위험 — 사용자 확인 후 수동
- **도메인 키워드 사전은 보수적.** 예시·인용·placeholder 형태는 OK 로 처리
- **예외 스킬 명시** (biz-rules·on-boarding 등) — 도메인 키워드 박힘이 의도된 경우
- **점검 결과는 보고서로 저장.** 시간 경과에 따른 계약 준수율 추적 가능
