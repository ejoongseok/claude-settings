# html-explain 컴포넌트 라이브러리

> `template.html` 스킨이 정의한 클래스로 `{{MAIN}}`과 `{{TOC_ITEMS}}`를 채울 때 쓰는 스니펫. 필요한 것만 골라 적응형 배치. 정적 정보는 `.tag`(버튼 아님), 동작은 `button`/`a`로.

## TOC 항목 (`{{TOC_ITEMS}}`)

```html
<a href="#s-tldr"><span class="n">00</span> 한눈에</a>
<a href="#s-flow"><span class="n">01</span> 흐름</a>
```
각 `href`는 main의 `<section id="...">`와 일치. scroll-spy가 자동 하이라이트.

## 섹션 + 헤더

```html
<section id="s-flow">
  <div class="sec-h"><span class="n">01</span><h3>제목</h3></div>
  ...
</section>
```

## 한눈에 / BLUF (역피라미드, 맨 위)

```html
<section id="s-tldr"><div class="hero">
  <span class="eyebrow">한눈에</span>
  <h2>핵심 한 줄 — <span class="key">결론·강조</span>.</h2>
  <ul class="why"><li>근거 1</li><li>근거 2</li></ul>
  <div class="tags"><span class="tag">라벨 <b>값</b></span></div>
</div></section>
```

## 콜아웃 (ok / info / warn / crit)

```html
<div class="note crit"><span class="lbl">주의</span><div>본문 <b>강조</b>.</div></div>
```
의미별: ok는 성공/낮은리스크, info는 특이점/참고, warn은 중간주의, crit는 치명/높음.

## 표 + 점수와 진행 막대

```html
<div class="card pad scrollx"><table>
  <thead><tr><th>기준</th><th class="win">A안</th></tr></thead>
  <tbody>
    <tr><td class="crit">항목</td>
      <td class="win"><div class="cell"><div class="bar"><span style="width:88%"></span></div><span class="num">88</span></div></td></tr>
  </tbody>
</table></div>
```
약한 값은 `<div class="bar dim">`, 추천/우위 열과 셀은 `class="win"`.

## 카드 (점수와 통계, 추천 핀)

```html
<div class="cards">
  <div class="stat"><div class="label">A안</div><div class="big">72</div><div class="meta">한 줄 평</div></div>
  <div class="stat win"><span class="pin">추천</span><div class="label">B안</div><div class="big">88</div><div class="meta">한 줄 평</div></div>
</div>
```

## 타임라인 + 예산 막대

```html
<div class="timeline">
  <div class="phase now" style="--w:3"><div class="pl">PHASE 1 · 4주</div><div class="pt">설계</div></div>
  <div class="phase" style="--w:5"><div class="pl">PHASE 2 · 7주</div><div class="pt">구축</div></div>
</div>
<div class="brow"><span class="bn">A안</span><div class="bar"><span style="width:64%"></span></div><span class="bv">0.64억</span></div>
```

## 코드 블록 (복사 버튼)

```html
<div class="code"><div class="topbar"><i></i><i></i><i></i></div>
  <button class="copy" onclick="copyText(this,'c1')">복사</button>
<pre id="c1">코드/JSON/curl</pre></div>
```
JSON 강조: `<span class="tok-key">"키"</span><span class="tok-punc">:</span> <span class="tok-str">"값"</span>`.

## 흐름 다이어그램 (과정과 시퀀스, 산문보다 우선)

> 번호 동그라미 배지(`.fn`) 안 씀. 화살표가 순서를 말함(겹침 배지는 산만, 밀도↑). 카드 + 화살표만.

```html
<div class="flow">
  <div class="fnode"><div class="actor">주체</div><div class="act">행동</div></div>
  <div class="farrow">&#10142;</div>
  <div class="fnode accent"><div class="actor">주체</div><div class="act"><b>핵심</b></div></div>
</div>
```

## 용어 툴팁 (회상보다 인식)

```html
<span class="term" tabindex="0" data-tip="용어 풀이">전문용어</span>
```
키보드 포커스로도 뜸. 인라인 코드는 `<span class="ic">코드</span>`.

## 원문 토글 (소스 문서가 있을 때만)

`template.html`의 단일 토글 버튼(`#modetoggle`, 클릭마다 스왑, 라벨이 다음 상태 안내) 유지 + 각 블록에 `class="only-easy"`(쉬운 설명) / `class="only-raw"`(원문 verbatim) 부여. 세션 요약 모드면 버튼 제거.

## footer (출처와 주의)

```html
<footer>생성 · 원본 §출처 · <b>원본 불변</b> · 폰트만 CDN<br>외부 공유 전 정확성 검토.</footer>
```

---

## kind별 프리셋 (가이드, 강제 아님)

| kind | 주로 쓰는 컴포넌트 |
|------|-------------------|
| meeting(회의록) | hero(결정 요약), 표(액션아이템 담당/기한), 콜아웃(미결) |
| status(진행현황) | hero, 카드(트랙 진행률), 막대, 타임라인, 콜아웃(블로커) |
| summary(요약) | hero(핵심 합의), 불릿, 콜아웃(결정/미해결), 흐름(필요 시) |
| rfp/decision | hero(BLUF 추천), 카드(점수), 표+막대(비교 매트릭스), 콜아웃(리스크) |
| api | hero, 흐름 다이어그램, 표(요청/응답), 코드, 콜아웃(에러/함정), 원문 토글 |
| external | 위 중 적합 + redact 강화 + footer 정확성 검토 |

## 헤더 아이콘 (kind별, `{{ICON}}`에 1개)

헤더 dot을 빈 장식이 아니라 문서 종류 표시로 쓴다. kind에 맞는 한 개를 `{{ICON}}`에 넣는다(흰색 선 아이콘으로 자동 스타일). 매칭 없으면 default.

```html
<!-- api -->      <svg viewBox="0 0 24 24"><path d="M9 8l-4 4 4 4"/><path d="M15 8l4 4-4 4"/></svg>
<!-- meeting -->  <svg viewBox="0 0 24 24"><path d="M5 6h14v9H10l-4 3v-3H5z"/></svg>
<!-- status -->   <svg viewBox="0 0 24 24"><path d="M5 19h14"/><path d="M8 19v-6"/><path d="M12 19V8"/><path d="M16 19v-9"/></svg>
<!-- summary -->  <svg viewBox="0 0 24 24"><path d="M6 8h12"/><path d="M6 12h12"/><path d="M6 16h8"/></svg>
<!-- rfp -->      <svg viewBox="0 0 24 24"><path d="M7 4h7l3 3v13H7z"/><path d="M9 13l2 2 4-4"/></svg>
<!-- external --> <svg viewBox="0 0 24 24"><path d="M12 4v10"/><path d="M8 8l4-4 4 4"/><path d="M6 13v5h12v-5"/></svg>
<!-- default -->  <svg viewBox="0 0 24 24"><path d="M7 4h10v16H7z"/><path d="M10 9h4M10 13h4"/></svg>
```
