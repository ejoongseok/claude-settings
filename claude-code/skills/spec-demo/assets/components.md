# spec-demo 컴포넌트

> Readable Light 스킨 + 표현 16종. 생성 HTML은 self-contained(아래 스킨 CSS를 `<style>`에 인라인, 폰트만 CDN). **구조가 복잡한 표현은 `assets/examples/`의 검증된 데모에서 스킨·구조·JS를 복사**해 도메인만 바꿔 쓴다. 정적 정보는 `.st`/`.tag`(버튼 아님), 동작은 `button`/`input`/세그먼트.

## 케이스 → 표현 선택 (가장 먼저)

다이어그램·시각화는 한 종류가 아니다. **케이스 성격에 맞는 표현을 고른다 — 단일 패턴 강요 금지.**

| 케이스 성격 | 표현 | 소스 |
|---|---|---|
| 부모-자식 집계 (규칙 후보 병기) | 집계 (슬라이더 + 롤업) | 스킨 §집계 |
| 조건부 전파 (A→B 특정 상태) | 표 하이라이트 | 스킨 §조건부 |
| 이벤트 연쇄 (발행→리스너→체인) | 이벤트 흐름 (fan-out) | 스킨 §이벤트 |
| 사용자 행동 + 검증 | 유스케이스 (폼+토스트) | 스킨 §유스케이스 |
| 변경 전/후 | 비교 (AS-IS/TO-BE) | 스킨 §비교 |
| 다단계 소요량 (계층 + 롤업) | 트리 + 소요량 | `examples/tree-rollup.html` |
| 상태 전이 (정/역전이) | 상태도 | `examples/state-machine.html` |
| 시간순 상호작용 (요청 흐름) | 시퀀스 (lifeline) | `examples/sequence.html` |
| 흐름·분기 (워크플로우) | 플로우차트 (2D 분기) | `examples/flowchart.html` |
| 데이터 구조 + 트랜잭션 전파 | ER 전파 | `examples/er-transaction.html` |
| 시스템·서비스 구성·연동 | 아키텍처 토폴로지 | `examples/architecture.html` |
| 역할별 기능·권한·동작 | 유스케이스 다이어그램 | `examples/usecase-actors.html` |
| 화면·CRUD 여러 페이지 | 화면 흐름 프로토타입 | `examples/screen-flow.html` |
| 행×열 가능/결과 (권한·상태×액션) | 매트릭스 | 스킨 §매트릭스 |
| 작업·일정의 시간축 | 타임라인 막대 | 스킨 §타임라인 |

소스가 `examples/`인 표현은 그 파일을 열어 스킨·구조·JS를 그대로 복사하고 도메인 데이터만 케이스에 맞게 바꾼다(검증된 구조 보존). 표현은 닫힌 목록이 아니라 케이스에 맞춰 고르고, 새 표현은 playbook에 누적한다.

## 스킨 CSS (생성 HTML `<style>`에 인라인)

```css
:root{
  --paper:#f7f8fa; --surface:#ffffff; --surface-2:#f2f4f6; --surface-3:#e8ebee;
  --ink:#191f28; --ink-2:#4e5968; --ink-3:#8b95a1;
  --line:#e5e8eb; --line-2:#eef1f3;
  --accent:#3182f6; --accent-deep:#1b64da; --accent-soft:#eaf2ff; --accent-line:#c3dafe;
  --grad:linear-gradient(90deg,#4593fc,#1b64da);
  --ok:#15b86b; --ok-bg:#e7f7ef; --warn:#c8820a; --warn-bg:#fff6e0; --danger:#e85b48; --danger-bg:#fdeeeb;
  --r-chip:999px; --r-sm:10px; --r-md:14px; --r-lg:20px;
  --shadow:0 1px 3px rgba(25,31,40,.05),0 8px 28px rgba(25,31,40,.06);
  --shadow-soft:0 1px 2px rgba(25,31,40,.04);
  --sans:'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',-apple-system,system-ui,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,'D2Coding',Consolas,monospace;
  --ease:cubic-bezier(.22,.61,.36,1);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.72;letter-spacing:-.01em;-webkit-font-smoothing:antialiased}
.shell{max-width:1000px;margin:0 auto;padding:46px 22px 96px}

/* header / section / card */
header{display:flex;align-items:center;gap:12px;margin-bottom:26px}
.dot{width:34px;height:34px;border-radius:11px;background:var(--accent);flex:none;display:grid;place-items:center;box-shadow:0 6px 16px rgba(49,130,246,.28)}
.dot svg{width:18px;height:18px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
h1{font-size:23px;font-weight:700;margin:0;letter-spacing:-.02em}
.sub{color:var(--ink-3);font-size:13.5px;margin:3px 0 0;font-weight:500}
section{margin-bottom:36px}
.sec-h{display:flex;align-items:center;gap:11px;margin:0 0 18px}
.sec-h .n{font-family:var(--mono);font-size:15px;font-weight:700;color:var(--accent)}
.sec-h h3{font-size:21px;font-weight:700;margin:0;letter-spacing:-.02em}
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);box-shadow:var(--shadow-soft)}
.pad{padding:24px 26px}

/* hero — 추상 케이스는 h2를 질문형으로 */
.hero{border:1px solid var(--line);border-radius:var(--r-lg);background:var(--surface);padding:34px 36px 30px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--grad)}
.eyebrow{display:inline-flex;font-size:11.5px;font-weight:700;color:var(--accent-deep);background:var(--accent-soft);padding:5px 13px;border-radius:var(--r-chip);letter-spacing:.03em}
.hero h2{font-size:24px;line-height:1.45;font-weight:700;margin:13px 0 0;letter-spacing:-.02em;max-width:44ch}
.hero h2 .key{color:var(--accent-deep)}
.why{margin:16px 0 0;padding:0;list-style:none;display:grid;gap:11px;max-width:66ch}
.why li{position:relative;padding-left:18px;font-size:15px;color:var(--ink)}
.why li::before{content:"";position:absolute;left:0;top:9px;width:6px;height:6px;border-radius:50%;background:var(--accent)}
.why b{color:var(--accent-deep)}

/* note — 합의 포인트=warn, 참고=info */
.note{display:flex;gap:11px;border-radius:var(--r-md);padding:14px 16px;margin:10px 0;font-size:14.5px;line-height:1.62}
.note .lbl{flex:none;font-weight:800;font-size:10.5px;letter-spacing:.04em;padding:4px 9px;border-radius:8px;height:fit-content;white-space:nowrap}
.note.warn{background:var(--warn-bg)}.note.warn .lbl{background:#e6a93a;color:#4a3500}
.note.info{background:var(--accent-soft)}.note.info .lbl{background:var(--accent);color:#fff}
.note b{color:var(--ink)}

/* 정보 칩 / 상태 배지 (정적) */
.meta-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
.tag{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:500;color:var(--ink-2);background:var(--surface-2);padding:6px 12px;border-radius:8px}
.tag b{color:var(--accent);font-family:var(--mono);font-size:12px}
.st{display:inline-block;font-size:11.5px;font-weight:700;padding:4px 11px;border-radius:var(--r-chip);white-space:nowrap;transition:all .3s var(--ease)}
.st-wait{background:var(--surface-3);color:var(--ink-2)}
.st-prog{background:var(--accent-soft);color:var(--accent-deep)}
.st-done{background:var(--ok-bg);color:var(--ok)}

/* 표 (공통) */
table{width:100%;border-collapse:collapse;font-size:14.5px}
thead th{text-align:left;padding:12px 14px;background:var(--surface-2);color:var(--ink-2);font-size:12.5px;font-weight:700;border:0}
thead th:first-child{border-radius:10px 0 0 10px}thead th:last-child{border-radius:0 10px 10px 0}
tbody td{padding:13px 14px;border-bottom:1px solid var(--line-2);vertical-align:middle;color:var(--ink);transition:background .3s var(--ease)}
.empty{color:var(--ink-3);font-size:14px;text-align:center;padding:30px}

/* 버튼 (동작) */
.btn{font-family:inherit;font-size:13px;font-weight:600;padding:8px 15px;border-radius:var(--r-chip);cursor:pointer;border:1px solid var(--accent-line);background:var(--accent-soft);color:var(--accent-deep);transition:all .2s var(--ease)}
.btn:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.ghost{border-color:var(--line);background:var(--surface);color:var(--ink-2)}
.btn-reset{font-family:inherit;font-size:12.5px;font-weight:600;padding:7px 14px;border-radius:var(--r-chip);cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--ink-2)}

/* §집계 — 자식 슬라이더 → 부모 롤업 2종 병기 */
.slider-wrap{display:flex;align-items:center;gap:12px;min-width:220px}
input[type=range]{-webkit-appearance:none;appearance:none;flex:1;height:6px;border-radius:999px;background:var(--surface-3);outline:none;cursor:pointer}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:18px;height:18px;border-radius:50%;background:var(--accent);cursor:pointer;box-shadow:0 2px 6px rgba(49,130,246,.4);border:2px solid #fff}
input[type=range]::-moz-range-thumb{width:16px;height:16px;border-radius:50%;background:var(--accent);cursor:pointer;border:2px solid #fff}
.pct{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--ink);width:42px;text-align:right}
.rollup{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:6px}
@media(max-width:620px){.rollup{grid-template-columns:1fr}}
.rcard{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r-md);padding:18px 20px}
.rcard .rlabel{font-size:13px;font-weight:700;color:var(--ink-2)}
.rcard .rformula{font-size:11.5px;color:var(--ink-3);margin-top:2px;font-family:var(--mono)}
.rcard .rbig{font-size:36px;font-weight:800;letter-spacing:-.04em;margin:8px 0 4px;color:var(--ink)}
.rcard .rbar{height:8px;border-radius:999px;background:var(--surface-3);overflow:hidden}
.rcard .rbar>span{display:block;height:100%;border-radius:999px;background:var(--grad);transition:width .35s var(--ease)}
.diff{display:flex;align-items:center;gap:10px;margin-top:14px;padding:13px 16px;border-radius:var(--r-md);font-size:14px;font-weight:600}
.diff.same{background:var(--ok-bg);color:var(--ok)} .diff.gap{background:var(--warn-bg);color:#946008}
.presets{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px}

/* §조건부 — A 세그먼트 → B 표 changed/kept */
.seg{display:inline-flex;gap:4px;background:var(--surface-2);padding:4px;border-radius:var(--r-md)}
.segbtn{font-family:inherit;font-size:13.5px;font-weight:600;padding:9px 16px;border-radius:var(--r-sm);border:0;background:transparent;color:var(--ink-2);cursor:pointer;transition:all .18s var(--ease)}
.segbtn:hover{color:var(--ink)} .segbtn.on{background:var(--surface);color:var(--accent-deep);box-shadow:var(--shadow-soft)}
.arrow{text-align:center;color:var(--ink-3);font-size:13px;margin:14px 0;font-weight:600} .arrow b{color:var(--accent-deep);font-family:var(--mono)}
tbody tr.changed td{background:var(--warn-bg)} tbody tr.kept td{opacity:.5}
.chgmark{font-size:11px;color:var(--warn);font-weight:700;opacity:0;transition:opacity .3s} tr.changed .chgmark{opacity:1}

/* §이벤트 — 트리거 → 이벤트 → 리스너 fan-out */
.sim{display:grid;grid-template-columns:300px 1fr;gap:18px;align-items:start}
@media(max-width:760px){.sim{grid-template-columns:1fr}}
.statebox{position:sticky;top:18px}
.statebox .sttval{font-size:30px;font-weight:800;letter-spacing:-.03em;margin:4px 0 2px}
.path{margin-top:14px;padding-top:14px;border-top:1px solid var(--line-2)}
.path .ptrack{font-family:var(--mono);font-size:13.5px;color:var(--ink-3);line-height:1.9} .path .ptrack .pcur{color:var(--accent-deep);font-weight:700}
.triggers{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.tbtn{font-family:inherit;text-align:left;padding:10px 14px;border-radius:var(--r-md);cursor:pointer;border:1px solid var(--accent-line);background:var(--surface);color:var(--ink);box-shadow:var(--shadow-soft)}
.tbtn:hover{border-color:var(--accent);background:var(--accent-soft)} .tbtn .tl{font-size:13.5px;font-weight:700;display:block} .tbtn .te{font-family:var(--mono);font-size:11px;color:var(--ink-3);margin-top:2px}
.evt-node{background:#1a1530;border-radius:var(--r-md);padding:14px 18px;color:#fff;box-shadow:0 8px 22px rgba(26,21,48,.25)}
.evt-node .ev-tag{font-size:10.5px;font-weight:700;letter-spacing:.05em;color:#a9c7ff;text-transform:uppercase} .evt-node .ev-name{font-family:var(--mono);font-size:16px;font-weight:700;margin-top:3px}
.fanout-lbl{font-size:11.5px;font-weight:700;color:var(--accent-deep);margin:14px 0 8px;display:flex;align-items:center;gap:8px} .fanout-lbl::before{content:"";flex:none;width:18px;border-top:2px dashed var(--accent)}
.listeners{display:grid;gap:10px}
.listener{display:flex;gap:12px;align-items:flex-start;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--r-md);padding:12px 14px;opacity:0;transform:translateY(8px);transition:all .35s var(--ease)} .listener.show{opacity:1;transform:translateY(0)}
.listener .mod{flex:none;font-size:10.5px;font-weight:700;padding:4px 9px;border-radius:var(--r-chip);background:var(--accent-soft);color:var(--accent-deep);white-space:nowrap;font-family:var(--mono)}
.listener .leffect{font-size:13.5px;color:var(--ink);font-weight:600;margin-top:3px} .listener .leffect b{color:var(--accent-deep)}

/* §유스케이스 — 폼 → 검증 → 토스트 */
.field{margin-bottom:14px} .field label{display:block;font-size:12.5px;font-weight:700;color:var(--ink-2);margin-bottom:6px} .field label .req{color:var(--danger);margin-left:3px}
.field input,.field select{width:100%;font-family:inherit;font-size:14px;padding:10px 13px;border-radius:var(--r-md);border:1px solid var(--line);background:var(--surface);color:var(--ink);transition:border .2s var(--ease)}
.field input:focus,.field select:focus{outline:none;border-color:var(--accent)} .field.err input,.field.err select{border-color:var(--danger);background:var(--danger-bg)}
.field .emsg{font-size:12px;color:var(--danger);font-weight:600;margin-top:5px;display:none} .field.err .emsg{display:block}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.save{width:100%;font-family:inherit;font-size:14.5px;font-weight:700;padding:12px;border-radius:var(--r-md);border:0;background:var(--accent);color:#fff;cursor:pointer;margin-top:4px} .save:hover{background:var(--accent-deep)}
.cases{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:14px}
.cbtn{font-family:inherit;font-size:12.5px;font-weight:600;padding:7px 13px;border-radius:var(--r-chip);cursor:pointer;border:1px solid var(--line);background:var(--surface);color:var(--ink-2)} .cbtn:hover{border-color:var(--accent);color:var(--accent-deep);background:var(--accent-soft)}
tbody tr.fresh td{animation:flash 1.2s var(--ease)} @keyframes flash{0%{background:var(--ok-bg)}100%{background:transparent}}
#toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--ink);color:#fff;font-size:14.5px;font-weight:600;padding:13px 22px;border-radius:var(--r-md);opacity:0;pointer-events:none;transition:all .3s var(--ease);box-shadow:0 10px 30px rgba(0,0,0,.2);display:flex;align-items:center;gap:10px;max-width:90%}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)} #toast.err{background:#3a1a17}#toast.ok{background:#14352a}
#toast .ti{flex:none;font-size:11px;font-weight:800;padding:3px 8px;border-radius:6px} #toast.err .ti{background:var(--danger);color:#fff}#toast.ok .ti{background:var(--ok);color:#fff}

/* §비교 — AS-IS ↔ TO-BE */
.compare{display:grid;grid-template-columns:1fr 1fr;gap:14px} @media(max-width:620px){.compare{grid-template-columns:1fr}}
.chg{font-size:11px;font-weight:700;padding:2px 7px;border-radius:6px}
.chg.add{background:var(--ok-bg);color:var(--ok)} .chg.del{background:var(--danger-bg);color:var(--danger)} .chg.mod{background:var(--warn-bg);color:#946008}

/* §매트릭스 — 행×열 가능/결과 (권한·상태×액션) */
.matrix{width:100%;border-collapse:collapse;font-size:13.5px}
.matrix th,.matrix td{padding:10px 12px;border:1px solid var(--line-2);text-align:center}
.matrix thead th{background:var(--surface-2);color:var(--ink-2);font-size:12px;font-weight:700}
.matrix tbody th{background:var(--surface-2);text-align:left;font-weight:700;color:var(--ink)}
.matrix .y{color:var(--ok);font-weight:800} .matrix .n{color:var(--ink-3)} .matrix .r{color:var(--accent-deep);font-weight:700}
.matrix td.on{background:var(--accent-soft)}

/* §타임라인 — 작업·일정 시간축 막대 */
.timebar-row{display:grid;grid-template-columns:120px 1fr;align-items:center;gap:10px;margin:6px 0}
.timebar-row .tl{font-size:13px;font-weight:600;color:var(--ink-2)}
.timebar{position:relative;height:24px;background:var(--surface-2);border-radius:var(--r-sm)}
.timebar>span{position:absolute;top:3px;bottom:3px;border-radius:6px;background:var(--grad);display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:700}

footer{margin-top:30px;padding:16px 20px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r-md);font-size:12px;color:var(--ink-3);line-height:1.75}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto}}
```

## 헤더

`.dot`(컬러 박스 + 흰 선 svg) + h1 + `.sub`. svg는 케이스를 암시하는 단순 라인 아이콘 1개. 빈 장식 아닌 종류 표시.

## 표현별 메모

**스킨으로 직접 생성 (단순/공통):**

- **집계**: 자식 슬라이더 + 부모 카드 2개(규칙 병기, 예 단순/가중) + `.diff`. 추상적이라 질문형 hero. JS: 슬라이더 `oninput` → 두 규칙 재계산.
- **조건부 전파**: A `.seg/.segbtn` → B 표 `tr.changed`(노랑)/`tr.kept`(흐림). 필터 조건이 합의 포인트. JS: `setX(v,btn)` → 각 행 규칙 검사.
- **이벤트 연쇄**: 트리거 → `.evt-node` → `.listener` 순차 `.show`(220ms). self loop 금지 → 별도 리스너 화살표. 상태는 큰 텍스트 + `.path`(누적 로그 금지). 
- **유스케이스**: `.field` 폼 + `.cases` "잘못된 케이스" → 검증 → `#toast`(err/ok) + `.field.err`. 예외 흐름 강조.
- **비교**: `.compare` 2컬럼 + `.chg`(add/del/mod) + "변경점만 보기" 토글.
- **매트릭스**: `.matrix` 행×열(권한 역할×기능, 상태×액션). 셀 `.y`(허용)/`.n`(불가)/`.r`(결과·조건부). 행/열 클릭 시 `td.on` 강조.
- **타임라인**: `.timebar-row`(라벨 + `.timebar>span` 위치·폭). 작업·배치 일정의 시간축. 막대 클릭 → 상세.

**examples/ 복사 (구조 복잡 — 검증 데모에서 그대로):**

상태도 `state-machine.html` · 시퀀스 `sequence.html` · 플로우차트 `flowchart.html` · ER 전파 `er-transaction.html` · 아키텍처 토폴로지 `architecture.html` · 다단계 트리 `tree-rollup.html` · 유스케이스 다이어그램 `usecase-actors.html` · 화면 흐름 `screen-flow.html`. 각 파일의 `<style>`·구조·`<script>`를 복사하고 도메인 데이터만 케이스에 맞게 교체.

## 공통 장치

- **기술/업무 모드 토글** — 같은 케이스를 기술 언어/업무 언어로 전환(라벨 스왑). "개발자/비개발자" 금지 → "기술/업무". 업무 모드 = 고객·기획 정렬.
- **단계 재생(양방향)** — 첫 버튼 "시작 →", 이후 "다음 →"·"← 뒤로". step 인덱스 + 거쳐온 경로 동기화. 시퀀스·플로우차트·상태도 공통.
- **표현 기법명 노출 금지** — eyebrow/라벨에 "상태도·시퀀스·2D 분기" 같은 기법명을 쓰지 않는다(만든 사람 메타). eyebrow는 케이스 상황·맥락으로 쓰거나 생략.
- **affordance 정직** — 동작은 button/input/세그먼트. 정적 표시(상태·거쳐온 경로)는 버튼처럼 보이는 알약 칩 금지 → 큰 텍스트·경로(모노+화살표).

## 핵심 JS 패턴

슬라이더 `oninput` 재계산 / 세그먼트 `setX(v,btn)` / 순차 `setTimeout` 점등 / `toast(type,msg)` / 노드 클릭 `jumpTo` / 단계 `next`·`prev`(양방향) / 모드 `setMode`(라벨 재빌드).
