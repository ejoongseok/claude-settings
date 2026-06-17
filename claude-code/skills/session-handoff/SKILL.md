---
name: session-handoff
description: 세션 종료 직전 호출. 작업 유형 10종(sprint/pr/debug/doc/outreach/exploration/meta/retro/mixed/unknown) 자동 식별 + 본 대화 전체 흡수 + 참조 자산 3 채널 매핑(A 본 대화 read / B 사용자 명시 / C 메모리 인덱스 grep, 선택) + 엣지케이스 10종 방어 + 다음 세션 모델용 인계 문서 작성 + 민감 정보 redact + LATEST/INDEX 통합 + 클립보드 자동 복사. 호출 `/session-handoff [topic]`. large-context 모델 가정. 권장 effort=max (정밀도 비용 > 토큰 비용 — 짧은 대화는 high 절약 가능).
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
recommended-effort: max
fallback-effort: high
---

# 세션 인계 스킬 (session-handoff)

## 역할

본 세션 종료 시점에 호출되어, **다음 세션의 모델**이 컨텍스트를 재구성할 수 있도록 인계 문서를 작성한다. 인계 문서는 사람이 아닌 **다음 세션 모델 독자 기준** — 명령형 지시문 + frontmatter 메타 + structured data 위주. 콘솔 출력만 사람 친화 한국어로.

## 컨텍스트

- **호스트**: large-context 모델 가정. 본 대화 처음~끝 전체를 한 번에 흡수 가능. 더 작은 컨텍스트 모델로 새 세션 진입 가능성 시 분량 경고 자동 삽입.
- **호출**: 사용자 명시 (`/session-handoff [topic]`). `disable-model-invocation: true` — 자동 호출 X.
- **작업 유형 10종**:
  - `sprint` — 여러 세션에 걸친 반복 작업 (기능 개발 / 테스트 작성 / 분석 등 진척 추적 대상)
  - `pr` — PR 리뷰·작성
  - `debug` — 디버깅·단정 정정·오류 진단
  - `doc` — 명세 / 설계 / 외부 공유 보고서
  - `outreach` — 외부(거래처·고객·이해관계자) 응대
  - `exploration` — 대규모 코드베이스 탐색·모듈 분석
  - `meta` — 스킬·hook·설정·메모리 시스템 작성 (본 스킬 자체가 meta 사례)
  - `retro` — 회고·메모리 정리·작업 마무리
  - `mixed` — 2개 이상 50%+ 동시 매치
  - `unknown` — 신호 약함 (사용자 한 줄 확인 후 진행)
- **저장**: 작업 유형별 자동 경로 분기 (§자동 추론 경로). `LATEST.md` 매번 갱신, `INDEX.md` append.
- **독자 분리**:
  - 인계 문서 = 다음 세션 모델 → 명령형 + structured data
  - 콘솔 출력 = 사람 → 한국어 친화 + 사용자 입력 명령어 안내

## 자동 추론 경로

기본 출력 디렉터리는 `.claude/handoff/` (Claude Code 상태와 같은 위치). 프로젝트마다 다르면 사용자 명시 인자 우선.

| 작업 유형 | 경로 |
|---|---|
| sprint | `.claude/handoff/sprint-{YYYY-MM-DD}-{topic}.md` (별도 진척 추적 디렉터리가 있으면 그쪽) |
| pr | `.claude/handoff/pr-{PR번호}-{YYYY-MM-DD}-{HHMM}.md` |
| debug | `.claude/handoff/debug-{YYYY-MM-DD}-{HHMM}-{topic}.md` |
| doc | `.claude/handoff/doc-{YYYY-MM-DD}-{HHMM}-{topic}.md` |
| outreach | `.claude/handoff/outreach-{YYYY-MM-DD}-{HHMM}-{counterparty}.md` |
| exploration | `.claude/handoff/explore-{YYYY-MM-DD}-{HHMM}-{topic}.md` |
| meta | `.claude/handoff/meta-{YYYY-MM-DD}-{HHMM}-{topic}.md` |
| retro | `.claude/handoff/retro-{YYYY-MM-DD}-{HHMM}-{topic}.md` |
| mixed / unknown | `.claude/handoff/{YYYY-MM-DD}-{HHMM}-{topic}.md` |
| 사용자 명시 | 인자 그대로 |

Retention 디폴트: sprint·meta·retro=permanent / debug=14d / pr·doc·outreach·exploration=7d.

## 작업 유형 신호 매트릭스 (Step 1)

| 유형 | 트리거 (본 대화 / git / 디렉터리 시그널) |
|---|---|
| sprint | 진척 추적 파일 read·write / feature 브랜치 / 진척률·잔여 키워드 |
| pr | `gh pr ...` / github MCP 도구 / 본 세션 commit + push / `.github/` 활동 / PR 번호 언급 |
| debug | error trace 다수 / 테스트 반복 실패 / 가설·재현·진단 키워드 / stack trace paste |
| doc | `.md` 작성·갱신 50%+ / docs/ 활동 / 섹션·목차 |
| outreach | 외부 거래처/고객/이해관계자 이름 / 메일·메시지 / 미응답 추적 |
| exploration | read·grep·glob 위주 (write 0건) / 발견 키워드 / 결론 미도출 |
| meta | `.claude/skills/` / 설정 파일(`settings.json` 등) / `CLAUDE.md` / hook frontmatter / 스킬 frontmatter / `rules/` |
| retro | 회고 문서 작성 / 진척 추적 파일 마무리 갱신 / 메모리 다수 grep + 정리 / 메모리 파일 rename·merge·delete |
| mixed | 2개 이상 50%+ 매치 |
| unknown | 신호 약함 → 사용자 한 줄 확인 |

복수 매치 → `mixed`. 호출 인자 `[topic]` 이 유형 hint 포함 시 우선.

## 참조 자산 3 채널 + 작업 유형별 매트릭스

**식별 3 채널**:
- **A** — 본 대화 직접 read (large-context 흡수로 자동 식별)
- **B** — 사용자 명시 언급 ("X 문서 참조해" / "그 규칙 봐")
- **C** — 메모리 인덱스 grep (**선택** — `MEMORY.md`·`CLAUDE.md`·노트 파일 등 메모리 인덱스를 유지하는 경우). 본 세션 주제 키워드 (작업 유형 + topic + 도메인 명사) 로 grep.

**합산**: 중복 제거 + 우선순위 정렬 (A > B > C, type 가중치 `sprint-ssot > session-output > memory > convention > domain-doc > code-ref > external`).

**작업 유형별 디폴트 참조 자산** (셀은 참조 *종류* — 자신의 메모리·문서에서 해당 종류를 찾는다):

| 유형 | memory | domain-doc | sprint-ssot | code-ref | external |
|---|---|---|---|---|---|
| sprint | 본 대화 read + 테스트·검증 게이트 관련 메모리 | 도메인 규칙·모듈 문서 | 진척 추적 파일 | 본 세션 변경 코드 site:line | 학습 노트 |
| pr | 외부 공개·코드 컨벤션·DI 패턴 관련 메모리 | PR 템플릿·코드 컨벤션 가이드 | (해당 시) | PR 변경 3~5개 | PR description |
| debug | 보안 판단·진단·추정 금지 관련 메모리 | 도메인·모듈 문서 | (해당 시) | error site:line | error log paste |
| doc | 외부 산출물·내부 경로 redact 관련 메모리 | 본문 .md, 문서 인덱스 | (해당 시) | (해당 시) | (해당 시) |
| outreach | 외주·거래처 평가·외부 paste 보존 관련 메모리 | 거래처/고객 프로필, 외주 트랙 | (해당 시) | (해당 시) | 외부 paste 원본 |
| exploration | 본 대화 read + 주제 매치 | (해당 시) | (해당 시) | 탐색 파일 인벤토리 | (해당 시) |
| meta | 스킬 작성·외부 공개 관련 메모리 + 본 대화 read | 대상 `SKILL.md`(참조 스킬), 설정 파일, `CLAUDE.md`, 룰셋 | (해당 시) | 스킬·hook 도구 호출 대상 | (해당 시) |
| retro | 본 작업 모든 feedback·reference 류 메모리 | 진척 추적 파일, 회고 문서 | 진척 추적 파일 (메인) | (해당 시) | 학습 노트, 작업 로그 |

## 엣지케이스 처리 매트릭스 (10종)

| # | 케이스 | 검출 | 처리 |
|:---:|---|---|---|
| 1 | 짧은 대화 (turn < 3 또는 도구 호출 < 5) | Step 0 카운트 | 사용자 한 줄 확인 ("인계 가치 낮음, 진행할까요?") 후 Y 시 진행 |
| 2 | git detached / merge / dirty | `git status --porcelain` + `git symbolic-ref HEAD` | frontmatter `detached@{SHA}` / `merge:{base}..{head}` + § "환경 상태" 미커밋 인벤토리 |
| 3 | sprint 식별 후 진척 추적 파일 부재 | Step 1 후 파일 확인 | mixed 강등 + `.claude/handoff/` fallback |
| 4 | topic 특수 문자 / 충돌 | sanitize (`/\?*<>:\|"`) + 파일 확인 | sanitize + `-2`, `-3` suffix |
| 5 | 클립보드 실패 | 클립보드 명령 exit code / 미존재 | 콘솔만 + 실패 메시지 |
| 6 | LATEST 첫 호출 | `Test-Path` / `test -f` | Write 신규 생성 |
| 7 | 자산 50+ | Step 3.5 카운트 | 우선순위 정렬 → 상위 10개 § "진입 read 의무" + 나머지 § "관련 참조 (추가)" |
| 8 | 더 작은 컨텍스트 모델 가능성 | 사용자 명시 / 환경 | 분량 경고 자동 삽입 + "상위 5개만 read" 안내 |
| 9 | mkdir 실패 | 디렉터리 생성 exit code | 콘솔 에러 + 작성 중단 + LATEST/INDEX 보호 |
| 10 | 인계 자기 호출 재귀 | `category: handover` frontmatter 패턴 | raw 재포함 금지 — external 참조만 |

## 워크플로우 (Step 0–11, 서브 3.5·5.5)

### Step 0 — 멈추고 생각하기 + 엣지케이스 사전 점검

- 인계 시점 적절성 (작업 미완 / 정정 직후 / 큰 발견)
- **엣지케이스 #1 (짧은 대화)** — 본 대화 turn / 도구 호출 카운트. < 3 turn 또는 < 5 도구 호출 시 사용자 한 줄 확인 후 진행 분기.
- **엣지케이스 #2 (git 비정상)** — `git status --porcelain` + `git symbolic-ref HEAD`. detached / merge / dirty 검출 시 frontmatter 표기 + § "환경 상태" 미커밋 인벤토리 작성.
- retention 결정 (작업 유형 디폴트 적용).

### Step 1 — 작업 유형 자동 식별

§신호 매트릭스 10종 적용. 호출 인자 `[topic]` 안에 유형 hint (예: `meta-foo`, `debug-bar`) 있으면 우선.

**엣지케이스 #3 (진척 추적 파일 부재)** — sprint 식별 시 진척 추적 파일 존재 확인. 0건이면 `mixed` 로 강등.

### Step 2 — topic 파싱 + 경로 추론

- 호출 인자 우선
- 미지정 시 작업 유형 + 컨텍스트로 자동 추론 (예: sprint → 가장 최근 read 한 진척 추적 파일의 작업명)
- **엣지케이스 #4 (특수문자·충돌)** — `[topic]` sanitize: `/\?*<>:\|"` 제거 + 공백 → `-`. 같은 분 다중 호출 시 파일 존재 확인 후 `-2`, `-3` 자동 suffix.
- 경로 결정 (§자동 추론 경로 적용)
- 디렉터리 생성:

```bash
mkdir -p ".claude/handoff"
```

**엣지케이스 #9 (mkdir 실패)** — exit code ≠ 0 시 콘솔 에러 + 작성 중단 + LATEST/INDEX 갱신 차단 (이전 상태 보호).

### Step 3 — 컨텍스트 풀 수집 (본 대화 전체 흡수 강제)

- 본 대화 처음~끝 전체 read — 일부 구간 흡수 금지
- 사용자 정정·확인·결정 시점 markup
- 도구 호출 결과 (Read·Glob·Grep raw, Write 신규 파일)
- 다음 명령 실행:
  - `git status --porcelain`
  - `git log -20 --oneline`
  - `git symbolic-ref HEAD` (작업 유형 시그널)
- 작업 유형별 추가 read:
  - sprint → 진척 추적 파일, 학습 노트
  - pr → `gh pr view {N}`, PR description, review comments
  - debug → error log, 재현 단계
  - doc → 현재 .md 파일 last-written 상태
  - outreach → 마지막 회신·외부 paste·미응답
  - meta → 본 세션 작성·검토 대상 `.claude/skills/*/SKILL.md` 또는 설정 파일 등
  - retro → 본 작업 feedback·reference 류 메모리, 회고 문서

**엣지케이스 #10 (재귀)** — 본 대화에 `category: handover` frontmatter 인계 문서 read 흔적 있으면 raw 재포함 금지. type=external 절대 경로 참조만 § "진입 read 의무" 에 포함.

### Step 3.5 — 참조 자산 3 채널 식별

- **채널 A**: 본 대화에서 Read·Glob·Grep 으로 접근한 모든 파일 인벤토리 (large-context 흡수)
- **채널 B**: 사용자 명시 언급 추적 ("X 문서 참조해" / "그 규칙 봐" 등)
- **채널 C (선택)**: 메모리 인덱스를 유지하면 read. 본 세션 주제 키워드 (작업 유형 + topic + 도메인 + 핵심 명사) 로 description grep. 매치 메모리 중 관련성 강한 N개 후보.

**합산 + 중복 제거 + 우선순위 정렬**:
- 채널 우선: A > B > C
- type 가중치: sprint-ssot > session-output > memory > convention > domain-doc > code-ref > external

**엣지케이스 #7 (자산 50+)** — 카운트 ≥ 50 시 상위 10개만 § "진입 read 의무" 포함, 나머지 § "관련 참조 (추가)" 별도 섹션.

각 자산에 type 컬럼 분류 (7종):
- `session-output` — 본 세션 신규 생성 .md / .json / 이미지 등
- `memory` — 사용자 메모리 (feedback·reference·user·project 류)
- `convention` — 행동 지침·룰셋 (`CLAUDE.md`, `rules/*.md` 등)
- `domain-doc` — 프로젝트 도메인 룰 (도메인 규칙·모듈·고객 문서 등) — convention 과 구분
- `sprint-ssot` — 진척 추적 파일 등
- `code-ref` — 코드 파일:줄번호
- `external` — 학습 노트, 외부 paste 원본, 다른 인계 파일 등

**복수 채널 매치 표기**: 한 자산이 A/B/C 중 2 이상에 매치 시 `A/B` 또는 `A/B/C` 다중 표기 (강한 채널 앞). 예: 본 대화 직접 read + 사용자 명시 둘 다 = `A/B`.

### Step 4 — 정량 지표 추출 (작업 유형별)

본 대화 raw 데이터 추출. 정성 표현 (대략 / 여러 / N개) 금지. **추출 불가 시 `[미측정]` 명시** (추정 0건).

| 작업 유형 | 추출 지표 |
|---|---|
| sprint | 진척률 before → after, 카테고리별, 자산 N건, 산출물 N건, 정정 N건 |
| pr | PR 번호, 변경 파일 N, +N/-N 라인, 리뷰 미응답 N, CI 상태 |
| debug | 재현 시도 N, 가설 (배제 N / 잔여 N), 진단 도구 N, 검증 N |
| doc | 작성 섹션 N/M, 미완 N, 의사결정 대기 N |
| outreach | 발송 N, 회신 대기 N, 데드라인 N, 액션 N |
| exploration | 읽은 파일 N, 발견 N, 후속 N |
| meta | 작성·검토 대상 N, 변경 의도 (신규 도입 / 보강 / 폐기 / 통합), 영향 범위 (본 / 글로벌 / 양쪽), 검증 방법 |
| retro | 회고 범위, 정리 대상 N, rename·merge·delete N, 일반화 룰 도출 N |

### Step 5 — 발견·정정·결정 자동 추출

본 대화 흐름에서:
- **단정 정정 사이클** — 사용자 "X 가 아니라 Y" / "정정해" / "다시 봐" 추적 → 표
- **신규 메모리** — 본 세션 생성된 메모리·학습 노트 인벤토리
- **결정 사항** — 사용자 명시 (옵션 A/B/C 중 선택, 방향 확정)
- **자가 점검 게이트** (해당 시) — 반복 적용 규칙 코드 블록
- **데드 코드·by-design·silent breakage** (코드 작업) 발견

### Step 5.5 — 민감 정보 redact

다음 패턴 grep + mask 처리. **실제 자격증명은 절대 본문에 옮기지 않는다** — 형태만 식별:

| 패턴 | 처리 |
|---|---|
| 비밀번호 형태 (`password=` / `pwd=` / `passwd=` 뒤 값, 또는 대화 중 명시된 자격증명) | `[REDACTED-PWD]` |
| JWT (`eyJ...` 3 세그먼트) | `[REDACTED-JWT]` |
| API 키 / `Authorization: Bearer ...` / 암호화 토큰 placeholder | `[REDACTED-KEY]` |
| 개인 메일 (외부 paste 회신) | `[REDACTED-EMAIL]` 또는 도메인만 노출 |
| 전화·휴대폰 | `[REDACTED-PHONE]` |
| 공인 IP (사설 IP `10.*` / `192.168.*` / `172.16~31.*` 제외) | `[REDACTED-IP]` |

자격증명 인벤토리 표는 사용자명·소속·권한만 (자격증명 값 컬럼 통째 제외).

### Step 6 — 환경 상태 (조건부)

비활성 시 섹션 통째 생략. 활성 시:
- 브라우저 자동화 세션 — 로그인 사용자 (redact 후), 현재 URL, 마지막 액션
- DB INSERT/UPDATE 영역 (테이블·키값)
- 외부 컨텍스트 (회신 대기, 회의 일정)
- 미완 상태 (테스트 중단, build 실패, git 미커밋)

### Step 7 — 다음 액션 우선순위 정렬

**§다음 액션 정의**: 새 세션 모델이 **단독 진입 가능한 작업**만 포함. 사용자 결정·입력 대기 항목은 §사용자 트리거 대기 로 분리 — 둘 중 한 곳에만 등재 (중복 금지). 분리 기준:

- 모델이 컨텍스트만으로 즉시 시작 가능 → §다음 액션
- 사용자 응답 (Y/N, 옵션 선택, 외부 자료 paste 등) 없이 시작 불가 → §사용자 트리거 대기

각 후보:
- 진입 path (URL / 절대 경로 / gh 명령 등 구체)
- 가치 (★ / ★★ / ★★★)
- 부작용·리스크
- 예상 소요 (5분 / 30분 / 1시간 / 반일)
- 관련 참조 (§ "진입 read 의무" # 번호)

작업 유형별 디폴트 우선순위:
- sprint → 잔여 카테고리 진척 가치 순
- pr → 미응답 리뷰 → CI 실패 → conflict → 머지
- debug → 잔여 가설 → 환경 변수 → 회귀
- doc → 미완 섹션 → 의사결정 → 외부 공유
- meta → 검증 시나리오 → 사용 후 평가 → 보강
- retro → 일반화 룰 도출 → 메모리 정리 → 후속 액션

### Step 8 — 인계 문서 작성 (§템플릿 준수)

**0건 섹션 처리 분기 룰**:
- **이전 호출에 데이터 있던 영역이 본 호출 0건** = 한 줄 명시 ("0건 — 직전 N건" 형식) — stale 감지 가치 (예: 직전 sprint 진척 N건 → 본 호출 0건이면 진척 정체 신호)
- **본 세션 주제와 무관한 영역 0건** = 섹션 통째 생략 — noise 회피

분량 제한 없음 — 단 빈 섹션·중복·정성 표현 금지.

### Step 9 — LATEST + INDEX 통합

```bash
mkdir -p .claude/handoff
```

`LATEST.md` 내용 — Write 로 갱신 (Append X):

```markdown
{인계_파일_절대_경로}

# 메타
created: {YYYY-MM-DD HH:MM}
work_type: {work_type}
topic: {topic}
```

`INDEX.md` — 한 줄 append:

```
{YYYY-MM-DD HH:MM} | {work_type} | {topic} | {retention} | {인계_파일_절대경로}
```

**엣지케이스 #6 (LATEST 첫 호출)** — `Test-Path` (PowerShell) 또는 `test -f` (Bash) 로 존재 확인. 없으면 Write 신규 생성.

### Step 10 — 자가 점검 게이트

**형식 검증**:

- [ ] frontmatter 12 필드 (created/category/work_type/project/type/retention/topic/valid_until/model/source_session_branch/source_session_last_commit/edge_cases_detected) 포함
- [ ] § "다음 세션 모델 지침" 명령형 톤 (안내문·강조어 0건)
- [ ] § "진입 read 의무" type 컬럼 7종 (session-output/memory/convention/domain-doc/sprint-ssot/code-ref/external) 중 1개로 모두 분류
- [ ] 식별 채널 복수 매치 시 `A/B`, `A/B/C` 다중 표기 적용
- [ ] § "변경 / 신규 파일" 표 `git 추적` 컬럼 모두 분류 (tracked/untracked/ignored/N/A)
- [ ] work_type 값이 10종 중 1개
- [ ] 메모리 채널 사용 시 1개 이상 (예외: 메모리 인덱스 미유지 / unknown + 본 대화 read 0건)
- [ ] § "진입 read 의무" 상위 10개 이하 (51+ 시 별도 섹션)
- [ ] 정량 지표 정성 표현 0 + `[미측정]` 명시
- [ ] 다음 액션 1개 이상 + path·가치·소요·참조
- [ ] stale 검증 표 + edge_cases_detected 항목
- [ ] frontmatter `edge_cases_detected` YAML 안전 형식 (`["#N", "#M"]` 또는 `[]`) — 인라인 설명 금지
- [ ] §다음 액션 vs §사용자 트리거 대기 **중복 등재 0건** (모델 단독 진입 가능 / 사용자 입력 필요 — 양자택일)
- [ ] §"0건 명시" 항목은 직전 회차 데이터 있던 영역만 (무관 영역 0건은 통째 생략 — 분기 룰 적용)
- [ ] 표·코드 블록 앞뒤 빈 줄 (CommonMark — grep 부분 read 효율)
- [ ] 빈 섹션 0건
- [ ] 이모지 0
- [ ] redact: 비밀번호/JWT/API 키/외부 메일 grep 0
- [ ] **엣지케이스 #1~10 모두 검출·처리 완료**

**모델 재진입 가능성** (자가 read 1회 — 검토자 모드):

- [ ] 정량 추출 가능
- [ ] 다음 액션 식별 가능
- [ ] 참조 자산 모두 절대 경로 + type + 목적 명시
- [ ] 사람 친화 안내문 0건
- [ ] 분량 경고 (해당 시) 표시

### Step 11 — 콘솔 출력 + 클립보드 자동 복사

**엣지케이스 #8 (더 작은 컨텍스트 모델 가능성)** — 사용자 명시 또는 환경 시그널 시 인계 문서 § "다음 세션 모델 지침" 첫 줄에 분량 경고 자동 삽입:

> 본 문서 분량 {N}줄. 작은 컨텍스트 모델은 § "진입 read 의무" 상위 5개만 read 권장.

콘솔 출력 양식 (§콘솔 출력 양식 참조).

클립보드 복사 (OS에 맞게 — macOS `pbcopy` / Linux `xclip -selection clipboard` 또는 `wl-copy` / Windows `clip`):

```bash
# 예 (macOS)
printf '%s' "@.claude/handoff/LATEST.md 읽고 진행해" | pbcopy
```

**엣지케이스 #5 (클립보드 실패)** — 클립보드 명령 exit code ≠ 0 또는 명령 미존재 검출 시 콘솔만 출력 + 실패 메시지 ("클립보드 복사 실패. 위 명령어를 수동 복사하세요.").

## 다음 세션 모델 독자 기준 인계 문서 템플릿

데이터 없는 섹션 통째 생략. 명령형 + structured data. 사람 친화 안내문·강조어 금지. 코드 블록·표 앞뒤 빈 줄 의무 (CommonMark — grep 부분 read 효율).

```markdown
---
created: {YYYY-MM-DD HH:MM}
category: handover
work_type: {sprint | pr | debug | doc | outreach | exploration | meta | retro | mixed | unknown}
project: {project 식별자 또는 'general'}
type: session-handover
retention: {7d | 14d | permanent}
topic: {sanitized topic}
valid_until: {YYYY-MM-DD}
model: {모델 capability — 예: large-context}
source_session_branch: {git branch | detached@{SHA} | merge:{base}..{head}}
source_session_last_commit: {short SHA}
edge_cases_detected: ["#N", "#M"]  # YAML 안전 형식 — 빈 배열은 [] / 상세 설명은 본문 §"환경 상태"
---

# 인계: {work_type}/{topic}

## 다음 세션 모델 지침

{분량 경고 — 작은 컨텍스트 모델 시 자동 삽입}

read 후 순차 수행:
1. frontmatter `work_type` + `edge_cases_detected` 분기 식별
2. § "진입 read 의무" 모든 절대 경로 read (병렬 가능, type 우선순위 sprint-ssot → session-output → memory → convention → domain-doc → code-ref → external)
3. § "환경 상태" 활성 세션 재연결 가능성 확인
4. § "stale 검증" 자가 점검 1회
5. § "다음 액션 우선순위" 1번 진입 또는 § "사용자 트리거 대기" 참조
6. 발견/정정/결정 표 = raw 기록 (재실행 X)

## 진입 read 의무

| # | type | 절대 경로 | 식별 채널 | 목적 |
|:---:|---|---|:---:|---|

식별 채널: A=본 대화 직접 read / B=사용자 명시 / C=메모리 인덱스 grep.

## 관련 참조 (추가 — 자산 50+ 시)

| # | type | 절대 경로 | 목적 |
|:---:|---|---|---|

## 본 세션 raw 컨텍스트

### git 상태

```
{git status output, dirty 시 미커밋 파일 명시}
```

### 변경 / 신규 파일

| 경로 | 작업 | git 추적 |
|---|---|---|

`git 추적` 값: `tracked` (git ls-files 매치) / `untracked` (git status `??`) / `ignored` (.gitignore 매치) / `N/A` (워크스페이스 외부). 새 세션 모델이 `git log` 만 보면 본 세션 작업 흔적 못 찾는 경우 (ignored / N/A) 식별 가능.

### 정량 지표

| 지표 | 값 | 비고 |
|---|---|---|

### 발견 / 단정 정정 (해당 시)

| # | 발견 / 단정 | 정정 / 검증 |
|:---:|---|---|

### 신규 메모리 / 학습 노트 (해당 시)

| 경로 | 카테고리 | 요지 |
|---|---|---|

### 사용자 명시 결정 (해당 시)

| # | 결정 | 적용 범위 |
|:---:|---|---|

### 자가 점검 게이트 (해당 시 — 반복 적용 규칙)

```{언어}
{코드 또는 명령}
```

## 환경 상태 (해당 시)

| 항목 | 값 |
|---|---|

## 다음 액션 우선순위

### 1. {제목} (★★★)

| 항목 | 값 |
|---|---|
| 진입 path | {URL / 절대 경로 / gh 명령} |
| 가치 | ★★★ |
| 부작용 | {없음 / list} |
| 예상 소요 | {5분 / 30분 / 1시간 / 반일} |
| 관련 참조 | {§ "진입 read 의무" # 번호} |

### 2. {제목} (★★)

### 3. {제목} (★)

## stale 검증 (재진입 시 1회)

| 항목 | 검증 명령 | 갱신 가능성 |
|---|---|---|
| git HEAD | `git log -1 --format=%H` ≠ {source_session_last_commit} → N 커밋 진행 | high |
| 환경 세션 | 브라우저/MCP 세션 종료 → 재로그인 필요 | high |
| 진척 추적 파일 mtime | mtime 변경 → 다른 세션 진행 가능성 | medium |
| 메모리 인덱스 mtime | 변경 → 신규 메모리 가능성 | medium |
| 인계한 메모리 mtime | 각 메모리 파일 mtime 변경 | low |
| 인계한 도메인 문서 mtime | 변경 → 도메인 룰 갱신 | low |
| edge_cases_detected | 새 세션 진입 영향 확인 | varies |

## 작업 유형별 추가 raw (해당 시)

### [pr 시]

| 필드 | 값 |
|---|---|
| PR 번호 | |
| 머지 상태 | |
| 리뷰 미응답 | |
| CI 상태 | |
| conflict | |

### [debug 시]

| 필드 | 값 |
|---|---|
| 재현 단계 | |
| 배제 가설 | |
| 잔여 가설 | |
| 다음 검증 | |

### [outreach 시]

| 필드 | 값 |
|---|---|
| 외부 컨택 (이름·도메인) | |
| 미응답 액션 | |
| 데드라인 | |

### [doc 시]

| 필드 | 값 |
|---|---|
| 문서 절대 경로 | |
| 작성 섹션 N/M | |
| 미완 섹션 | |
| 의사결정 대기 | |

### [meta 시]

| 필드 | 값 |
|---|---|
| 작성·검토 대상 | {SKILL.md / 설정 파일 / CLAUDE.md / hook / rules} |
| 변경 의도 | {신규 도입 / 보강 / 폐기 / 통합} |
| 영향 범위 | {본 프로젝트 / 글로벌 / 양쪽} |
| 검증 방법 | {정적 / End-to-end / 사용자 실측} |

### [retro 시]

| 필드 | 값 |
|---|---|
| 회고 범위 | {작업 단계 / 시기 / 시스템 영역} |
| 정리 대상 | {feedback / reference / 학습 노트} |
| rename·merge·delete 액션 | N건 |
| 일반화 룰 도출 | {N건 / 후보 / 폐기} |

## 사용자 트리거 대기 (모델 단독 진입 불가)

| # | 대기 항목 | 사용자 액션 | 비고 |
|:---:|---|---|---|
```

## 콘솔 출력 양식 (사람 친화 한국어)

```
[session-handoff] 인계 문서 작성 완료

파일: {인계_파일_절대경로}
LATEST 갱신: .claude/handoff/LATEST.md
INDEX append: .claude/handoff/INDEX.md
작업 유형: {work_type}  (10종 중 1개)
분량: {N} 줄
참조 자산: session-output {a} / memory {b} / convention {c} / domain-doc {d} / sprint-ssot {e} / code-ref {f} / external {g}
엣지케이스 검출: {none | #N, #M (자동 처리됨)}

클립보드 복사: {성공 — 단순 진입 프롬프트 복사됨 | 실패 — 위 명령어 수동 복사 필요}

새 세션 진입 — 다음 중 1개를 새 세션에 입력하세요:

1. LATEST 활용 (권장):
   @.claude/handoff/LATEST.md 읽고 진행해

2. 특정 인계 파일:
   @{인계_파일_경로} 읽고 진행해

3. 영역 지정 / 구체 액션:
   {인계_파일_경로} 보고 {우선순위_1_제목} 진행해
```

## large-context 활용 메타

- 본 스킬은 large-context 모델 가정 — 본 대화 처음~끝 전체 read 의무 (일부 구간 흡수 금지)
- 정량 지표는 raw 데이터 추출 — 추정 금지, 불가 시 `[미측정]`
- 분량 제한 없음 (50줄~500줄+ 모두 OK) — 정보 충실도 우선
- 새 세션도 같은 모델 가정 — 인계 문서 풀 read 후 즉시 재진입
- 더 작은 컨텍스트 모델 가능성 시 frontmatter `model` 메타 + 분량 경고 자동 삽입

## 양식 SSoT 원칙

- **양식 SSoT = §"다음 세션 모델 독자 기준 인계 문서 템플릿"** (본 SKILL.md 내부). 외부 어떤 인계 파일도 양식의 기본·표준 아님.
- 본 대화나 사용자 발언에 특정 인계 파일이 등장해도 그것은 **일회성 사례**. 채널 A (본 대화 직접 read) 로 자동 식별돼도 "참조 자산" 으로만 활용하고 양식·분량의 기본으로 일반화 금지.
- 분량은 본 세션 컨텍스트 양에 비례 — 짧은 대화 = 짧은 인계 (50줄 가능), 큰 작업 = 풍부 인계 (500줄+ 가능). 특정 사례의 풍부도를 모든 인계의 기본으로 매핑 금지.
- 양식 추가·변경은 본 SKILL.md 의 §템플릿 갱신을 통해서만 — 외부 참조 파일 갱신으로 양식 우회 X.

## 독자 분리 원칙

- **인계 문서 독자 = 다음 세션 모델** — 명령형 + frontmatter + structured data. 사람 친화 안내문·강조어 금지.
- **콘솔 출력 독자 = 사람** — 한국어·친화 톤 + 사용자 입력 명령어 안내.

## 참조 자산 식별 원칙

3 채널 합산 — A 본 대화 직접 read / B 사용자 명시 / C 메모리 인덱스 grep(선택). type 컬럼 분류로 새 세션 모델이 우선순위별 read 가능.

## 엣지케이스 방어 원칙

매트릭스 10종 사전 점검 의무. 검출 시 frontmatter `edge_cases_detected` 명시 + 처리 방식 적용.

## 작업 유형 원칙

10종 (sprint/pr/debug/doc/outreach/exploration/meta/retro/mixed/unknown). 본 스킬 작성 자체가 **meta 작업 유형 사례**.

## 제약

- 본 스킬은 사용자 명시 호출만 (`disable-model-invocation: true`)
- 본 세션이 인계 가치 낮으면 (짧은 대화) 사용자 한 줄 확인 후 진행
- 인계 문서는 매번 새 파일 (덮어쓰기 X)
- LATEST.md 만 매번 덮어쓰기
- INDEX.md 는 append-only (expired 정리 별도)
- 민감 정보 redact 의무 — 누설 위험 시 작성 중단
- 본 세션 작업이 destructive op (git reset --hard 등) 직후면 인계 문서에 명시 + 사용자 트리거 대기로 분류

## 사람용 사용법

README.md 참조. 결과물 예시는 `examples/` — 사람이 산출물 형태를 미리 보기 위한 것이다. 양식 SSoT는 본 문서 §템플릿이며, 예시를 양식·분량의 표준으로 삼지 않는다 (§양식 SSoT 원칙).
