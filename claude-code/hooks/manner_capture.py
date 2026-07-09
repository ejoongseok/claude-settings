#!/usr/bin/env python3
# manner_capture.py  UserPromptSubmit 훅
#
# 내가 친 모든 프롬프트를 조용히 세션별 하루 파일에 누적한다. 즉각 피드백은 없다(해석은 /mirror 스킬).
#   저장: ~/.claude/manner/YYYY-MM/YYYY-MM-DD.{세션}.md   (세션별이라 동시 쓰기 충돌이 원천에 없음)
#   기록: 걸렸든 안 걸렸든 전부. 원문, 시각(시:분), 세션. 분모와 맥락을 위해 깨끗한 것도 남긴다.
#   검출: 구어체와 정량성은 prose-lint.sh 재사용, 군말은 여기서 빈도.
#   붙여넣기: 임계 넘으면 지시부만 추출하고 [추출], 지시부를 못 찾으면 [스킵]. 원본 덩어리는 남기지 않는다.
#   맥락: Stop 훅이 떨군 직전 응답 배턴을 집어 이 프롬프트에 붙인다(집으면 소비).

import sys, os, re, json, glob, subprocess, datetime

BASE = os.path.expanduser("~/.claude/manner")
PROSE_LINT = os.path.expanduser("~/.claude/agents/proofreader/prose-lint.sh")

FILLERS = ["뭔가", "막", "이제", "그냥", "좀", "약간", "그", "뭐"]
FILLER_RATIO = 0.08
FILLER_SHORT_N = 15
FILLER_SHORT_MIN = 3

PASTE_LINE_LEN = 200
PASTE_TOTAL = 2000
BATON_MAX_AGE = 60 * 60 * 12


def read_stdin_json():
    # 윈도우 로케일 코덱이 서러게이트를 만들지 않도록 raw 바이트를 UTF-8 로 직접 디코딩.
    try:
        raw = sys.stdin.buffer.read()
        return json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        return {}


def clean(s):
    # 혹시 남은 서러게이트를 걸러 UTF-8 로 안전하게 쓰게 한다.
    return s.encode("utf-8", "replace").decode("utf-8") if isinstance(s, str) else s


def read_input():
    data = read_stdin_json()
    prompt = clean((data.get("prompt") or data.get("user_prompt") or "").strip())
    sid = str(data.get("session_id") or "nosession")
    return prompt, sid


def session_short(sid):
    return re.sub(r"[^A-Za-z0-9_-]", "", sid)[:12] or "nosession"


def style_lint_off():
    d = os.getcwd()
    while True:
        if os.path.exists(os.path.join(d, ".style-lint-off")):
            return True
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent


def is_paste(text):
    if len(text) > PASTE_TOTAL:
        return True
    return any(len(ln) > PASTE_LINE_LEN for ln in text.splitlines())


def looks_human(ln):
    s = ln.strip()
    if not s or len(s) > PASTE_LINE_LEN:
        return False
    if re.search(r"\d{2}:\d{2}:\d{2}", s):
        return False
    if s[0] in "{[<":
        return False
    plain = sum(c.isalnum() or c.isspace() for c in s)
    return plain / len(s) > 0.6


def extract_instruction(text):
    human = [ln.strip() for ln in text.splitlines() if looks_human(ln)]
    extracted = " ".join(human).strip()
    if not extracted:
        return None, len(text)
    return extracted, len(text) - len(extracted)


def run_prose_lint(text):
    if not os.path.exists(PROSE_LINT):
        return []
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"manner.{os.getpid()}.md")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        out = subprocess.run(["bash", PROSE_LINT, tmp], capture_output=True, text=True).stdout
    except Exception:
        return []
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    hits = []
    for line in out.splitlines():
        m = re.search(r"\[(비격식|모호어)\]\s*(.*)", line)
        if not m or "인용 가능성" in line:
            continue
        axis = "구어체" if m.group(1) == "비격식" else "정량성"
        hits.append(f"{axis}({m.group(2).strip()[:40]})")
    return hits


def check_fillers(text):
    tokens = [t.strip(" .,!?~…\"'()[]{}·") for t in text.split()]
    tokens = [t for t in tokens if t]
    n = len(tokens)
    if n == 0:
        return None
    per = {f: sum(1 for t in tokens if t == f) for f in FILLERS}
    total = sum(per.values())
    used = ",".join(f for f, c in per.items() if c)
    if n >= FILLER_SHORT_N:
        if total and total / n >= FILLER_RATIO:
            return f"군말 {total / n * 100:.1f}%({used})"
    elif max(per.values()) >= FILLER_SHORT_MIN:
        return f"군말 다수({used})"
    return None


def pickup_baton(sid):
    now = datetime.datetime.now().timestamp()
    short = session_short(sid)
    mine = os.path.join(BASE, f".baton-{short}.json")
    head = None
    for path in glob.glob(os.path.join(BASE, ".baton-*.json")):
        try:
            age = now - os.path.getmtime(path)
        except OSError:
            continue
        if path == mine:
            if age <= BATON_MAX_AGE:
                try:
                    head = json.load(open(path, encoding="utf-8")).get("head")
                except Exception:
                    head = None
            try:
                os.remove(path)
            except OSError:
                pass
        elif age > BATON_MAX_AGE:
            try:
                os.remove(path)
            except OSError:
                pass
    return clean(head) if head else None


def ledger_path(sid):
    today = datetime.date.today()
    d = os.path.join(BASE, today.strftime("%Y-%m"))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"{today}.{session_short(sid)}.md")


def write_entry(sid, shown, marker, detections, prior, elided):
    path = ledger_path(sid)
    fresh = not os.path.exists(path)
    now = datetime.datetime.now()
    shown = clean(shown)
    prior = clean(prior) if prior else None
    detections = [clean(d) for d in detections]
    with open(path, "a", encoding="utf-8") as f:
        if fresh:
            f.write(f"---\ncreated: {now.date()}\ncategory: manner\nsession: {sid}\nretention: permanent\n---\n\n")
            f.write(f"# 말투 원장 {now.date()} (세션 {session_short(sid)})\n\n")
            f.write("자동 기록(UserPromptSubmit, 침묵). 해석과 개선본은 /mirror 스킬.\n\n")
        head = f"## {now.strftime('%H:%M')}"
        if marker:
            head += f"  {marker}"
        f.write(head + "\n")
        label = "원문(지시부)" if marker == "[추출]" else "원문"
        f.write(f"{label}: {shown}\n")
        if elided:
            f.write(f"(붙여넣기 {elided}자 생략)\n")
        f.write(f"검출: {', '.join(detections) if detections else '없음'}\n")
        f.write(f"직전응답: {prior if prior else '없음'}\n\n")


def main():
    prompt, sid = read_input()
    if not prompt or prompt.startswith("/"):
        return
    if style_lint_off():
        return

    prior = pickup_baton(sid)
    marker, elided, target, shown = "", 0, prompt, prompt

    if is_paste(prompt):
        extracted, elided = extract_instruction(prompt)
        if extracted:
            marker, target, shown = "[추출]", extracted, extracted
        else:
            marker, target, shown = "[스킵]", None, f"(붙여넣기 {len(prompt)}자, 지시부 없음)"

    detections = []
    if target is not None:
        detections = run_prose_lint(target)
        fm = check_fillers(target)
        if fm:
            detections.append(fm)

    write_entry(sid, shown, marker, detections, prior, elided)


if __name__ == "__main__":
    main()
