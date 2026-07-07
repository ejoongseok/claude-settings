#!/usr/bin/env bash
# prose-lint.sh 산문 표기 검출기 (보고 전용, 수정하지 않음)
#
# 사용: bash prose-lint.sh <파일이나 디렉터리>...
#   디렉터리를 주면 하위 *.md 전부를 검사한다. 파일을 직접 주면 확장자 무관 검사한다.
#
# 검출 범주: 특수기호, 특수 번호기호(원문자류), 프로즈 속 ASCII 화살표, "박다" 표현, 한자, 이모지
# 제외: 코드 펜스 내부, 인라인 코드. blockquote 줄은 검출하되 "인용 가능성" 표시를 붙인다.
#
# 판단(원문 인용 보존, 규칙이 금지 대상을 예시로 인용한 줄)은 이 스크립트가 하지 않는다.
# 보고를 보고 사람이나 윤문 에이전트(proofreader)가 판단한다.
#
# 종료코드: 발견 있으면 1, 없으면 0, 사용법 오류 2.
set -uo pipefail
[ $# -ge 1 ] || { echo "사용법: bash prose-lint.sh <파일|디렉터리>..."; exit 2; }
python - "$@" <<'PY'
import sys, os, re, glob

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

CATS = [
    ("기호",       re.compile(r'[—–→←↔⇒★☆▶▸※§·ㆍ•]')),
    ("번호기호",   re.compile(r'[①-⒇㉠-㉾Ⅰ-ⅿ]')),
    ("ASCII화살표", re.compile(r'(?<![-\w/<])(->|=>)(?![\w>])')),
    ("박다표현",   re.compile(r'박제|박[다아어혀힌힘]')),
    ("비격식",     re.compile(r'죽었|죽는다|뻗는다|뻗었|터진다|터졌|깨졌|깨진다|날아갔|꼬였|꼬인다|튀었|튄다|쏜다|쏘는|쏴서|먹힌|먹혔|먹히|씹힌|씹혔|찍는다|찍었|말이 안\s?[되된]')),   # 대표 패턴만. 열린 범주라 목록 밖 구어체는 판단 주체(에이전트, 사람) 몫
    ("한자",       re.compile(r'[一-鿿]')),
    ("모호어",     re.compile(r'대략|몇몇|몇 ?[개건차명곳]|여러 ?[개건곳]|다수(?!결)|수차례|조만간|최근(?! ?\d)|상당히')),   # 정량화 후보 탐지. "최근 2주"처럼 수치가 붙으면 제외. 오탐 많은 범주라 반드시 판단 후 처리
    ("이모지",     re.compile(r'[\U0001F300-\U0001FAFF✅❌❗⚠⭐]')),
]

INLINE_CODE = re.compile(r'`[^`]*`')

def targets(arg):
    if os.path.isdir(arg):
        return sorted(glob.glob(os.path.join(arg, '**', '*.md'), recursive=True))
    return [arg]

findings = []          # (path, lineno, cat, excerpt, in_quote)
counts = {}

for arg in sys.argv[1:]:
    for path in targets(arg):
        if not os.path.isfile(path):
            print(f"[warn] 파일 아님: {path}")
            continue
        try:
            lines = open(path, encoding='utf-8', errors='replace').read().splitlines()
        except OSError as e:
            print(f"[warn] 읽기 실패: {path} ({e})")
            continue
        in_fence = False
        for i, raw in enumerate(lines, 1):
            stripped = raw.lstrip()
            if stripped.startswith('```') or stripped.startswith('~~~'):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            line = INLINE_CODE.sub('', raw)
            in_quote = stripped.startswith('>')
            for cat, rx in CATS:
                if rx.search(line):
                    excerpt = raw.strip()
                    if len(excerpt) > 90:
                        excerpt = excerpt[:90] + '...'
                    findings.append((path, i, cat, excerpt, in_quote))
                    counts[cat] = counts.get(cat, 0) + 1

if not findings:
    print("발견 없음 (0건)")
    sys.exit(0)

for path, lineno, cat, excerpt, in_quote in findings:
    tag = "  (blockquote, 인용 가능성)" if in_quote else ""
    print(f"{path}:{lineno}: [{cat}] {excerpt}{tag}")

print()
print("범주별 합계: " + ", ".join(f"{c} {n}건" for c, n in sorted(counts.items())) + f" / 총 {len(findings)}건")
print("주의: 코드 펜스와 인라인 코드는 제외됨. 인용과 규칙 예시(금지 대상을 보여주는 줄)는 정당할 수 있으니 판단 후 처리.")
sys.exit(1)
PY
