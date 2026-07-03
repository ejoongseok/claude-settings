---
name: html-explain
description: 문서(파일) 또는 현재 세션 대화를 핵심부터 이해되는 인터랙티브 HTML로 재가공. 원본 불변, 별도 .html 생성. 트리거 "html로 보여줘 / 설명 html / 이해하기 쉽게 / 인터랙티브 / 외부 공유용 html". 호출 `/html-explain [파일경로 | 비움=세션] [--kind=...] [--external]`.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
argument-hint: "[<file.md> 또는 비움=현재 세션] [--kind=meeting|status|summary|rfp|api|explain|external] [--external]"
recommended-effort: high
---

# html-explain

## 입력

- 인자에 파일 경로가 오면 그 문서를 read.
- 인자가 없으면(또는 topic 단어만이면) 현재 세션 대화 전체 흡수: 한 일 / 정한 일 / 다음.
- `--kind` 없으면 내용으로 판별. `--external`은 외부 공유 모드.

## 절차

1. read: `assets/template.html`(스킨), `assets/design-principles.md`(0절 체크리스트), `assets/components.md`(컴포넌트 + kind 프리셋), `assets/content-rules.md`(내용 추출 10원칙), `assets/playbook.md`(해당 kind 누적 학습).
2. 입력 흡수(파일/세션).
3. **핵심 추출**: `assets/content-rules.md` 적용. 결론 먼저(역피라미드), What>How, 내부 경로와 상수와 플래그와 담당자 주관 redact, 정량과 절대 표기, 추정은 `추정`/`TBD`.
4. kind 판별 후 playbook 학습 반영.
5. `template.html`의 `{{TITLE}}{{SUBTITLE}}{{TOC_ITEMS}}{{MAIN}}` 를 components.md 컴포넌트로만 채움. 내용 구조가 배치를 정하되 담백 규칙(hero 금지, 색 배경 금지, 화려 컴포넌트 금지, 풀폭)은 절대 어기지 않음. TOC 항목은 `<a href="#s-id">제목</a>`, 섹션은 `<section class="s" id="s-id"><h2>제목</h2>`. 헤더 아이콘 없음.
6. `design-principles.md` 0절 체크리스트 통과 확인.
7. 저장: 작업 폴더의 `rendered/{YYYY-MM-DD}-{slug}.html`(폴더 없으면 생성). 입력이 파일이면 그 파일과 같은 폴더의 `rendered/`도 무방. 저장 후 원본 파일 미변경 확인.
8. 콘솔: 저장 경로 안내. 열기는 OS에 맞게 안내한다: macOS는 `open <경로>`, Linux는 `xdg-open <경로>`, Windows는 `start "" <경로>`.
9. external 모드: 콘솔에 정확성 검토 체크리스트를 출력한다. 내부 경로와 상수와 담당자 주관 제거 / 요약이 원문과 일치 / 추정 표시 / 저맥락화.
10. 사용자 피드백 시 `assets/playbook.md` 해당 kind에 1줄 append(날짜 포함, 간결하게).

## 비협상 제약

- 원본 절대 불변, 항상 별도 `.html`.
- 스킨은 `template.html` 그대로. 다크 금지. 이모지 금지.
- **담백 풀폭 고정**: 사이드바가 화면 왼쪽 끝에 붙고 본문은 풀폭(가운데 정렬 금지). hero 금지, 색 배경 박스 금지, 화려한 카드와 타임라인과 다이어그램 금지. 강조는 색이 아니라 굵기와 크기와 여백과 좌측 얇은 선으로. 색은 표의 O와 X, 그리고 주의와 중요 콜아웃에만 최소로. 헤더 아이콘 없음. 상세는 `components.md` 비협상 절.
- 외부 의존 추가 금지(Pretendard CDN 하나만), 그 외 CSS와 JS는 인라인.
- affordance 정직: 동작 요소는 `button`이나 `a`, 정적은 텍스트(가짜 버튼 금지).
- 디자인과 문서 품질 기준은 `design-principles.md`가 단일 출처, 여기 재기술 금지.
