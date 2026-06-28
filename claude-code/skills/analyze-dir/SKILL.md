---
name: analyze-dir
description: "현재 디렉터리의 내용을 분석하여 어떤 목적의 폴더인지 파악"
argument-hint: "[--save]"
disable-model-invocation: true
model: opus
effort: high
allowed-tools: Read, Grep, Glob, Write, Agent(structure-scanner), Agent(content-analyzer), Agent(relation-mapper), Bash(du *)
---

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | 일반 SW 관점으로만 진행 (Tier 1) |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 현재 디렉터리 구조 | `pwd` 의 실제 파일 | **필수** | 빈 디렉터리 안내 후 종료 |
| 서브에이전트 | structure-scanner, content-analyzer, relation-mapper | **필수** | 에이전트 미설치 시 메인에서 직접 Glob/Read 로 fallback |

## 옵션 해석

$ARGUMENTS를 확인하세요:

- `--save`가 있으면 -> 분석 결과를 현재 디렉터리에 ANALYSIS.md로 저장
- 인자가 없으면 -> 대화로만 보고

## 분석 프로세스

### 1단계: 구조 스캔 위임

structure-scanner 에이전트에게 다음을 요청하세요:
"현재 디렉터리의 구조를 스캔하고, 규모/파일 유형 분포/디렉터리 유형을 판별해서 요약해줘"

### 2단계: 상세 분석 위임

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**:
> - Agent 병렬: structure-scanner(1단계 완료 후), content-analyzer, relation-mapper 를 **단일 메시지 내에서 동시 호출**
> - 에이전트 미설치 fallback 시 Glob + Read 병렬: 디렉터리 트리 탐색, 주요 파일(README/package.json/pom.xml/index 진입점) Read, import/require/include grep 을 한 번에
> - Bash: `du -sh`, 파일 유형별 `find | wc -l` 병렬 실행

1단계 결과를 바탕으로 content-analyzer와 relation-mapper에게 동시에 위임하세요:

content-analyzer에게:
"현재 디렉터리는 [1단계에서 판별된 유형]이다. 주요 파일을 읽고 각 파일의 목적과 역할을 분석해줘"

relation-mapper에게:
"현재 디렉터리는 [1단계에서 판별된 유형]이다. 파일 간 참조, import, 의존 관계를 분석해줘"

### 3단계: 종합 보고

3개 에이전트의 결과를 종합하여 아래 형식으로 보고하세요.
에이전트 간 분석이 충돌하면, 실제 파일 내용을 근거로 판단하세요.
보고서에 에이전트 이름이나 위임 과정을 노출하지 마세요.

```
## 요약
[이 디렉터리가 무엇인지 1~2문장]

## 규모
- 파일 수: N개
- 디렉터리 수: N개
- 총 용량: XX MB
- 주요 파일 유형: [확장자별]

## 구조
[디렉터리 트리 + 각 폴더/파일의 역할]

## 주요 파일
| 파일 | 역할 | 비고 |
|------|------|------|

## 파일 간 관계
[참조, 의존, 흐름 관계 설명]

## 개선 제안 (해당 시)
[구조적 개선이나 빠진 요소가 있으면 제안]
```

`--save`가 지정된 경우에만 이 내용을 ANALYSIS.md로 저장하세요.
저장 실패 시 (권한 부족 등) 오류를 보고하고, 대화로 결과를 출력하세요.
`--save`가 없으면 대화로만 보고하세요.

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬 |
|---|---|---|
| 받은 업무 요청 메시지(슬랙·메일) 분석·판정 | `/analyze-request` | [다루지 않음] |
| CLAUDE.md·메모리 설정 진단·최적화 | `/optimize-claude-md` | [다루지 않음] |
| 임의 디렉터리의 목적·구조·파일 관계 분석 | 이 스킬 | [핵심] |

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[환경·규모]** 분석 대상 파일 10만 개 이상
- 신호: `find . -type f | wc -l` ≥ 100k
- 대응: structure-scanner 만 먼저 수행해 규모·분포 파악 후, 규모별 분석 전략(샘플링·구역화) 결정

**[의존성 부재]** 서브에이전트 3종(structure-scanner / content-analyzer / relation-mapper) 미설치
- 신호: `.claude/agents/` 내 해당 에이전트 파일 부재
- 대응: 메인 세션에서 Glob + Read 로 순차 fallback 수행 + 시간 경고 표시
