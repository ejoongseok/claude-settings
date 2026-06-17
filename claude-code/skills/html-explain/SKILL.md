---
name: html-explain
description: 문서(파일) 또는 현재 세션 대화를 핵심부터 이해되는 인터랙티브 HTML로 재가공. 원본 불변, 별도 .html 생성. 트리거 "html로 보여줘 / 설명 html / 이해하기 쉽게 / 인터랙티브 / 외부 공유용 html". 호출 `/html-explain [파일경로 | 비움=세션] [--kind=...] [--external]`.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
argument-hint: "[<file.md> 또는 비움=현재 세션] [--kind=meeting|status|summary|rfp|api|external] [--external]"
recommended-effort: high
---

# html-explain

## 입력

- 인자에 파일 경로 → 그 문서 read.
- 인자 없음(또는 topic 단어만) → 현재 세션 대화 전체 흡수: 한 일 / 정한 일 / 다음.
- `--kind` 없으면 내용으로 판별. `--external` = 외부 공유 모드.

## 절차

1. read: `assets/template.html`(스킨), `assets/design-principles.md`(§0 체크리스트), `assets/components.md`(컴포넌트 + kind 프리셋), `assets/content-rules.md`(내용 추출 10원칙), `assets/playbook.md`(해당 kind 누적 학습).
2. 입력 흡수(파일/세션).
3. **핵심 추출** — `assets/content-rules.md` 적용: 결론 먼저(역피라미드), What>How, 내부 경로·상수·플래그·담당자 주관 redact, 정량 표기, 추정은 `추정`/`TBD`.
4. kind 판별 → playbook 학습 반영.
5. `template.html`의 `{{TITLE}}{{SUBTITLE}}{{ICON}}{{TOC_ITEMS}}{{MAIN}}` 를 components.md 컴포넌트로 채움. 적응형 — 내용 구조가 배치를 결정(고정 틀 강제 금지). 헤더 `{{ICON}}`는 kind에 맞는 헤더 아이콘(components.md "헤더 아이콘")으로 채움 — 빈 장식이 아니라 종류 표시, 매칭 없으면 default.
   - **소스 문서 모드**: `.seg`(원문 토글) 유지 + 핵심 블록을 `.only-easy`(쉬운 설명) / `.only-raw`(원문 verbatim)로 병기 — 해석 검증성 보존.
   - **세션 요약 모드**: `.seg` 블록 제거(원문 개념 없음).
6. `design-principles.md` §0 체크리스트 통과 확인.
7. 저장: 작업 폴더의 `rendered/{YYYY-MM-DD}-{slug}.html`(폴더 없으면 생성). 입력이 파일이면 그 파일과 같은 폴더의 `rendered/`도 무방. 저장 후 원본 파일 미변경 확인.
8. 콘솔: 저장 경로 안내. 열기는 OS에 맞게 — macOS `open <경로>`, Linux `xdg-open <경로>`, Windows `start "" <경로>`.
9. external 모드: 콘솔에 정확성 검토 체크리스트 출력 — 내부 경로·상수·담당자 주관 제거 / 요약이 원문과 일치 / 추정 표시 / 저맥락화.
10. 사용자 피드백 시 `assets/playbook.md` 해당 kind에 1줄 append(날짜·간결).

## 비협상 제약

- 원본 절대 불변 — 항상 별도 `.html`.
- 스킨은 `template.html` 그대로(라이트). 다크 금지. 이모지 금지.
- 외부 의존 추가 금지(Pretendard CDN 1개만) — 그 외 CSS·JS 인라인.
- affordance 정직: 동작 요소는 `button`/`a`, 정적은 `.tag`(가짜 버튼 금지).
- 고정 template N개 금지 — 적응형 배치 + playbook 누적.
- 디자인·문서 품질 기준은 `design-principles.md`가 SSoT — 여기 재기술 금지.
