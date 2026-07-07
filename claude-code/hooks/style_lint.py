#!/usr/bin/env python3
"""PostToolUse 훅: 산출물 표현 린트 (경고 모드).

- 데이터: stdin JSON (tool_name, tool_input.file_path, content 또는 new_string)
- 검사 범위: 새로 쓰인 텍스트만.
  Write는 content 전체(전면 재작성은 전체를 새 저작으로 간주),
  Edit는 저장된 파일을 디스크에서 읽어 펜스(코드 블록) 맥락을 판정한 뒤
  new_string에 속한 줄만 귀속시켜 검사한다. 디스크를 읽지 못하면
  펜스 맥락을 알 수 없으므로 어휘 계열(이모지, 박다, 구어체)만 보수 검사.
- 파일 유형: md는 전체 규칙, 코드와 txt(java/js/ts/tsx/py/html/txt)는 어휘 계열만,
  그 외 확장자는 미검사.
- 신규 md(Write)는 frontmatter(첫 줄 --- 블록) 부재도 검출한다. 존재만 보고
  키 스키마는 보지 않는다(산출물 created/category/retention, memory 등
  파일 유형별 스키마가 달라서). 관례상 frontmatter 없는 README.md,
  INDEX.md, MEMORY.md는 제외. Edit는 소급 없음 원칙에 따라 미검사.
- 위반 발견 시 exit 2 + stderr. Claude에 피드백되어 자가 수정을 유도한다.
  파일은 이미 저장된 뒤라 차단이 아니라 경고다.
- 제외: `~/.claude` 등 .claude 설정 구역(규칙 정의라 언급과 사용 구분 불가,
  단 memory는 산출물이므로 검사함), 임시 디렉터리, CLAUDE.md 파일,
  상위 디렉터리 어딘가에 `.style-lint-off` 마커가 있는 저장소 전체.
- 기준 문서: ~/.claude/rules/expression.md
"""
import sys, json, re
from pathlib import Path

WHITELIST = "✓✗△"  # 허용 상태 기호

RULES_MD = [
    ("emoji", re.compile("[\U0001F000-\U0001FBFF☀-➿⬀-⯿️‼⁉]")),
    ("화살표", re.compile("[←-⇿⟰-⟿]")),
    ("화살표ascii", re.compile(r"(?<![-<>=!|`])(->|=>)(?![->=])")),
    ("별표장식", re.compile("[★☆]")),
    ("삼각불릿", re.compile("[▶▸►◀◁]")),
    ("참고표", re.compile("[※]")),
    ("섹션기호", re.compile("[§]")),
    ("번호기호", re.compile("[①-⓿㈀-㋿Ⅰ-ⅿ]")),
    ("가운뎃점", re.compile("[·•・ㆍ]")),
    ("긴줄표", re.compile("[—–―]")),
    ("한자", re.compile("[一-鿿㐀-䶿]")),
    ("박다", re.compile("박[다아어혀힌힘]|박제")),
    ("구어체", re.compile("죽었|뻗었|터졌|터진다|깨졌|깨진다|날아갔|꼬였|튀었|튄다|쏜다|먹힌|먹혔|씹혔|찍는다|찍었|말이 안 되|널뛰|굴러간")),
]
RULES_CODE = [r for r in RULES_MD if r[0] in ("emoji", "박다", "구어체")]
EQ_DEF = re.compile(r"(?<![=<>!+\-*/|])\s=\s(?!=)")  # 프로즈 정의용 등호 의심


def exempted(fp: Path) -> bool:
    try:
        for d in fp.parents:
            if (d / ".style-lint-off").exists():
                return True
    except OSError:
        pass
    return False


def fence_split(text: str):
    """(줄번호, 인라인코드 제거본, 원본 strip) 목록과 펜스 내부 줄번호 집합."""
    vis, fenced, fence = [], set(), False
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            fence = not fence
            fenced.add(i)
            continue
        if fence:
            fenced.add(i)
            continue
        vis.append((i, re.sub(r"`[^`]*`", "", line), s))
    return vis, fenced


def main() -> int:
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except Exception:
        return 0
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    raw_path = ti.get("file_path") or ""
    if tool not in ("Write", "Edit") or not raw_path:
        return 0
    low = raw_path.replace("\\", "/").lower()
    if "/appdata/local/temp/" in low:
        return 0
    if "/.claude/" in low and "/memory/" not in low:
        return 0
    name = low.rsplit("/", 1)[-1]
    if name in ("claude.md", "claude.local.md"):
        return 0
    ext = name.rsplit(".", 1)[-1] if "." in name else ""
    if ext != "md" and ext not in ("java", "js", "ts", "tsx", "py", "html", "txt"):
        return 0
    if exempted(Path(raw_path)):
        return 0
    delta = ti.get("content") if tool == "Write" else ti.get("new_string")
    if not delta or len(delta) > 2_000_000:
        return 0
    for ch in WHITELIST:
        delta = delta.replace(ch, "")

    hits = []
    unit = "L"
    if ext == "md":
        rules = RULES_MD
        attr = None  # None이면 전체 귀속
        if tool == "Write":
            base = delta
            if name not in ("readme.md", "index.md", "memory.md") and not base.startswith("---"):
                lines0 = base.splitlines()
                hits.append((1, "frontmatter부재", lines0[0].strip()[:70] if lines0 else ""))
        else:
            try:
                base = Path(raw_path).read_text(encoding="utf-8", errors="replace")
                if len(base) > 2_000_000:
                    return 0
                for ch in WHITELIST:
                    base = base.replace(ch, "")
                attr = {l.strip() for l in delta.splitlines() if l.strip()}
            except OSError:
                base, rules, unit = delta, RULES_CODE, "추가분 "
        vis, fenced = fence_split(base)
        for ln, clean, raw_strip in vis:
            if attr is not None and raw_strip not in attr:
                continue
            for rule, rx in rules:
                if rx.search(clean):
                    hits.append((ln, rule, raw_strip[:70]))
            if rules is RULES_MD and not clean.lstrip().startswith("|") and EQ_DEF.search(clean):
                hits.append((ln, "정의등호", raw_strip[:70]))
        if rules is RULES_MD:  # 표 앞 빈 줄 (펜스 밖에서만)
            raw = base.splitlines()
            for i in range(1, len(raw) - 1):
                ln = i + 1
                if ln in fenced or (ln + 1) in fenced:
                    continue
                if (raw[i].lstrip().startswith("|") and re.match(r"^\|[\s:|-]+\|?$", raw[i + 1].lstrip())
                        and raw[i - 1].strip() and not raw[i - 1].lstrip().startswith("|")
                        and (attr is None or raw[i].strip() in attr)):
                    hits.append((ln, "표앞빈줄", raw[i - 1].strip()[:70]))
    else:
        unit = "L" if tool == "Write" else "추가분 "
        for ln, line in enumerate(delta.splitlines(), 1):
            for rule, rx in RULES_CODE:
                if rx.search(line):
                    hits.append((ln, rule, line.strip()[:70]))

    if not hits:
        return 0
    err = sys.stderr
    try:
        err.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(f"[style-lint] {raw_path}: 표현 규칙 위반 의심 {len(hits)}건 (경고 모드, 파일은 저장됨)", file=err)
    for ln, rule, ex in hits[:10]:
        print(f" - {unit}{ln} [{rule}] {ex}", file=err)
    if len(hits) > 10:
        print(f" - 외 {len(hits) - 10}건", file=err)
    if any(r == "frontmatter부재" for _, r, _ in hits):
        print("frontmatter 기준: 전역 CLAUDE.md 산출물 형식 절 (created, category, retention 또는 파일 유형별 스키마).", file=err)
    print("대체 기준: ~/.claude/rules/expression.md. 수정하거나, 원문 인용 등 예외에 해당하면 사유를 한 줄 밝히고 진행하세요.", file=err)
    return 2


if __name__ == "__main__":
    sys.exit(main())
