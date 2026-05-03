# /memory-garden 판정 few-shot 예시

> Phase 3 판정 전 참조. 각 예시는 메모리 본문 → claim 추출 → 검증 → 판정 + confidence + 근거 순서를 따른다.
> 판정 서술은 이 형식을 모범으로 삼는다.

---

## 예시 1 — Completed (프로젝트 종료)

**메모리**: `project_alpha_analysis.md`

**본문 요지**:
> project-alpha 분석 작업. 데이터 모델 정의 + 비즈니스 규칙 매핑. 종료 예정 2026-04-16.

**claim 추출**:
- C1: "project-alpha 분석 작업 존재"
- C2: "종료 예정 2026-04-16"

**검증 경로 매핑**:
- C1 → `.local.claude/projects/project-alpha/STATUS.md` Read
- C2 → 같은 STATUS.md에서 종료 상태 확인

**검증 결과**:
- `.local.claude/projects/project-alpha/STATUS.md:12` "종료 2026-04-16, 04-23 이후 아카이브 가능"
- 오늘 2026-04-22 기준 종료 후 6일 경과

**판정**: **Completed** / confidence **High**

**근거**: `projects/project-alpha/STATUS.md:12` "종료 2026-04-16" + 현재 의사결정에 영향 없음

**동작**: Phase 6-1 아카이브 → `{auto memory}/_archive/2026-04/`

---

## 예시 2 — Promoted (feedback 규칙 반영)

**메모리**: `feedback_test_strategy.md`

**본문 요지**:
> 테스트 전략 피드백 — 통합 테스트는 실제 DB를 써야 한다. 목(mock) 사용 금지. 과거 이슈에서 목/프로덕션 괴리로 마이그레이션 실패 경험.

**claim 추출**:
- C1: "통합 테스트에 실제 DB 사용"
- C2: "목 사용 금지 (과거 이슈 기반)"

**검증 경로 매핑**:
- 프로젝트 `./CLAUDE.md` + 개인 `~/.claude/CLAUDE.md` + `~/.claude/rules/*.md` 로드
- "통합 테스트", "mock", "데이터베이스" 키워드로 의미 매칭

**검증 결과**:
- `./CLAUDE.md:NN` "통합 테스트는 실 DB 사용. 목 금지" 반영 확인
- **또는** 반영되지 않은 상태라면 Active 유지

**판정 (반영 확인 시)**: **Promoted** / confidence **High**

**근거**: `./CLAUDE.md:NN` "통합 테스트는 실 DB 사용. 목 금지" — 동일 규칙 반영

**동작**: Phase 6-1 삭제

**주의**: grep 매칭 0건이어도 의미론적으로 반영됐을 수 있음(다른 표현). 반영처 본문을 Read해서 **모델이 의미 비교로 판정**.

---

## 예시 3 — Active (만료 임박이나 아직 유효)

**메모리**: `project_license_expiry.md`

**본문 요지**:
> 외부 라이브러리 dev 라이선스 만료일 2026-04-24. 벤더와 통화 결과로 갱신 여부 결정.

**claim 추출**:
- C1: "외부 라이브러리 dev 라이선스 존재"
- C2: "만료일 2026-04-24"
- C3: "벤더 통화로 후속 결정 대기"

**검증 경로 매핑**:
- C2 → 오늘 날짜(2026-04-22) vs 만료일 비교
- C3 → 관련 daily/meetings 로그 또는 후속 메모리 존재 확인

**검증 결과**:
- 오늘 기준 만료까지 2일 남음 → 아직 유효
- 후속 처리 없음 → 해소되지 않은 라이브 상태

**판정**: **Active** / confidence **High**

**근거**: 오늘 2026-04-22 vs 만료일 2026-04-24 (D-2). 현재 의사결정에 여전히 영향

**주의**: 만약 오늘이 2026-04-25 이후였다면
- 후속 처리 확인됨 → **Resolved**
- 후속 처리 불명 → **Stale**(사용자 확인) 또는 **Outdated**(갱신 필요)

이 예시는 "**시간 의존 판정은 날짜 비교가 필수**"를 보여준다.

---

## 예시 4 — Duplicate (관계 그래프 containment)

**메모리 A**: `project_beta_overall.md`
**메모리 B**: `project_beta_crossorigin_poc.md`

**Phase 2 관계 탐지**:
- 둘 다 project-beta 주제
- A는 전체 프로젝트 진행 상태(1단계 PR #303 머지, 2단계 진행 중)
- B는 그 안의 특정 실증(cross-origin 검증 완료)

**관계 유형**: **containment** — B는 A의 일부 마일스톤

**Phase 3 판정**:
- A → **Active**, confidence High (전체 프로젝트 라이브)
- B → **Duplicate** 후보, confidence Med

**검증**:
- B의 주장("cross-origin 실증 완료")이 A에 이미 "1단계 PR #303 머지"로 표현됐는지 확인
- B가 독립적으로 인용될 가치가 있는 상세(예: 특정 패턴·숫자·제약)를 품고 있으면 → **reference 관계**로 재분류, 둘 다 Active

**판정 (독립 가치 없음)**: **Duplicate** / confidence Med → Phase 6-1 통합 (A에 흡수)
**판정 (독립 가치 있음)**: 둘 다 **Active**, 관계는 `reference`

**근거**: Phase 2 관계 그래프 `B --containment--> A` + B의 상세가 A에 포괄 확인

---

## 예시 5 — Outdated (부분 불일치)

**메모리**: `project_gamma_assignment.md`

**본문 요지**:
> project-gamma TF — PL 1명 단독 담당. 2026-04-16 추가로 백엔드 개발자 1명 공식 배정, 프론트 개발자 1명 빠짐.

**claim 추출**:
- C1: "PL 1명 담당"
- C2: "2026-04-16 백엔드 개발자 1명 배정"
- C3: "프론트 개발자 1명 빠짐"

**검증 경로 매핑**:
- 최신 daily/meetings에서 project-gamma TF 언급 확인
- `.local.claude/projects/project-gamma/STATUS.md` Read

**검증 결과 가상 시나리오**:
- STATUS.md에 "PL 1명 유지, 2026-04-20 백엔드 개발자 재할당 해제"가 있다면 → C2가 outdated
- 나머지 claim은 유효

**판정**: **Outdated** / confidence Med (부분 불일치)

**근거**: `projects/project-gamma/STATUS.md:NN` "백엔드 개발자 재할당 해제 2026-04-20" — 메모리의 C2와 불일치

**동작**: Phase 6-1 갱신 — 해당 부분만 Edit, 나머지 유지. `description`도 재확인

---

## 예시 6 — Stale (근거 부족)

**메모리**: 가상 `project_xyz.md`

**본문 요지**:
> XYZ 프로젝트 진행 중. 관련 이슈는 점차 해소되고 있음.

**claim 추출**:
- C1: "XYZ 프로젝트 존재"
- C2: "이슈 해소 중"

**검증 경로 매핑**:
- C1 → 프로젝트 STATUS.md 존재 확인
- C2 → "점차 해소"가 구체성 없음. 검증 경로 매핑 실패

**판정**: **Stale** / confidence Low

**원인**: C2가 추상 서술. 근거 부족 → Phase 4-2 강등 규칙 적용

**동작**: Phase 6-1 실행 금지. Phase 5 보고서에 사용자 확인 항목으로 포함. "C2의 구체적 근거가 있나요? 없으면 삭제하시겠어요?"

---

## 예시 7 — Contradiction (Phase 2 모순)

**메모리 A**: `feedback_tone_concise.md` ("간결한 어투 선호")
**메모리 B (가상)**: 최근 작성된 상충 메모 ("장문 설명 선호, 세부 맥락 다 포함")

**Phase 2 관계**: contradiction

**판정**:
- 두 메모리가 상충하는 지시
- 최신 B가 실제 사용자 의도인지, 일회성 피드백인지 불명

**판정**: 둘 다 **Stale** / confidence Low — 사용자 확인 필요

**근거**: Phase 2 관계 그래프 `A <--contradiction--> B` + 최신성만으로 우선순위 결정 불가

**동작**: Phase 5 보고서 Stale 섹션에 함께 묶어 제시. 사용자가 "A 유지/B 폐기" 또는 "B 유지/A 폐기" 선택.

---

## 요약 패턴

- **확인 가능 사실 + 구체 출처** → High confidence 판정 가능
- **부분 불일치** → Outdated (Stale 아님)
- **검증 경로 매핑 실패** → Stale (Low confidence)
- **관계 그래프 우선 활용** → Duplicate/Resolved 판정 정확도 향상
- **모순은 항상 사용자 확인** → 자동 처리 금지
