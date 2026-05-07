---
name: pitfall
description: "현재 세션의 시행착오를 시도·실패·원인·해결·재방문 신호 5요소로 캡처합니다. 보편 교훈은 메모리에, 프로젝트 특수는 문서에 저장합니다. 동일 함정 재방문 차단을 위해 시행착오 인지 후 어느 시점에든 호출하세요(시점 무관)."
argument-hint: "[--target doc|mem|both] [--note <message>]"
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Glob, Grep, AskUserQuestion, Bash(ls*), Bash(stat*), Bash(wc*)
effort: high
---

## 역할

현재 세션의 시행착오를 5요소로 캡처해 메모리 또는 문서에 저장. 동일 함정 재방문 차단.

톤: 추출은 분석적, 사용자 안내문은 존댓말, 산출 본문은 평서체.

## 핵심 원칙

- 입력은 현재 세션 중 가장 최근 시행착오 1건 (호출 시점은 무관, 다건 흡수는 `/session-glean`)
- 5요소 누락 시 추출 보류 (불완전 기록 금지)
- 매체 판단: 보편 교훈 → 메모리, 프로젝트 특수 → 문서, 양쪽 해당 → 둘 다
- 동일 시행착오 사전 검사 (Grep) 후 SKIP
- 모든 변경에 `(출처: 세션 §N)` 표기

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|---|---|:---:|---|
| 현재 세션 | (대화 내) | 필수 | 시행착오 0건 시 종료 |
| auto memory 디렉터리 | 시스템 자동 명시 경로 | 선택 | 문서 모드로 fallback |
| 메모리 인덱스 | `MEMORY.md` | 선택 | 신규 생성 |
| 프로젝트 문서 sink | `.local.claude/learn/`, `.local.claude/modules/{name}.md`, `docs/pitfalls.md` | 선택 | 신규 위치 추천 |
| 기존 시행착오 기록 | `.local.claude/learn/*pitfall*.md`, `docs/pitfalls.md`, `MEMORY.md` 의 feedback 항목 | 선택 | Grep 검사만 수행 |

## 프로젝트 컨텍스트

호출 전 자동 read: `CLAUDE.md`, `MEMORY.md` (있으면), 기존 시행착오 기록 (중복 방지).

## 입력 처리

| 입력 | 동작 |
|---|---|
| (빈) | 현재 세션 중 가장 최근 시행착오 자동 추출 + 매체 자동 판단 |
| `--target doc` | 문서만 |
| `--target mem` | 메모리만 |
| `--target both` | 양쪽 강제 |
| `--note "{텍스트}"` | 사용자 명시 시행착오 (자동 추출 대체) |

## 프로세스

### Phase 1: 추출

현재 세션에서 시행착오 5요소 추출:

| 요소 | 정의 | 예시 |
|---|---|---|
| 시도(Tried) | 무엇을 시도했는가 | "X 라이브러리 Y API 사용" |
| 실패(Failed) | 어떤 실패가 발생했는가 | "Z 에러로 N분 지연" |
| 원인(Cause) | 진짜 원인 | "Y API는 W 조건에서 미동작" |
| 해결(Fix) | 어떻게 해결·회피했는가 | "V 함수로 우회" |
| 재방문 신호(Trigger) | 다시 만났을 때 인식 키워드 | "Z 에러 + Y API" |

5요소 누락 시 → AskUserQuestion으로 부족 요소 질문. 답변 못 받으면 추출 보류.

`--note` 입력 시: 사용자 텍스트를 5요소로 구조화. 부족 요소만 추출로 보충.

조기 종료: 현재 세션에 시행착오 식별 불가 → "추출할 시행착오가 없습니다" 안내 후 종료.

### Phase 2: 매체 판단 + 승인

매체 자동 판단 휴리스틱:

| 시행착오 성격 | 매체 |
|---|---|
| 외부 도구·라이브러리·언어 기능 (보편) | 메모리 (feedback type) |
| 이 모듈·이 코드베이스·이 데이터 (프로젝트 특수) | 문서 |
| 양쪽 해당 | 둘 다 (각 매체에 맞는 표현) |

`--target` 인자 명시 시 자동 판단 생략하고 강제.

저장 위치 결정:

- 메모리: auto memory 시스템 — feedback type 또는 project type
- 문서:
  - `.local.claude/learn/` 존재 → `.local.claude/learn/{YYYY-MM-DD}-pitfall.md`
  - 모듈 특화 → `.local.claude/modules/{name}.md` 의 "함정" 섹션 추가
  - 그 외 → `docs/pitfalls.md` (부재 시 신규)

동일 시행착오 사전 검사:

1. Grep으로 재방문 신호·키워드 검색 (위 sink 후보 전체)
2. 발견 시 SKIP + 위치 안내 ("이미 기록됨: {파일}:{줄}"), 신규 저장 안 함

AskUserQuestion으로 매체·위치 승인 후 Phase 3 진입.

### Phase 3: 적용 + 보고

처리 순서:

1. 메모리 저장 (해당 시):
   - type 결정: 보편 → feedback / 프로젝트 특수 → project
   - auto memory 시스템 frontmatter (`name`, `description`, `type`) + 5요소 본문
   - `MEMORY.md` 인덱스에 한 줄 추가: `- [{title}]({file}.md) — {재방문 신호}`
2. 문서 저장 (해당 시):
   - 기존 파일 → Edit (5요소 표 추가)
   - 신규 파일 → Write (CONTRACT §7-2 frontmatter + 5요소 표 + 첫 줄 `> /pitfall 으로 생성 — YYYY-MM-DD`)
3. 보고:
   - 저장 위치 표 (매체·경로·5요소 요약)
   - 재방문 시 검색 키워드 명시

## 출력 구조 / 산출물

- 메모리 파일: auto memory 시스템 frontmatter + 5요소 본문 + 출처
- 문서 파일: CONTRACT §7-2 frontmatter + 5요소 표 + 첫 줄 `> /pitfall 으로 생성 — YYYY-MM-DD`
- 기존 갱신: 해당 sink의 "함정" 섹션에 5요소 표 한 줄 추가
- 보고: 대화 텍스트, 미저장

5요소 표 형식:

```
| 시도 | 실패 | 원인 | 해결 | 재방문 신호 | 출처 |
```

## 저장 경로

매체별 결정 규칙:

- 메모리: auto memory 시스템 (시스템 자동 명시 경로)
- 문서: Phase 2 위치 결정 규칙

## 분량 임계

CONTRACT §5 전수 준수.

| sink | 임계1 | 임계2 | 안내 |
|---|:---:|:---:|---|
| 메모리 개별 파일 | 50 | 100 | 분리 또는 요약 |
| `MEMORY.md` (자동 로드) | 200 | — | `/memory-garden` |
| `docs/pitfalls.md` | 300 | 500 | 카테고리·시기별 분리 |
| `.local.claude/learn/*pitfall*.md` | 200 | 300 | 시기별 분리 |
| `.local.claude/modules/*.md` | 300 | 500 | sub-doc 분리 |

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬 |
|---|---|---|
| 세션 전체 다건 학습 흡수 | `/session-glean` | [다루지 않음] |
| 메모리 인덱스 정리·아카이브 | `/memory-garden` | [다루지 않음] |
| 외부 디렉터리 흡수 | `/absorb` | [다루지 않음] |
| 단건 코드 검증 | `/learn` | [다루지 않음] |
| 만료 문서 정리 | `/garden` | [다루지 않음] |
| 현재 세션 중 단건 시행착오 캡처 | 이 스킬 | [핵심] |

## 다음 스킬 연결

- 시행착오 3건+ 발견 → `/session-glean`
- `MEMORY.md` 200줄 근접 → `/memory-garden`
- 코드 레벨 검증 필요 → `/learn`
- 데이터 부재 (CLAUDE.md·메모리 모두 없음) → `/on-boarding`

## 제약조건

- 단건 처리 (3건+은 `/session-glean` 안내)
- 5요소 누락 시 추출 보류
- 동일 시행착오 SKIP (사전 Grep 검사)
- 매체 판단 + 사용자 승인 필수
- 시크릿·PII 마스킹
- 출처 추적: 모든 변경에 `(출처: 세션 §N)`
- 부분 승인 시 미반영 항목 보고 명시
- 멱등성: Phase 2 SKIP 검사로 보장

## 검증 시나리오

공통 3블록은 CONTRACT §6-1 참조.

### 이 스킬의 고유 실패 시나리오

[환경·규모] 시행착오 3건+ 발견
- 신호: Phase 1 추출 가능 시행착오 ≥ 3
- 대응: `/session-glean` 안내 + 가장 최근 1건만 처리

[데이터 결함] 5요소 부분 누락
- 신호: 시도·실패·원인·해결·재방문 신호 중 일부 추출 불가
- 대응: AskUser로 부족 요소 질문, 답변 미수신 시 추출 보류

[데이터 결함] 동일 시행착오 이미 기록
- 신호: Phase 2 Grep 결과 기존 sink에 동일 재방문 신호 발견
- 대응: SKIP + 위치 안내 (`이미 기록됨: {파일}:{줄}`), 신규 저장 안 함

[의존성 부재] auto memory 디렉터리 미존재
- 신호: 시스템 메모리 경로 부재
- 대응: 디렉터리 생성 안내 후 사용자 승인, 또는 `--target doc` 자동 전환
