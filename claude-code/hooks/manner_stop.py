#!/usr/bin/env python3
# manner_stop.py  Stop 훅
#
# Claude 응답이 끝나면 그 응답의 앞부분을 세션별 배턴 파일에 떨군다.
# 다음 프롬프트에서 manner_capture.py 가 이 배턴을 집어 "직전 응답" 맥락으로 붙인다(집으면 소비).

import sys, os, re, json, glob, datetime

BASE = os.path.expanduser("~/.claude/manner")
HEAD_LEN = 160
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


def session_short(sid):
    return re.sub(r"[^A-Za-z0-9_-]", "", str(sid))[:12] or "nosession"


def main():
    data = read_stdin_json()
    sid = data.get("session_id") or "nosession"
    msg = data.get("last_assistant_message") or ""
    if not msg:
        return

    head = clean(re.sub(r"\s+", " ", msg).strip()[:HEAD_LEN])
    os.makedirs(BASE, exist_ok=True)

    now = datetime.datetime.now().timestamp()
    for path in glob.glob(os.path.join(BASE, ".baton-*.json")):
        try:
            if now - os.path.getmtime(path) > BATON_MAX_AGE:
                os.remove(path)
        except OSError:
            pass

    baton = os.path.join(BASE, f".baton-{session_short(sid)}.json")
    try:
        with open(baton, "w", encoding="utf-8") as f:
            json.dump({"ts": datetime.datetime.now().isoformat(), "head": head}, f, ensure_ascii=False)
    except OSError:
        pass


if __name__ == "__main__":
    main()
