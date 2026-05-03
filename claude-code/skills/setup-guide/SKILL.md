---
name: setup-guide
description: 개발 환경 셋업 가이드 (human/SETUP.md) 의 점검·갱신·암묵지식 캡처. 신규 합류자 안내, 환경 변경 추적(새 dependency·MCP·hook), 셋업 중 발견한 트러블슈팅 누적에 사용.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

`human/SETUP.md` 를 살아있는 문서로 유지하는 스킬. on-boarding 이 첫 산출 후 환경이 변하거나 셋업 중 새로 알게 된 노하우를 누적할 때 사용.

## 핵심 원칙

- **자동 추출 정보** (런타임·빌드·MCP·hooks 등) 는 코드/설정 파일이 진실의 원천. SETUP.md 가 어긋나면 SETUP.md 갱신
- **암묵 지식** (VPN, 인증, 협업 채널) 은 사람만 알 수 있음. 사용자 입력으로만 추가
- **트러블슈팅** 은 누적만, 삭제 금지 (다음 사람이 같은 문제 안 겪게)
- SETUP.md 가 없으면 `/on-boarding` 먼저 실행하라고 안내

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | 일반 SW 관점으로만 진행 (Tier 1) |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 런타임/빌드 메타 | `.nvmrc`, `.tool-versions`, `package.json engines`, `pom.xml`, `build.gradle` | 선택 | 수동 입력 요청, `[런타임 미확인]` 태그 |
| MCP/Hook 설정 | `.mcp.json`, `.claude/settings.json` | 선택 | MCP·Hook 섹션 생략 |
| 기존 SETUP.md | `human/SETUP.md` | 선택 | 신규 생성 모드 — `update/diff` 사용 불가 |

## 모드 판단

| 입력 | 모드 | 동작 |
|------|------|------|
| `/setup-guide check` 또는 `/setup-guide` (기본) | **점검** | 현재 환경 vs SETUP.md 일치 여부 검사 |
| `/setup-guide update` | **갱신** | 코드/설정 변경 감지 → SETUP.md 자동 반영 |
| `/setup-guide capture <내용>` | **수확** | 사용자 입력으로 암묵 지식·트러블슈팅 추가 |
| `/setup-guide diff` | **차이만** | 자동 추출 항목 vs SETUP.md 차이만 출력, 변경 없음 |

## 사전 체크 (모든 모드 공통)

> **[Opus 4.7 / 1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**하여 컨텍스트 효율화:
> - Read 병렬: `.nvmrc`, `.python-version`, `.tool-versions`, `package.json`, `pom.xml`, `build.gradle*`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `Pipfile`, `.mcp.json`, `.claude/settings.json`, `.claude/settings.local.json`, `docker-compose.yml`, `.env.example`, `Dockerfile`, `.vscode/extensions.json`, `.editorconfig`, `Makefile`, `README.md`, 기존 `human/SETUP.md` 전부 동시 로드
> - Glob: 위 파일들 존재 여부 일괄 탐색
> - Bash: 각 런타임 `--version` 확인 명령을 동시 실행 (점검 모드에서)
>
> 순차 호출 대신 병렬 호출로 네트워크 왕복 감소 + 자동 추출 소스 전체가 동시에 컨텍스트에 로드되어 SETUP.md 와의 diff 계산이 한 번에 완료.

1. `human/SETUP.md` 존재 확인
   - 없으면: "SETUP.md 가 없습니다. 먼저 `/on-boarding` 으로 초기 가이드를 생성하세요." 안내 후 종료
2. 프로젝트 루트의 자동 추출 소스 파일 식별:
   - `.nvmrc`, `.python-version`, `.tool-versions`, `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml`
   - `package.json`, `requirements.txt`, `pyproject.toml`, `Pipfile`
   - `docker-compose.yml`, `.env.example`, `Dockerfile`
   - `.vscode/extensions.json`, `.editorconfig`
   - `.mcp.json`, `.claude/settings.json`, `.claude/settings.local.json`
   - `Makefile`, `README.md`

## 모드별 프로세스

### 1. 점검 모드 (`check`)

**목적**: SETUP.md 따라하면 진짜 셋업 되는지 검증.

1. SETUP.md 의 §2 필수 설치 표를 Read 하여 각 항목의 **확인 명령** 추출
2. 각 확인 명령을 Bash 로 실행하여 현재 환경 측정 (`node -v`, `mvn --version`, `python --version` 등)
3. SETUP.md 가 명시한 버전 vs 실제 버전 비교
4. 결과 보고:

```markdown
## 환경 점검 — YYYY-MM-DD

### 일치 [OK]
| 항목 | SETUP.md 명시 | 현재 환경 |
|------|-------------|----------|
| Node.js | 20.11.x | 20.11.1 |
| Java | 17 | 17.0.10 |

### 불일치 [WARN]
| 항목 | SETUP.md | 현재 | 권고 |
|------|---------|------|------|
| Python | 3.11 | 3.9.6 | pyenv install 3.11 |

### 미설치 [FAIL]
| 항목 | 확인 명령 결과 |
|------|--------------|
| Maven | command not found |

### 자동 추출 소스 변경 감지
- `package.json` 가 SETUP.md 작성 후 수정됨 (의존성 추가 가능성) → `/setup-guide update` 권장
- `.mcp.json` 신규 생성됨 → SETUP.md §5 갱신 권장
```

### 2. 갱신 모드 (`update`)

**목적**: 코드/설정 변화를 SETUP.md 에 반영.

1. 자동 추출 소스 파일 전체 Read
2. SETUP.md §2 (필수 설치), §3 (환경 변수), §4 (IDE), §5 (Claude Code), §6 (첫 실행) 의 현재 내용 추출
3. **diff 계산**:
   - 추가됨: 자동 추출 소스에 있으나 SETUP.md 에 없는 것
   - 변경됨: 양쪽 다 있으나 값이 다른 것 (예: Node 버전 18 → 20)
   - 제거됨: SETUP.md 에 있으나 자동 추출 소스에 없는 것
4. **반영 전 사용자 확인** (최대 5건씩 묶어서 한 번에):
   ```
   다음 변경사항을 SETUP.md 에 반영할까요?
   
   추가 (3):
   - MCP 서버: github (Read 권한)
   - npm script: test:e2e
   - 환경 변수: SENTRY_DSN
   
   변경 (1):
   - Node.js: 18.x → 20.11.x (.nvmrc 변경)
   
   제거 (0):
   
   [전체 반영] [선택 반영] [취소]
   ```
5. 반영 후 SETUP.md 의 변경 라인을 사용자에게 표시
6. 자동 추출 소스 파일은 절대 수정하지 않음 (SETUP.md 만 수정)

**주의**: §1, §7, §8 (사전 요구사항·암묵 지식·트러블슈팅) 은 자동 갱신 대상이 아님. 손대지 않음.

### 3. 수확 모드 (`capture`)

**목적**: 사용자가 셋업 중 발견한 암묵 지식·트러블슈팅을 SETUP.md 에 누적.

`$ARGUMENTS` 가 자유 입력. 분류 자동 판단:

| 입력 패턴 | 분류 | 반영 위치 |
|----------|------|---------|
| "VPN 어떻게 받지", "DB 비밀번호", "Slack 채널" | 암묵 지식 | §7 사람에게 들어야 할 것 |
| "에러 났는데 ~로 해결", "이 명령 안 되면 ~" | 트러블슈팅 | §8 트러블슈팅 |
| "이 명령 추가해야 함", "Make target 이 ~" | 첫 실행 보강 | §6 첫 실행 |
| "OS 별 차이", "M1 Mac 에서는 ~" | 사전 요구사항 | §1 사전 요구사항 |

분류 모호하면 사용자에게 짧게 재질문 (선택지 제시).

**트러블슈팅 형식** (§8 누적 시):
```markdown
### {증상 한 줄}
- **환경**: macOS 14 / arm64 / Node 20.11
- **원인**: {원인 한 줄}
- **해결**: {명령/조치}
- **추가 일시**: YYYY-MM-DD
```

기존 트러블슈팅과 중복인지 Grep 으로 확인 후 추가. 중복이면 보강만.

### 4. 차이만 모드 (`diff`)

**목적**: 갱신 권장사항만 빠르게 확인. 실제 변경 없음.

`update` 모드의 1-3 단계까지만 실행. 4단계 사용자 확인 직전에서 멈추고 결과 출력 후 종료.

## 산출물 변경 시 주의

- SETUP.md 는 사람이 직접 손대는 문서 — 자동 갱신 시 사용자 추가 내용 (§7, §8) 보존 필수
- 변경 라인은 항상 사용자에게 표시 (몰래 수정 금지)
- 변경 후 SETUP.md 하단에 갱신 일시 한 줄 추가:
  ```markdown
  ---
  마지막 자동 갱신: YYYY-MM-DD ({모드}, N건 변경)
  ```

## 분량 임계 — 자동 분리

| 임계 | 동작 |
|------|------|
| ≤300줄 | 단일 `human/SETUP.md` 유지 |
| 301~500줄 | "곧 분리 권장" 알림 + 사용자 결정 |
| >500줄 | **분리 강제** — §8 트러블슈팅을 `human/SETUP-TROUBLESHOOTING.md` 로 이전 |

**분리 기준**:
- `human/SETUP.md` (메인): §1~§7, §9 (셋업 절차 본체)
- `human/SETUP-TROUBLESHOOTING.md` (수동 참조): §8 트러블슈팅만 (가장 빠르게 누적되는 영역)
- 메인 파일에 `→ 트러블슈팅: [SETUP-TROUBLESHOOTING.md](./SETUP-TROUBLESHOOTING.md)` 안내

추가로 §8 트러블슈팅이 200줄 넘으면 OS·역할별 sub-section 으로 재구조화 제안 (Mac/Windows/Linux, FE/BE 등).

## 다른 스킬 연결

- SETUP.md 없음 → `/on-boarding` 안내
- 트러블슈팅이 도메인 규칙·코드 버그 의심 → `/learn` 또는 `/cs` 안내
- 환경 변경이 빈번 (월 5회+) → 사용자에게 hook 자동화 (`PostToolUse` 또는 `SessionStart`) 제안

## 제약조건

- **SETUP.md 만 수정**. 자동 추출 소스 파일 (`.nvmrc`, `package.json` 등) 은 절대 수정하지 않음
- **§7 (암묵 지식), §8 (트러블슈팅) 은 자동 갱신 안 함**. 사용자 명시 입력 (`capture` 모드) 으로만 변경
- **자동 갱신 전 사용자 확인 필수**. "전체 반영 / 선택 반영 / 취소" 선택지 제시
- **트러블슈팅은 삭제 금지**. 누적만. 해결된 문제도 다음 사람에게 가치 있음
- **점검 모드의 Bash 실행은 read-only 명령만**. 설치·수정 명령은 절대 실행하지 않음 (사용자에게 안내만)
- **민감 정보 검출**. SETUP.md 에 비밀번호·API 키·토큰이 들어가려 하면 차단 + `[확인 필요]` placeholder 로 대체

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[의존성 부재]** 런타임 메타 파일(.nvmrc, package.json engines, pyproject.toml 등) 0개
- 신호: 런타임·버전 명시 파일 모두 부재
- 대응: 사용자에게 런타임 이름·버전 수동 입력 요청 + `[수동 입력]` 태그로 출처 표시

**[데이터 결함]** capture 모드에서 기존 SETUP.md 구조 불일치
- 신호: 기존 SETUP.md 섹션 스키마가 현재 표준과 다름
- 대응: diff 요약 제시 + 사용자 확인 후 재구성(merge/overwrite 선택)
