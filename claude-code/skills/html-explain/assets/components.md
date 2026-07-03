# html-explain 컴포넌트 (담백 풀폭 전용)

> 이 스킬의 모든 산출물은 담백하다. `template.html`의 플레이스홀더(`{{TITLE}} {{SUBTITLE}} {{TOC_ITEMS}} {{MAIN}}`)를 아래 컴포넌트로만 채운다. 레이아웃은 사이드바가 화면 왼쪽 끝에 붙고 본문이 풀폭이다(가운데 정렬 아님). 색 배경 박스, hero, 화려한 카드는 만들지 않는다.

## 비협상 (재현성의 근거)

이걸 어기면 예전처럼 매번 다르게 나온다. 반드시 지킨다.

- hero(큰 결론 박스)를 만들지 않는다. 한눈에나 결론도 그냥 섹션 하나로, 섹션 요약과 불릿 또는 항목으로 시작한다.
- 색 배경 박스를 만들지 않는다. 요약, 용어, 콜아웃 전부 배경 없이 좌측 얇은 선과 작은 라벨만 쓴다.
- 카드 그림자, 점수 막대, 통계 카드, 타임라인 막대, 흐름 다이어그램 같은 화려한 컴포넌트를 만들지 않는다.
- 강조는 색이 아니라 굵기, 크기, 여백, 좌측 얇은 선으로 한다. 색은 표의 O와 X, 그리고 주의와 중요 콜아웃에만 최소로 쓴다.
- 헤더에 아이콘을 넣지 않는다. 제목과 메타 한 줄만 둔다.

## TOC 항목 (`{{TOC_ITEMS}}`)

```html
<a href="#s-tldr">한눈에</a>
<a href="#s-done">한 일</a>
```

각 `href`는 본문 `<section class="s" id="...">`의 id와 일치한다. 스크롤에 따라 현재 항목이 자동으로 표시된다.

## 문서 헤더 (`{{TITLE}}` `{{SUBTITLE}}`)

`template.html`이 이미 헤더 자리를 잡아둔다. 제목과 메타 한 줄만 채운다. 아이콘은 없다.

## 섹션

```html
<section class="s" id="s-done">
  <h2>한 일</h2>
  ...
</section>
```

## 섹션 핵심 요약 (그 섹션 결론을 맨 위에 한두 줄)

```html
<div class="sec-summary">이 섹션에서 알아야 할 핵심을 한두 줄로.</div>
```

## 항목 (무엇 왜 어떻게, 어떻게는 접어서 점진적 공개)

```html
<div class="item">
  <span class="item-id">항목 라벨</span>
  <div class="item-title">제목</div>
  <div class="item-body">
    <p><b>무엇:</b> 무엇이 되는가.</p>
    <p><b>왜:</b> 왜 그런가(근거나 재사용).</p>
    <details><summary>어떻게</summary><p>구현이나 함정 상세.</p></details>
  </div>
</div>
```

한눈에나 결론 섹션처럼 짧은 요약이면 항목 대신 섹션 요약과 담백한 불릿을 쓴다.

```html
<div class="item-body" style="padding:0">
  <ul><li>핵심 1</li><li>핵심 2</li></ul>
</div>
```

## 용어 사전 (항목 하단, 그 항목에 처음 나온 용어)

```html
<div class="item-glossary"><dl><dt>용어</dt><dd>쉬운 풀이.</dd></dl></div>
```

용어 사전을 넣으면 `template.html`의 스크립트가 본문 첫 등장 용어에 자동으로 밑줄과 툴팁을 붙인다(위로 올려다볼 필요가 없어진다). 사전이 없으면 조용히 넘어간다.

## 표 (데이터가 밀집할 때만)

서술로 풀 수 있으면 서술이 먼저다. 비교나 매트릭스처럼 격자가 꼭 필요할 때만 표를 쓴다.

```html
<div class="item-body"><table>
  <thead><tr><th>항목</th><th class="c">가능</th></tr></thead>
  <tbody>
    <tr><td>기능</td><td class="c"><span class="ok-m">O</span></td></tr>
    <tr><td>기능</td><td class="c"><span class="x-m">X</span></td></tr>
  </tbody>
</table></div>
```

`ok-m`은 초록, `x-m`은 빨강, `co-m`은 주황(조건부), `na-m`은 회색(해당 없음). 난이도나 등급은 `<span class="lv mid">중</span>`, `lv hi`, `lv top`으로 배경 없이 색 텍스트만.

## 콜아웃 (담백, 좌측 선만)

```html
<div class="cal warn">본문. <b>강조</b>.</div>
```

`warn`은 주의(주황 선), `danger`는 중요(빨강 선), `ok`는 정리(회색 선). 배경색은 없다.

## 코드

```html
<pre>curl 이나 JSON 이나 코드</pre>
```

`item-body` 안에 두면 회색 코드 박스로 나온다.

## 용어 툴팁 (수동으로 붙일 때)

```html
<span class="term" tabindex="0" data-tip="용어 풀이">전문용어</span>
```

용어 사전을 쓰면 자동으로 붙으므로 대개 필요 없다.

## footer

```html
<footer>생성일과 출처. 원본 불변. 외부 공유 전 정확성 검토.</footer>
```

## kind별 구성 (컴포넌트는 다 담백, 내용 구성만 다르다)

kind가 달라도 스킨은 같다. 무엇을 담느냐만 다르다.

| kind | 담는 내용 |
|------|------|
| meeting(회의록) | 섹션 요약, 결정과 액션 항목, 담당과 기한 표 |
| status(진행현황) | 섹션 요약, 트랙별 항목, 진행률 표, 블로커 콜아웃 |
| summary(요약)와 세션 요약 | 섹션 요약, 한 일과 정한 것과 다음 항목, 불릿 |
| rfp(제안과 결정) | 섹션 요약, 비교 표, 기준 항목, 리스크 콜아웃 |
| api | 섹션 요약, 흐름을 서술한 항목, 요청과 응답 표, 코드 |
| explain(설명형) | 섹션 요약, 무엇 왜 어떻게 항목, 접기, 용어 사전 |
| external(외부 제공용) | 위에 더해 내부 경로와 담당자 주관을 지우고 저맥락으로 |
