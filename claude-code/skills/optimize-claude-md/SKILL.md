---
name: optimize-claude-md
description: "CLAUDE.md와 메모리 설정을 진단하고 개선합니다. CLAUDE.md 점검, 반복 지시 해소, 설정 최적화 요청 시 사용하세요."
argument-hint: "[문제 설명 또는 공백]"
allowed-tools: Read, Edit, Write, Agent
effort: high
disable-model-invocation: true
---

CLAUDE.md 및 관련 메모리 설정을 종합 분석하여 개선안을 제시하고, 승인 후 적용합니다.
CLAUDE.md로 해결할 수 없는 문제는 적합한 대안(Hook, Skill, 서브에이전트, .claude/rules/)을 설명과 예시로 제안합니다.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 SW 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | Tier 1(도메인 무관) 점검만 수행 |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 대상 파일 | `CLAUDE.md` (프로젝트 또는 `~/.claude/`) | **필수** | "대상 파일 부재" 안내 후 종료 |
| 서브에이전트 | `claude-md-analyzer` | **필수** | 에이전트 미설치 시 메인에서 직접 분석 fallback |
| 메모리·훅·규칙 | `~/.claude/memory/`, `settings.json` hooks, `rules/` | 선택 | 재배치 후보 그룹 B/C 중 Hook/Memory 옵션 제외 |

## 동작 모드

$ARGUMENTS 유무에 따라 모드를 선택하세요:

- $ARGUMENTS가 비어 있음 → 전체 분석 모드
- $ARGUMENTS에 문제 설명이 있음 → 집중 분석 모드 (해당 문제 해결에 초점)

## 1단계: 수집 및 진단 위임

> **[Opus 4.7 / 1M 활용]** 서브에이전트가 부재하거나 메인에서 직접 분석 fallback 하는 경우 **다중 파일 동시 Read** 후 교차 분석:
> - 로드: 프로젝트 `CLAUDE.md`, `~/.claude/CLAUDE.md`, `~/.claude/memory/**/*.md`, `~/.claude/settings.json`, `~/.claude/settings.local.json`, `.claude/rules/**/*.md`, `~/.claude/rules/**/*.md`, `.claude/settings.json`, `.claude/settings.local.json`, `.mcp.json`, auto memory
> - 교차 분석: {CLAUDE.md 규칙} vs {hooks} vs {rules/ 정책} — 중복 지시, 모순, Hook 으로 옮겨야 할 규칙, rules/ 로 분리할 도메인 지식 식별
> - 200줄 초과 시 어떤 부분이 (a) 자명한 지시 (b) 도메인 지식 (c) Hook 대상 (d) rules/ 대상 인지 한 번에 분류 가능
> - 한계: 총 로드량이 600K줄 초과 시 CLAUDE.md + 최근 변경 memory/ 만 우선 로드.

claude-md-analyzer 서브에이전트에게 분석을 위임하세요.
위임할 때 아래 정보를 전달하세요:
- 분석 모드 (전체 또는 집중)
- 집중 모드인 경우 사용자의 문제 설명: $ARGUMENTS

서브에이전트의 분석 보고서를 수신할 때까지 대기하세요.

## 2단계: 개선안 작성

서브에이전트가 보고한 진단 결과를 바탕으로, 발견한 문제를 아래 세 그룹으로 분류하여 개선안을 작성하세요.

### 그룹 A: 메모리 파일 수정으로 해결 가능 (CLAUDE.md, .claude/rules/, ~/.claude/rules/)
각 항목에 대해:
- 대상 파일: 경로
- 현재 내용 (인용)
- 문제점
- 수정안 (구체적 텍스트)
- 수정 이유

### 그룹 B: 메모리 파일 재배치로 해결 가능
각 항목에 대해:
- 현재 위치와 내용
- 이동할 위치
- 이동 이유

### 그룹 C: CLAUDE.md로 해결할 수 없음 - 다른 확장 수단 필요
각 항목에 대해:
- 문제 설명
- CLAUDE.md로 안 되는 이유 (예: "CLAUDE.md는 LLM 판단에 의존하므로 100% 실행을 보장하지 못합니다")
- 권장 확장 수단 (Hook / Skill / 서브에이전트 / .claude/rules/ 중)
- 확장 수단의 동작 방식 설명
- 설정 예시 (코드 블록)

확장 수단 선택 기준:
- "매번 빠짐없이 실행되어야 하는 동작" → Hook
- "판단이 필요한 반복 작업" → Skill
- "컨텍스트를 분리해야 하는 탐색/분석" → 서브에이전트
- "특정 파일 경로에만 적용되는 규칙" → .claude/rules/ (paths frontmatter)

## 3단계: 제시 및 승인

아래 형식으로 분석 결과를 사용자에게 보고하세요.

---

## 분석 결과

### 수집한 파일
[파일 목록과 각 줄 수]

### 그룹 A: 메모리 파일 수정 (N건)
[각 항목의 대상 파일, 현재 → 수정안]

### 그룹 B: 재배치 (N건)
[각 항목의 현재 위치 → 이동 위치]

### 그룹 C: 다른 확장 수단 권장 (N건)
[각 항목의 문제, 권장 수단, 예시]

---

보고 후 사용자에게 다음을 물으세요:
- "그룹 A, B의 변경 사항을 적용할까요? 특정 항목만 선택할 수도 있습니다."

## 4단계: 적용

사용자가 승인한 항목만 적용하세요.
- 기존 파일 수정은 Edit 도구를 사용하세요.
- 새 파일 생성은 Write 도구를 사용하세요.
- 적용 전에 대상 파일을 Read로 한 번 더 읽어 최신 상태를 확인하세요.
- 각 변경 후 해당 파일의 줄 수를 확인하여 200줄 이내인지 검증하세요.
- 모든 적용이 끝나면 변경 요약을 보고하세요.

## 주의사항

- CLAUDE.md를 절대 200줄 넘게 만들지 마세요. 넘칠 경우 @import나 .claude/rules/로 분리하세요.
- "깔끔한 코드 작성", "베스트 프랙티스 따르기" 같은 자명한 지시는 추가하지 마세요.
- auto memory(MEMORY.md)는 읽기만 하고 직접 수정하지 마세요. 충돌이 있으면 CLAUDE.md 쪽을 조정하세요.
- 그룹 C의 확장 수단은 설명과 예시만 제공하세요. 파일을 직접 생성하지 마세요.

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[의존성 부재]** claude-md-analyzer 서브에이전트 부재
- 신호: `.claude/agents/claude-md-analyzer*` 미존재 또는 호출 실패
- 대응: 메인 세션에서 직접 분석 fallback 수행 + 단일 패스 경고 표시

**[사용자 개입 필요]** 200줄 초과 원인이 도메인 지식(biz-rules·용어·프로세스)일 때
- 신호: 분류 결과 "도메인 지식" 비중이 임계치 이상
- 대응: 자동 삭제 금지, 사용자에게 `biz-rules.md` 등 별도 파일로 이동 여부 확인 후 진행
