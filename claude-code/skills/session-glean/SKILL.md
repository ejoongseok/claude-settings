---
name: session-glean
description: "현재 세션에서 발견한 새 지식, 결정, 교훈을 작업 디렉터리 문서에 반영합니다. 관련 문서가 있으면 갱신하고, 없으면 적합한 위치에 신규 문서를 생성합니다. 세션 중간이나 말미에 호출하여 학습을 휘발시키지 않고 문서 자산으로 보존하세요."
argument-hint: "[path] [--scope auto|cwd|local-claude] [--dry-run]"
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Glob, Grep, AskUserQuestion, Bash(git status*), Bash(git diff*), Bash(git log*), Bash(ls*), Bash(stat*), Bash(wc*), Bash(find *), Bash(mkdir *)
effort: high
---

## 역할

세션 대화에서 추출한 영속 학습을 작업 디렉터리 문서에 증분 반영. 매칭 sink 있으면 갱신, 없으면 신규 생성.

톤: 추출은 분석적, 사용자 안내문은 존댓말, 산출 문서 본문은 평서체.

## 핵심 원칙

- 입력은 세션 컨텍스트만 (외부 디렉터리 흡수는 `/absorb`)
- 영속 학습만 (So What 필터: 6개월 후 새 팀원에게 유효한가)
- 모든 변경에 `(출처: 세션 N절)` 표기
- CONFLICT 자동 해결 금지
- 신규 파일은 매칭 부재 + 사용자 승인 시
- 분량 임계 사전 검사, 강제 분리 안 함

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|---|---|:---:|---|
| 세션 컨텍스트 | (대화 내) | 필수 | 영속 학습 0건 시 종료 |
| 프로젝트 규칙 | `CLAUDE.md` | 선택 | 일반 SW 가정 + `[프로젝트 규칙 미확인]` |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | Glob fallback |
| 도메인 sink | `.local.claude/biz-rules.md`, `.local.claude/{modules,customers,people,adr}/*.md`, `.local.claude/team.md`, `.local.claude/INFRASTRUCTURE.md`, `.local.claude/{be-guide,fe-guide}/*.md` | 선택 | cwd 모드 자동 전환 |
| absorb 흡수 이력 | `.local.claude/docs/absorb-log.md` | 선택 | Grep 사전 검사만 |

## 프로젝트 컨텍스트

호출 전 자동 read: `CLAUDE.md`, `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md`, `.local.claude/docs/absorb-log.md`. 모두 부재 시 `/on-boarding` 안내 후 종료.

## 모드 판단

| `--scope` | 동작 |
|---|---|
| `auto` (기본) | `.local.claude/` 존재 시 `local-claude`, 부재 시 `cwd` |
| `cwd` | working directory만 |
| `local-claude` | `.local.claude/` 강제 (부재 시 종료) |

판단: `Glob` 으로 `.local.claude/` 존재 확인.

## 입력 처리

| 입력 | 동작 |
|---|---|
| (빈) | working directory + `auto` |
| `{경로}` | sink 후보 한정 |
| `--scope X` | 모드 강제 |
| `--dry-run` | Phase 5 미실행 |

존재하지 않는 경로면 종료. 파일 지정 시 그 파일만 sink. 디렉터리 지정 시 하위만 스캔.

## 프로세스

### Phase 1: 추출

1. 인자와 `--scope` 확정
2. 6개 카테고리로 추출:

| 유형 | 정의 | 예시 |
|---|---|---|
| 사실(Fact) | 검증 가능한 구체 정보 | "X 라이브러리 Y 버전부터 Z 동작" |
| 결정(Decision) | 합의되거나 지시된 방향 | "이 모듈은 A 패턴으로 통일" |
| 규칙(Rule) | 반복 적용 규칙 | "PR 시 체크리스트 N 항목 필수" |
| 관계(Relation) | 엔티티 간 연결 | "C 모듈이 D 테이블에 의존" |
| 타임라인(Timeline) | 시간 순서 이벤트 | "YYYY-MM-DD E 마이그레이션 완료" |
| 인사이트(Insight) | 패턴, 교훈 | "F 작업은 G 방식이 더 안전" |

3. 각 항목에 `claim`(한 줄), `근거`(세션 위치), `영속성 판단`

4. So What 필터:

| 통과 | 폐기 |
|---|---|
| 반복 적용 규칙과 정책 | 일회성 작업 현황 |
| 구조적 변경 | 단순 질의응답 |
| 결정 + 근거 | 코드나 git에 이미 기록 |
| 상태 전이, 인원 변동, 마일스톤, 고객사 특성 | 개인 감상, 일정 조율 |

5. 영속 항목 0개면 "영속 학습 추출 안 됨" 안내 후 종료. 빈 보고서 미생성.

### Phase 2: 탐지

> Glob, Bash, Read 단일 메시지 병렬 호출

`local-claude` 모드 sink:

- `CLAUDE.md`, `bot/INDEX.md`, `bot/*.md`
- `.local.claude/{biz-rules,biz-rules-detail,team,INFRASTRUCTURE}.md`
- `.local.claude/{modules,customers,people,adr}/*.md`
- `.local.claude/{be-guide,fe-guide}/*.md`

`cwd` 모드 sink:

- `CLAUDE.md`, `bot/INDEX.md`, `bot/*.md`
- `README.md`, `human/README.md`, `human/*.md`
- `docs/**/*.md`, 최상위 `*.md`

우선순위 (높은 순): `bot/INDEX.md` > `bot/*.md` > `CLAUDE.md` > `docs/` > `human/README.md` > `README.md` > 기타.

병렬 도구:

- Glob: 위 패턴 동시
- Bash: `git status --short`, `git log --oneline -10`, `stat`, `wc -l`
- Read: 우선순위 상위 5~7 사전 적재

컷오프:

- 후보 12+면 상위 12 + "추가 N개" 안내
- 후보 0이면 Phase 3 신규 위치 결정
- `archive`, `node_modules`, `.git` 제외

### Phase 3: 매칭

> 후보 Read + Grep 단일 메시지 병렬

분류:

| 매칭 | 분류 |
|---|---|
| 단일 sink + 동일 기재 | SKIP |
| 단일 sink + 보강 | ENRICH |
| 단일 sink + 갱신 | UPDATE |
| 단일 sink + 모순 | CONFLICT |
| 매칭 부재 | NEW (기존 문서) 또는 CREATE_FILE (신규) |
| 다중 sink | 단일 sink + 다른 곳은 anchor 참조 |

사전 검사:

1. SKIP: Grep으로 동일하거나 유사한 표현 검사
2. CONFLICT: 기존 sink 모순
3. 분량 임계: 변경 후 줄 수 추정 (CONTRACT 5절 표)

신규 파일 위치:

- `bot/` 존재 시 `bot/{topic}.md`
- `docs/` 존재 시 `docs/{topic}.md`
- 둘 다 부재면 `docs/` 신규 생성 후 `docs/{topic}.md`
- `local-claude` 모드면 `.local.claude/{modules,customers,...}/`

신규 파일 생성 임계: 동일 주제로 추출 항목 3건 이상이거나 구조화 가능한 분량일 때만. 단건 사실 1건으로 신규 파일 생성 금지 (`/absorb` 정책 차용).

각 초안 구조: `target_file`, `action`, `summary`, `diff_preview`, `provenance`, `threshold_warning`.

### Phase 4: 승인

후보 표:

```
| # | 대상 | 작업 | 요지 | 출처 | 분량 알림 |
```

AskUserQuestion 분할:

| 후보 수 | 패턴 |
|:---:|---|
| 1~3 | 단일 질문 다중 옵션 |
| 4~8 | "전체/선택/취소" 1차 후 후보별 2차 |
| 9+ | 상위 5 1차 + 나머지 일괄 (호출 4회 이내) |

후보별 옵션: 적용 / 스킵 / 수정 요청 / 통째 보기.

CONFLICT 별도:

```
| 항목 | 기존 | 새 정보 | 출처 |
```

옵션: 기존 유지 / 새로 교체 / 양쪽 보존(`[충돌]` 태그).

신규 파일 별도: 위치, 이름, 사유, 골격 미리보기 + 분량 임계 결과.

`--dry-run`이면 Phase 5 미실행.

### Phase 5: 적용

1. 사전: `git status --short` (git 시) / mtime 기록 (비-git)
2. 처리 순서: CONFLICT, UPDATE, ENRICH, NEW, CREATE_FILE 순
3. Edit는 한 문서, 한 섹션 단위
4. 신규 파일 frontmatter (CONTRACT 7-2절 참조): `category: {topic}, retention: {sink 도메인 기본값}, harvest_targets: [...]`. 첫 줄 `> /session-glean 으로 생성 (YYYY-MM-DD)`
5. 사후: `git diff --stat` (git) / 변경 파일 + mtime (비-git)
6. 보고:

```
| 대상 | 작업 | 변경 줄 수 | 요지 | 출처 |
```

후속 제안: 임계 근접, 외부 흡수 필요, 만료 정리 시점.

## 출력 구조 / 산출물

- Phase 4 보고: 대화 텍스트, 미저장
- 신규 파일: CONTRACT 7-2절 frontmatter + 첫 줄 `> /session-glean 으로 생성 (YYYY-MM-DD)`
- 기존 갱신: 변경 이력 테이블 있으면 `| YYYY-MM-DD | session-glean: {요약} | 세션 N절 |` 추가

## 저장 경로

신규 산출물: Phase 3 위치 결정 규칙. 보고서: 미저장.

## 분량 임계

CONTRACT 5절 전수 준수. Phase 3 사전 측정.

| sink | 임계1 | 임계2 | 안내 |
|---|:---:|:---:|---|
| `CLAUDE.md` (자동 로드) | 200 | 없음 | `/optimize-claude-md` |
| `bot/*.md` | 150 | 없음 | `/dualize-docs` 또는 `/on-boarding --refresh` |
| `.local.claude/biz-rules.md` | 200 | 400 | `biz-rules-detail.md` 분리 |
| `.local.claude/customers/*.md` | 300 | 500 | 디렉터리 분리 |
| `.local.claude/modules/*.md` | 300 | 500 | sub-doc 분리 |
| `human/SETUP.md` | 300 | 500 | `/setup-guide` |
| 보고서 | 300 | 없음 | 후보 컷오프 |

임계 초과 시 보고서 "분량 초과 알림" 섹션 표시. 강제 분리 안 함.

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬 |
|---|---|---|
| 외부 디렉터리 흡수 | `/absorb` | [다루지 않음] |
| 만료와 아카이브 | `/garden` | [다루지 않음] |
| 자동 메모리 정리 | `/memory-garden` | [다루지 않음] |
| 단건 코드 검증 | `/learn` | [다루지 않음] |
| AI/사람 레이어 재구성 | `/dualize-docs` | [다루지 않음] |
| 프로젝트 진입 산출 | `/on-boarding` | [다루지 않음] |
| 세션 학습을 문서에 증분 반영 | 이 스킬 | [핵심] |

## 다음 스킬 연결

- `CLAUDE.md` 200줄 근접 시 `/optimize-claude-md`
- 외부 디렉터리 흡수 필요 시 `/absorb {path}`
- 만료 정리 시점에는 `/garden`
- 신규 모듈이나 고객사 정의는 `/briefing` 또는 `/customer-profile`
- 단건 claim 코드 검증은 `/learn`
- 데이터 부재 시 `/on-boarding`

## 제약조건

- 세션 컨텍스트 외 입력 금지
- CONFLICT 자동 해결 금지
- 신규 파일은 매칭 부재 + 승인 시
- 분량 임계 사전 검사, 강제 분리 안 함
- 부분 승인 시 미반영 항목 보고 명시
- 출처 추적: 모든 변경에 `(출처: 세션 N절)`
- 시크릿과 PII 마스킹
- `--dry-run` 시 Phase 5 절대 미실행
- 멱등성: Phase 3 SKIP 검사로 보장

## 검증 시나리오

공통 3블록은 CONTRACT 6-1절 참조.

### 이 스킬의 고유 실패 시나리오

[환경/규모] 추출 12+ / sink 12+
- 신호: Phase 1 영속 학습 ≥ 12 또는 Phase 2 후보 sink ≥ 12
- 대응: 우선순위(결정 > 규칙 > 사실 > 관계 > 타임라인 > 인사이트) 컷오프 + AskUser 추가 처리 옵션

[데이터 결함] CONFLICT 감지
- 신호: Phase 3 Grep 결과 기존 sink와 새 학습 상충
- 대응: 자동 해결 금지, Phase 4 좌우 비교 표

[사용자 개입 필요] AskUser 4회 초과
- 신호: 후보 9+ 분할 질의 4회 초과 예상
- 대응: "전체/선택/취소" 1차 + 묶음 2차 (4회 이내)

[의존성 부재] git 저장소 아님
- 신호: `git status` exit code != 0
- 대응: git diff 생략, mtime 추적, "되돌림 수동" 안내
