---
name: skills-guide
description: 사용 가능한 스킬 카탈로그 + 컨텍스트 기반 추천. "지금 어떤 스킬?", "스킬 목록", "오늘 회의록 정리하려는데" 같은 발견성 질문에 응답. 신규 사용자·다른 스킬 진입점 안내·시나리오별 그룹 보기.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash
---

## 역할

55개 스킬의 발견성 문제를 해결한다. 사용자가:
- "지금 컨텍스트에서 어떤 스킬 호출하면 좋을까?"
- "스킬 목록 보여줘"
- "신규 프로젝트 들어왔는데 뭐부터 해야 해?"
- "회고 관련 스킬 뭐 있지?"

질문할 때 **55개 카탈로그를 횡단 분석**하여 top 3~5 추천 + 시나리오별 그룹 안내.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 스킬 목록 | `skills/*/SKILL.md` | **필수** | "스킬 디렉터리 없음" 안내 |
| CONTRACT.md | `claude-config/CONTRACT.md` 또는 `~/.claude/CONTRACT.md` | 선택 | 카탈로그 모드만 동작, 검증 추천 생략 |
| 사용자 컨텍스트 | 현재 대화 + git status + 최근 산출물 | 선택 | 카탈로그·태그 필터만 동작 |

## 모드 판단

| 입력 | 모드 | 동작 |
|------|------|------|
| `/skills-guide` (기본) | **카탈로그** | 55개 전체 + 그룹별 보기 |
| `/skills-guide {자유 텍스트}` | **추천** | 컨텍스트 분석 → top 3~5 추천 |
| `/skills-guide --group {그룹명}` | **그룹 필터** | core / diagnosis / write / review / plan / data 등 |
| `/skills-guide --new` | **신규 프로젝트** | 첫 진입 추천 흐름 (/on-boarding → /setup-guide → ...) |
| `/skills-guide --search {키워드}` | **검색** | description grep |

## 카탈로그 (55개 — 그룹별)

> 최신 카탈로그는 호출 시점에 `ls skills/` + frontmatter description 추출로 자동 생성. 아래는 **현재 분류**.

### 1. 신규 프로젝트 진입
| 스킬 | 용도 | 첫 호출 권장 순서 |
|------|------|--------------|
| `/on-boarding` | 6산출물 자동 생성 (CLAUDE.md, bot/INDEX.md, human/README.md, biz-rules.md, team.md, SETUP.md) | 1 |
| `/setup-guide` | 환경 셋업 가이드 살아있는 문서로 유지 | 2 (수시) |
| `/skill-check` | 55개 계약 준수 점검 | 3 (월 1회) |
| `/skills-guide` | 이 스킬 — 카탈로그·추천 | 4 (수시) |

### 2. 진단 (관점별 정기 보고)
| 스킬 | 관점 | 활용 빈도 |
|------|------|--------|
| `/business-diagnosis` | 사업·경영 (돈·시간·사람) | 분기 |
| `/product-diagnosis` | 제품·고객 | 분기 |
| `/tech-diagnosis` | 기술·코드·인프라 | 분기 |
| `/delivery-diagnosis` | 전달·실행 (PM/PL 시각) | 월 |
| `/security-diagnosis` | 보안·컴플라이언스 | 분기·반기 |
| `/growth-diagnosis` | 성장·마케팅 | 분기 (성장 단계만) |
| `/data-diagnosis` | 데이터·메트릭 | 분기·반기 |

### 3. 작성·생성 (산출물)
| 스킬 | 산출물 |
|------|------|
| `/prd` | 제품 요구사항 문서 |
| `/srs` | 기술 요구사항 명세서 |
| `/todo` | Outside-In 개발 TODO |
| `/pr` | PR 제목·본문 |
| `/issue` | GitHub 이슈 |
| `/draft` | 메시지·보고서 초안 |
| `/adr` | 아키텍처 의사결정 기록 |
| `/poc` | PoC 계획·실행 |
| `/brainstorm` | 아이디어 발산 |
| `/rfc` | 기술/비기술 의사결정 RFC (복수안 비교→결정) |
| `/spec-demo` | 동작하는 명세 — 도메인 규칙을 인터랙티브 HTML로 정렬·합의 |
| `/html-explain` | 코드·문서를 인터랙티브 HTML로 설명·시각화 |

### 4. 리뷰·검증
| 스킬 | 용도 |
|------|------|
| `/review` | 자기 검토 (4관점) |
| `/team-review` | 팀원 코드 교육적 리뷰 |
| `/qa` | QA 체크리스트 작성 |
| `/qa-run-light` | QA 빠른 실행 |
| `/qa-run-deep` | QA 1M context 깊이 실행 |
| `/convention-audit` | 컨벤션 준수 감사 |
| `/deploy-checklist` | 배포 전 체크리스트 |
| `/pitfall` | 반복되는 함정·실수 패턴 점검·예방 |

### 5. 회고·학습
| 스킬 | 용도 |
|------|------|
| `/daily` | 데일리/주간/분기/성장 회고 |
| `/daily-todos` | 오늘 할 일 트래커 |
| `/learn` | 검증된 지식을 문서에 반영 |
| `/memo` | 검증 없이 일단 적기 |
| `/meeting-notes` | 회의록 구조화 |
| `/briefing` | 아침 브리핑 (최근 변경 요약) |
| `/session-handoff` | 세션 인계 문서 생성 (다음 세션·모델용) |
| `/session-glean` | 세션에서 지식·결정·할일 수확 |

### 6. 데이터·고객·팀 관리
| 스킬 | 용도 |
|------|------|
| `/biz-rules` | 비즈니스 규칙 단일 진실 원천 |
| `/customer-profile` | 고객사별 프로필 (B2B 시) |
| `/cs` | 고객 문의·장애 추적 (B2B 시) |
| `/people` | 동료·상사·팀원 프로필 |
| `/coaching` | 1on1·성장 가이드 |
| `/leadership` | 리더십 조언 |
| `/analyze-request` | 들어온 요청 해석 |

### 7. 정원·정리
| 스킬 | 용도 |
|------|------|
| `/garden` | .local.claude 정원 관리 + 분량 임계 검사 |
| `/absorb` | 외부 문서 흡수 + 지식 추출 |
| `/parse-doc` | 바이너리·외부 문서 파싱 |
| `/dualize-docs` | 사람용·AI용 문서 분리 |
| `/optimize-claude-md` | CLAUDE.md 최적화 (200줄 룰) |
| `/analyze-dir` | 디렉터리 구조 분석 |
| `/rewrite-external` | 외부 공유용 문서로 재작성 (민감정보 제거·저맥락화) |
| `/memory-garden` | 메모리(.claude/memory) 정원 관리 |

### 8. 메타 (스킬 시스템 자체)
| 스킬 | 용도 |
|------|------|
| `/skill-check` | CONTRACT.md 준수 자동 점검 |
| `/skill-modernize` | 모델 세대 전환 시 전 스킬 최신화 메타-스킬 |
| `/skills-guide` | 이 스킬 (카탈로그·추천) |

## 추천 모드 (자유 텍스트 → top 3~5)

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**하여 컨텍스트 효율화:
> - Glob: `skills/*/SKILL.md` — 전체 스킬 파일 경로 수집
> - Read 병렬: 모든 `skills/*/SKILL.md` (55개) 의 frontmatter + 상단 description/역할 섹션 동시 로드 — 1M context 내 충분
> - Bash: `git status --short`, 최근 `.local.claude/*` mtime 체크를 병렬로
> - Grep: 사용자 입력 키워드를 전체 스킬 description 에 동시 매칭

### 컨텍스트 신호 추출
1. 현재 대화 마지막 N 메시지 키워드
2. `git status` (변경 파일 패턴)
3. 최근 산출물 (`.local.claude/*` mtime 14일)
4. 현재 시각 (아침 → briefing, 저녁 → daily)

### 매핑 예시 (자유 텍스트 → 추천)

| 사용자 입력 패턴 | 추천 |
|--------------|------|
| "오늘 한 일 정리", "회고", "스탠드업" | `/daily`, `/daily-todos` |
| "회의록", "미팅 정리" | `/meeting-notes` |
| "PR 만들어", "PR 본문" | `/pr` |
| "이슈 작성" | `/issue` |
| "코드 리뷰", "내가 짠 거 봐줘" | `/review` |
| "팀원 코드 봐줘", "교육적으로" | `/team-review` |
| "배포 전 체크" | `/deploy-checklist` |
| "QA 체크리스트", "테스트 시나리오" | `/qa` |
| "고객한테 메시지", "보고 드릴 거" | `/draft` |
| "고객 문의 분석", "장애 신고" | `/cs` |
| "기능 기획", "PRD" | `/prd` |
| "기술 명세", "SRS" | `/srs` |
| "개발 TODO", "작업 분해" | `/todo` |
| "아이디어 정리", "발산" | `/brainstorm` |
| "PoC", "프로토타입" | `/poc` |
| "기술 부채 분석", "코드 건강도" | `/tech-diagnosis` |
| "고객 데이터 분석", "제품 방향" | `/product-diagnosis` |
| "런웨이", "재무 분석" | `/business-diagnosis` |
| "일정 자꾸 밀려", "WIP 관리" | `/delivery-diagnosis` |
| "보안 점검", "취약점" | `/security-diagnosis`, `/security-review` |
| "전환율", "리텐션" | `/growth-diagnosis` |
| "지표 정합성", "분석 인프라" | `/data-diagnosis` |
| "이거 알게 됐어", "검증해서 문서에" | `/learn` |
| "일단 적어둘 게" | `/memo` |
| "신규 프로젝트 진입" | `/on-boarding` 후 `/setup-guide` |
| "환경 셋업 점검", "새 dependency" | `/setup-guide` |
| "정원 정리", "오래된 문서" | `/garden` |
| "비즈니스 규칙 발견" | `/biz-rules` |

각 추천에 **호출 명령 + 1줄 이유** 제공.

## 신규 프로젝트 첫 진입 흐름 (`--new`)

```
1. /on-boarding              # 6산출물 자동 생성
   → CLAUDE.md, bot/INDEX.md, human/README.md, biz-rules.md, team.md, SETUP.md

2. /setup-guide              # SETUP.md 환경 점검
   → 빈 프로젝트 환경 vs 자동 추출 결과 일치 검증

3. /skill-check              # 55개 계약 준수 첫 점검
   → P1 0건 / P2 N건 / P3 N건 보고서

4. (작업하며 점진적으로)
   /biz-rules                # 도메인 규칙 발견 시 §4 채움
   /people                   # 동료 프로필 (팀 있을 때)
   /customer-profile         # 고객 프로필 (B2B 시)

5. (월 1회)
   /skill-check              # 계약 준수 재점검
   /garden                   # 문서 정원 + 분량 임계 검사

6. (분기 1회)
   /business-diagnosis
   /product-diagnosis
   /tech-diagnosis
   /delivery-diagnosis
```

## 출력 구조

### 카탈로그 모드
```markdown
## 사용 가능한 스킬 — 55개 (그룹별)

### 1. 신규 프로젝트 진입 (4개)
- `/on-boarding` — ...
...

### 핵심 권장 (가장 자주 호출)
- `/daily` (회고, 일 1회)
- `/pr` (PR 작성 시)
- `/review` (자기 검토)
- `/biz-rules` (도메인 규칙 발견 시)

### 사용 빈도 낮음 (필요 시만)
- /business-diagnosis, /growth-diagnosis 등 분기 단위
```

### 추천 모드
```markdown
## 추천 — "{사용자 입력}"

### Top 3
1. **`/{스킬명}`** — {1줄 이유}
   호출: `/{스킬명} {예상 인자}`

2. **`/{스킬명}`** — ...

3. **`/{스킬명}`** — ...

### 보강 (선택)
- 위 작업 후 → `/{다음 스킬}` 권장
```

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "어떤 스킬 있어?" | **이 스킬** | ✓ 핵심 |
| "스킬 위반 점검" | /skill-check | 다루지 않음 |
| "모델 세대 전환 전 스킬 최신화" | /skill-modernize | 다루지 않음 |
| "스킬 신규 작성" | 사용자 (CONTRACT.md 참조) | 다루지 않음 |
| "특정 스킬 실행" | 해당 스킬 직접 호출 | 다루지 않음 |

## 다음 스킬 연결

- 추천 결과 호출 후 산출물 생성 → 자연스러운 다음 스킬 안내 (각 스킬의 "다음 스킬 연결" 섹션)
- 신규 프로젝트면 `--new` 흐름
- 카탈로그가 변하면 (스킬 추가/삭제) → 본 스킬 카탈로그 섹션 자동 갱신 권장

## 분량 임계

이 스킬 자체는 카탈로그 + 추천 로직. 55개 → 70개+ 늘어나면 그룹별 sub-doc 분리 검토.

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[데이터 결함]** 스킬 디렉터리 이름과 frontmatter `name` 불일치
- 신호: `skills/foo/SKILL.md`의 frontmatter `name: bar`
- 대응: 불일치 스킬을 카탈로그·추천에서 제외 + 경고 표시 ("naming 불일치 — 수정 필요")

**[사용자 개입 필요]** 자유 텍스트 입력으로 추천 결과가 모호(점수 동률 등)
- 신호: top 후보 스코어 차이 < 임계치 또는 키워드 매칭 다의어
- 대응: AskUserQuestion 으로 범위·의도 확정(예: "코드 리뷰입니까, PR 본문 작성입니까?") 후 재추천

## 제약조건

- **카탈로그는 자동 생성.** `ls skills/` + frontmatter 추출로 만들고, 본문 정적 표는 fallback
- **추천은 top 5 이내.** 너무 많이 추천하면 발견성 회복 X
- **각 추천에 1줄 이유 필수.** "왜 이 스킬?" 답해야 사용자 결정 가능
- **신규 프로젝트 흐름은 순서 명확.** /on-boarding 먼저, 그 다음 /setup-guide, ...
- **자기 추천 금지.** 사용자가 `/skills-guide` 호출 후 응답에 다시 `/skills-guide` 추천 X
- **컨텍스트 부족 시 명시 질문.** "어떤 작업이신가요?" 형태 1개 질문
