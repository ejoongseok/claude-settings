---
name: adr
description: 기술 의사결정 기록 (Architecture Decision Record). 중요한 기술적 결정의 맥락, 대안, 근거를 구조화하여 기록합니다.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
---

> **외부-가시 문서**: [`rules/external-doc.md`](../../rules/external-doc.md) 10원칙 준수. ADR은 신규 입사자, 감사, 파트너 참조 전제. 내부 경로 금지, What > How, 정량과 절대 표기, 추측/확정 구분(근거 출처 명시).

## 역할

"왜 이렇게 결정했는지"를 미래의 팀원(또는 미래의 나)이 이해할 수 있도록 기술 의사결정을 구조화하여 기록한다.

톤: 간결하고 객관적. 근거 명확, 감정과 정치 배제.

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| 결정 전 복수안 비교와 협의 (제안/협의) | `/rfc` | [FAIL] 다루지 않음 |
| 아이디어 발산 (비교와 결정 없음) | `/brainstorm` | [FAIL] 다루지 않음 |
| 이미 내려진 기술 결정의 맥락, 대안, 근거 기록 | **이 스킬** | [OK] 핵심 |

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | 일반 SW 관점으로만 진행 (Tier 1) |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 이전 ADR | `docs/adr/` 또는 `.local.claude/adr/` | 선택 | ADR 번호 새로 시작 (ADR-0001) |
| RFC/브레인스토밍 | `.local.claude/rfc/`, `.local.claude/brainstorm/` | 선택 | 결정 배경 자동 수집 불가, 사용자에게 질문 |

## 입력

`$ARGUMENTS`로 결정 제목이나 맥락을 받는다.

| 입력 예 | 동작 |
|---------|------|
| `/adr 드라이브 파일 저장소를 NCloud로 전환` | 해당 결정에 대한 ADR 작성 |
| `/adr` (인자 없음) | 최근 ADR 목록을 보여주고 새로 작성할지 질문 |
| `/adr list` | 기존 ADR 목록 표시 |

## 정보 수집

> **[1M 활용]** 다음을 **단일 메시지에서 병렬 호출**:
> - Bash: `ls .local.claude/adr/` (기존 ADR 번호 충돌 방지)
> - Read: 기존 ADR `.local.claude/adr/*.md`, `CLAUDE.md`, `.local.claude/biz-rules.md`, 관련 `.local.claude/modules/{name}.md`
> - Grep: 결정과 관련된 코드/설정 키워드 (`*.java`, `*.yml`)
> - Read: 관련 `.local.claude/rfc/*.md`, `.local.claude/brainstorm/*.md` (배경)

### 1. 사용자 인터뷰
인자만으로 충분하지 않으면 아래를 질문:
- 어떤 문제를 해결하려는 건지?
- 고려한 대안이 있는지?
- 제약 조건 (일정, 비용, 기술 스택, 고객사 요구 등)?
- 이미 결정된 건지, 아직 논의 중인지?

### 2. 코드/설정 맥락
결정과 관련된 코드가 있으면 확인:
```bash
# 관련 모듈/설정 확인
grep -r "관련키워드" --include="*.java" --include="*.yml" -l
```

### 3. 기존 ADR 확인
```bash
ls .local.claude/adr/ 2>/dev/null
```
번호 충돌 방지 및 관련 ADR 연결을 위해 기존 목록 확인.

### 4. 관련 문서 확인
- `.local.claude/biz-rules.md`: 비즈니스 규칙에 영향 주는 결정인지
- `.local.claude/modules/{name}.md`: 영향받는 모듈
- `CLAUDE.md`: 기존 컨벤션과 충돌 여부

## 상태 정의

| 상태 | 설명 |
|------|------|
| 제안 | 아직 논의 중. 피드백 필요 |
| 승인 | 결정 확정. 실행 단계 |
| 대체됨 | 이후 다른 ADR로 대체됨 (대체 ADR 번호 링크) |
| 폐기 | 결정이 철회됨 |

## 출력 구조

```markdown
# ADR-{번호}: {결정 제목}

| 항목 | 내용 |
|------|------|
| 상태 | 제안 / 승인 / 대체됨 / 폐기 |
| 날짜 | YYYY-MM-DD |
| 결정자 | (논의 참여자) |
| 영향 범위 | 모듈, 고객사, 인프라 등 |

## 상황 (Context)

왜 이 결정이 필요한가? 어떤 문제나 변화가 이 결정을 촉발했는가?
- 배경 설명
- 현재 상태의 문제점
- 제약 조건 (일정, 비용, 기술, 인력, 고객 요구 등)

## 대안 (Options)

### 대안 A: {이름}
- 설명
- 장점
- 단점
- 예상 비용/기간

### 대안 B: {이름}
- 설명
- 장점
- 단점
- 예상 비용/기간

### 대안 C: {이름} (고려했으나 제외)
- 설명
- 제외 사유

## 결정 (Decision)

**{선택한 대안}을 채택한다.**

선택 근거:
- 근거 1
- 근거 2
- 근거 3

## 결과 (Consequences)

### 긍정적
- ...

### 부정적/리스크
- ...
- 완화 방안: ...

### 후속 작업
- [ ] ...
- [ ] ...

## 관련 ADR
- ADR-{번호}: {제목} ({관계 설명})
```

> **[메타인지]** 출력 전 자기 검증:
> 1. 근거 재점검: 각 대안의 장/단점, 비용, 기간에 근거(측정, 벤치마크, 모듈 문서)가 있는가?
> 2. 전제 검증: 결정이 유효하려면 어떤 전제(제약 조건, 트래픽 규모, 팀 역량)가 성립해야 하는가? 전제 변경 시 재고해야 할 ADR인가?
> 3. 반대 증거: "미래의 신규 입사자가 이 ADR만 보고 '왜 이 결정?'에 답할 수 있는가?" 자기 완결성 반박 1개 이상

## 파일 저장

Frontmatter (CONTRACT 7-2절 표준): `category: adr, retention: permanent, harvest_targets: [biz-rules.md]`

### 번호 부여
```bash
ls .local.claude/adr/ 2>/dev/null | sort -t'-' -k1 -n | tail -1
```
기존 ADR의 마지막 번호 + 1. 없으면 0001부터 시작.

### 저장 경로
- `.local.claude/adr/{번호}-{kebab-case-제목}.md`
- 디렉터리 없으면 `mkdir -p`로 생성

### 예시
- `.local.claude/adr/0001-ncloud-migration.md`
- `.local.claude/adr/0002-elasticsearch-index-strategy.md`

## 다음 스킬 연결

ADR 작성 완료 후 안내:
- 결정을 실행하려면 `/todo` (작업 분해)
- 결정에 대해 의견을 구하려면 `/draft` (공유용 초안)
- 결정이 비즈니스 규칙에 영향 주면 `/biz-rules` (규칙 업데이트)

## 제약조건

- **외부-가시 문서 공통 원칙 준수**: `rules/external-doc.md` (가독성 5 + 정직성 5). ADR은 팀 외부(신규 입사자, 감사, 파트너)에도 참조될 수 있음.
- ADR은 **결정을 기록**하는 것이지 **결정을 대신 내려주는 것이 아님**. 대안의 트레이드오프를 명확히 제시하되, 최종 결정은 사용자에게.
- 단, 사용자가 "결정해줘"라고 하면 추천안을 제시하고 근거를 설명.
- 코드 변경 없이 문서만 생성. 실제 구현은 `/todo`에서.
- 이미 존재하는 ADR과 같은 주제면 기존 ADR을 업데이트할지 새로 만들지 질문.

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT 6-1절** 참조.

### 이 스킬의 고유 실패 시나리오

**[데이터 결함]** 기존 ADR 번호가 겹침
- 신호: `.local.claude/adr/ADR-NNN-*.md` 에서 부여하려는 번호가 이미 존재
- 대응: 다음 번호로 자동 재번호 + 사용자에게 최종 번호 확인 요청 + 기존 ADR과의 관계(Supersedes / Related) 명시 질문

**[사용자 개입 필요]** 대안과 근거가 부재
- 신호: 결정에 대한 대안(Options)이 1개 이하이거나 근거(Context) 가 1줄 미만
- 대응: "ADR 은 의사결정 기록 문서, 대안 비교가 핵심" 안내 + `/brainstorm` 으로 대안 발산, `/rfc` 로 비교 권장 후 중단
