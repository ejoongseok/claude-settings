#!/usr/bin/env bash
# Claude Code status line script
#
# 표시 내용 (3행):
#   1행: 모델 | effort | git 브랜치(+staged ~modified) | Claude API 상태
#   2행: 컨텍스트 사용률 바 | 5h 한도 | 7d 한도 | Fable 주간 한도 | 세션 비용
#   3행: 현재 경로 | KST/UTC 시각
#
# 설치:
#   1) 이 파일을 ~/.claude/statusline-command.sh 로 저장
#   2) ~/.claude/settings.json 에 아래 블록 추가:
#        "statusLine": {
#          "type": "command",
#          "command": "bash ~/.claude/statusline-command.sh"
#        }
#   3) Claude Code 재시작
JQ=$(command -v jq 2>/dev/null)
if [ -z "$JQ" ]; then
  JQ=$(ls "$HOME"/AppData/Local/Microsoft/WinGet/Packages/jqlang.jq_*/jq.exe 2>/dev/null | head -1)
fi
if [ -z "$JQ" ]; then
  printf 'statusline: jq not found (winget install jqlang.jq)\n'
  exit 0
fi

# ── ANSI color helpers ──────────────────────────────────────────────────────
orange()  { printf '\033[38;5;208m%s\033[0m' "$1"; }
cyan()    { printf '\033[36m%s\033[0m' "$1"; }
green()   { printf '\033[32m%s\033[0m' "$1"; }
yellow()  { printf '\033[33m%s\033[0m' "$1"; }
red()     { printf '\033[31m%s\033[0m' "$1"; }
dim()     { printf '\033[2m%s\033[0m' "$1"; }

SEP=$(dim " | ")

# ── Parse stdin JSON once ───────────────────────────────────────────────────
INPUT=$(cat)

_jq() { echo "$INPUT" | "$JQ" -r "$1" 2>/dev/null; }

# ── 1. Model name ───────────────────────────────────────────────────────────
MODEL=$(_jq '.model.display_name // .model.id // "claude"')
SECTION_MODEL=$(orange "${MODEL}")

# ── 1b. Effort level (only present when model supports reasoning effort) ────
EFFORT_RAW=$(_jq '.effort.level // empty')
SECTION_EFFORT=""
if [ -n "$EFFORT_RAW" ] && [ "$EFFORT_RAW" != "null" ]; then
  case "$EFFORT_RAW" in
    low)   SECTION_EFFORT=$(dim    "effort:low")   ;;
    medium) SECTION_EFFORT=$(cyan  "effort:med")   ;;
    high)  SECTION_EFFORT=$(yellow "effort:high")  ;;
    xhigh) SECTION_EFFORT=$(orange "effort:xhigh") ;;
    max)   SECTION_EFFORT=$(red    "effort:MAX")   ;;
    *)     SECTION_EFFORT=$(dim    "effort:${EFFORT_RAW}") ;;
  esac
fi

# ── 2. Current folder path ──────────────────────────────────────────────────
CWD=$(_jq '.workspace.current_dir // .cwd // ""')
[ -z "$CWD" ] && CWD=$(pwd)
SECTION_FOLDER=$(dim "${CWD}")

# ── 2b. KST time (Asia/Seoul) + UTC ─────────────────────────────────────────
# Git Bash 는 tzdata 미탑재라 TZ=Asia/Seoul 이 UTC 로 폴백됨 → epoch 직접 가산
KST_EPOCH=$(( $(date -u +%s) + 32400 ))
KST_TIME=$(date -u -d "@${KST_EPOCH}" '+%Y-%m-%d %H:%M' 2>/dev/null)
UTC_TIME=$(date -u '+%Y-%m-%d %H:%M')
SECTION_TIME="$(yellow "${KST_TIME} KST")${SEP}$(dim "${UTC_TIME} UTC")"

# ── 3. Git branch + staged/modified counts (cached 5 s) ────────────────────
CACHE_DIR="${TMPDIR:-/tmp}/claude_statusline"
mkdir -p "$CACHE_DIR"
# Use a checksum of the cwd as the cache key
REPO_HASH=$(echo "$CWD" | cksum | awk '{print $1}')
CACHE_FILE="$CACHE_DIR/git_${REPO_HASH}"
NOW=$(date +%s)

SECTION_GIT=""
USE_CACHE=0
if [ -f "$CACHE_FILE" ]; then
  CACHE_TIME=$(head -1 "$CACHE_FILE" 2>/dev/null)
  if [ -n "$CACHE_TIME" ] && [ $(( NOW - CACHE_TIME )) -lt 5 ]; then
    USE_CACHE=1
  fi
fi

if [ "$USE_CACHE" -eq 1 ]; then
  SECTION_GIT=$(tail -n +2 "$CACHE_FILE" 2>/dev/null)
else
  # Run git in the project dir; skip optional locks to avoid contention
  BRANCH=$(git -C "$CWD" -c gc.auto=0 symbolic-ref --short HEAD 2>/dev/null)
  if [ -n "$BRANCH" ]; then
    STAGED=$(git -C "$CWD" -c gc.auto=0 diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
    MODIFIED=$(git -C "$CWD" -c gc.auto=0 diff --name-only 2>/dev/null | wc -l | tr -d ' ')

    GIT_BRANCH=$(green "$BRANCH")
    GIT_COUNTS=""
    if [ "${STAGED:-0}" -gt 0 ] || [ "${MODIFIED:-0}" -gt 0 ]; then
      GIT_COUNTS=" $(green "+${STAGED:-0}") $(yellow "~${MODIFIED:-0}")"
    fi
    SECTION_GIT="${GIT_BRANCH}${GIT_COUNTS}"
  else
    SECTION_GIT=$(dim "no git")
  fi
  # Write cache: timestamp on line 1, rendered content on line 2+
  { echo "$NOW"; printf '%s' "$SECTION_GIT"; } > "$CACHE_FILE"
fi

# ── 4. Session cost ─────────────────────────────────────────────────────────
# Claude Code가 모델별 단가로 계산한 세션 누적 추정치 (실제 청구액과 다를 수 있음)
COST_USD=$(_jq '.cost.total_cost_usd // 0')
COST_RAW=$(awk -v c="${COST_USD:-0}" 'BEGIN { printf "%.4f", c }')
SECTION_COST=$(dim "\$${COST_RAW}")

# ── 5. Context window usage % + text progress bar ───────────────────────────
USED_PCT=$(_jq '.context_window.used_percentage // empty')

SECTION_CTX=""
if [ -n "$USED_PCT" ] && [ "$USED_PCT" != "null" ]; then
  PCT_INT=$(printf '%.0f' "$USED_PCT")

  # 10-block bar
  FILLED=$(( PCT_INT / 10 ))
  [ "$FILLED" -gt 10 ] && FILLED=10
  BAR=""
  i=0
  while [ "$i" -lt "$FILLED" ]; do BAR="${BAR}█"; i=$(( i + 1 )); done
  while [ "$i" -lt 10 ];        do BAR="${BAR}░"; i=$(( i + 1 )); done

  if   [ "$PCT_INT" -ge 80 ]; then
    SECTION_CTX="$(red   "$BAR") $(red    "${PCT_INT}%")"
  elif [ "$PCT_INT" -ge 50 ]; then
    SECTION_CTX="$(yellow "$BAR") $(yellow "${PCT_INT}%")"
  else
    SECTION_CTX="$(green  "$BAR") $(green  "${PCT_INT}%")"
  fi
else
  SECTION_CTX=$(dim "ctx: --")
fi

# ── 6. Rate limits (5-hour session + 7-day weekly) ─────────────────────────
FIVE_PCT=$(_jq '.rate_limits.five_hour.used_percentage // empty')
FIVE_RESET=$(_jq '.rate_limits.five_hour.resets_at // empty')
SEVEN_PCT=$(_jq '.rate_limits.seven_day.used_percentage // empty')
SEVEN_RESET=$(_jq '.rate_limits.seven_day.resets_at // empty')

SECTION_FIVE_HOUR=""
if [ -n "$FIVE_PCT" ] && [ "$FIVE_PCT" != "null" ]; then
  FIVE_INT=$(printf '%.0f' "$FIVE_PCT")
  # Format reset time as HH:MM
  RESET_STR=""
  if [ -n "$FIVE_RESET" ] && [ "$FIVE_RESET" != "null" ]; then
    RESET_STR=$(date -d "@${FIVE_RESET}" '+%H:%M' 2>/dev/null || date -r "${FIVE_RESET}" '+%H:%M' 2>/dev/null || echo "")
  fi

  if   [ "$FIVE_INT" -ge 80 ]; then FIVE_LABEL=$(red "5h:${FIVE_INT}%")
  elif [ "$FIVE_INT" -ge 50 ]; then FIVE_LABEL=$(yellow "5h:${FIVE_INT}%")
  else                               FIVE_LABEL=$(green "5h:${FIVE_INT}%")
  fi

  if [ -n "$RESET_STR" ]; then
    FIVE_LABEL="${FIVE_LABEL}$(dim "(${RESET_STR})")"
  fi

  SECTION_FIVE_HOUR="$FIVE_LABEL"
fi

SECTION_SEVEN_DAY=""
if [ -n "$SEVEN_PCT" ] && [ "$SEVEN_PCT" != "null" ]; then
  SEVEN_INT=$(printf '%.0f' "$SEVEN_PCT")
  # Format reset time as MM-DD HH:MM (week away — date matters)
  SEVEN_RESET_STR=""
  if [ -n "$SEVEN_RESET" ] && [ "$SEVEN_RESET" != "null" ]; then
    SEVEN_RESET_STR=$(date -d "@${SEVEN_RESET}" '+%m-%d %H:%M' 2>/dev/null || date -r "${SEVEN_RESET}" '+%m-%d %H:%M' 2>/dev/null || echo "")
  fi

  if   [ "$SEVEN_INT" -ge 80 ]; then SEVEN_LABEL=$(red "7d:${SEVEN_INT}%")
  elif [ "$SEVEN_INT" -ge 50 ]; then SEVEN_LABEL=$(yellow "7d:${SEVEN_INT}%")
  else                                SEVEN_LABEL=$(green "7d:${SEVEN_INT}%")
  fi

  if [ -n "$SEVEN_RESET_STR" ]; then
    SEVEN_LABEL="${SEVEN_LABEL}$(dim "(${SEVEN_RESET_STR})")"
  fi

  SECTION_SEVEN_DAY="$SEVEN_LABEL"
fi

# rate limit 없으면 각 섹션은 빈 문자열 유지 (LINE2 조건 분기에서 처리)

# ── Claude API status (status.claude.com, 60s cache, background refresh) ────
CLAUDE_STATUS_CACHE="$CACHE_DIR/claude_api_status"
CLAUDE_STATUS_TTL=60

_fetch_claude_status() {
  STATUS_JSON=$(curl -s --max-time 5 "https://status.claude.com/api/v2/status.json" 2>/dev/null)
  if [ -n "$STATUS_JSON" ]; then
    SI=$(echo "$STATUS_JSON" | "$JQ" -r '.status.indicator // "unknown"')
    case "$SI" in
      none)     NV=$(printf '\033[32m●ok\033[0m') ;;
      minor)    NV=$(printf '\033[33m●minor\033[0m') ;;
      major)    NV=$(printf '\033[31m●major\033[0m') ;;
      critical) NV=$(printf '\033[31m●CRIT\033[0m') ;;
      *)        NV=$(printf '\033[2m●?\033[0m') ;;
    esac
    { echo "$(date +%s)"; printf '%s' "$NV"; } > "$CLAUDE_STATUS_CACHE"
  fi
}

SECTION_CLAUDE_STATUS=$(dim "claude:--")
if [ -f "$CLAUDE_STATUS_CACHE" ]; then
  STATUS_CACHE_TIME=$(head -1 "$CLAUDE_STATUS_CACHE" 2>/dev/null)
  CACHED_VAL=$(tail -n +2 "$CLAUDE_STATUS_CACHE" 2>/dev/null)
  if [ -n "$STATUS_CACHE_TIME" ] && [ $(( NOW - STATUS_CACHE_TIME )) -lt $CLAUDE_STATUS_TTL ]; then
    SECTION_CLAUDE_STATUS="$CACHED_VAL"
  else
    # 캐시 만료 — 이전 값 그대로 표시(~ 표시로 구식임을 표기), 백그라운드에서 갱신
    SECTION_CLAUDE_STATUS="${CACHED_VAL}$(dim "~")"
    ( _fetch_claude_status ) &
  fi
else
  # 캐시 없음 — 백그라운드 첫 fetch, 다음 갱신 시 표시됨
  ( _fetch_claude_status ) &
fi

# ── 6b. Fable 주간 한도 (/api/oauth/usage, 300s 캐시, 백그라운드 갱신) ───────
# stdin rate_limits 에는 모델별 주간 한도가 없어 undocumented usage API 를 사용.
# 본인 계정의 OAuth 토큰(~/.claude/.credentials.json)을 읽어 본인 사용량만 조회.
# 실패해도(토큰 없음/네트워크/스키마 변경) 이 섹션만 조용히 생략 — 나머지 무영향.
FABLE_CACHE="$CACHE_DIR/fable_usage"
FABLE_TTL=300
CRED_FILE="$HOME/.claude/.credentials.json"

_fetch_fable_usage() {
  [ -f "$CRED_FILE" ] || return
  local tok
  tok=$("$JQ" -r '.claudeAiOauth.accessToken // empty' "$CRED_FILE" 2>/dev/null)
  [ -n "$tok" ] || return
  local resp
  resp=$(curl -s --max-time 5 "https://api.anthropic.com/api/oauth/usage" \
    -H "Authorization: Bearer $tok" \
    -H "anthropic-beta: oauth-2025-04-20" 2>/dev/null)
  [ -n "$resp" ] || return
  # Fable = limits[] 중 kind==weekly_scoped 이고 scope.model.display_name=="Fable"
  # 저장 형식: 1행=timestamp, 2행="<percent>\t<resets_at ISO8601>"
  local line
  line=$(echo "$resp" | "$JQ" -r '
    (.limits[]? | select(.kind=="weekly_scoped" and .scope.model.display_name=="Fable"))
    | "\(.percent)\t\(.resets_at)"' 2>/dev/null | head -1)
  [ -n "$line" ] || return
  { echo "$(date +%s)"; printf '%s' "$line"; } > "$FABLE_CACHE"
}

SECTION_FABLE=""
FABLE_LINE=""
if [ -f "$FABLE_CACHE" ]; then
  FABLE_CACHE_TIME=$(head -1 "$FABLE_CACHE" 2>/dev/null)
  FABLE_LINE=$(tail -n +2 "$FABLE_CACHE" 2>/dev/null)
  if [ -z "$FABLE_CACHE_TIME" ] || [ $(( NOW - FABLE_CACHE_TIME )) -ge $FABLE_TTL ]; then
    ( _fetch_fable_usage ) &   # 만료 — 이전 값 표시하고 백그라운드 갱신
  fi
else
  ( _fetch_fable_usage ) &     # 캐시 없음 — 첫 fetch, 다음 렌더부터 표시
fi

if [ -n "$FABLE_LINE" ]; then
  FABLE_PCT=$(printf '%s' "$FABLE_LINE" | cut -f1)
  FABLE_RESET_ISO=$(printf '%s' "$FABLE_LINE" | cut -f2)
  if [ -n "$FABLE_PCT" ] && [ "$FABLE_PCT" != "null" ]; then
    FABLE_INT=$(printf '%.0f' "$FABLE_PCT" 2>/dev/null)
    FABLE_RESET_STR=""
    if [ -n "$FABLE_RESET_ISO" ] && [ "$FABLE_RESET_ISO" != "null" ]; then
      # ISO8601(+00:00) → 로컬 MM-DD HH:MM. 7d 섹션과 동일 형식.
      # TZ 미지정: Git Bash 는 tzdata 미탑재라 TZ 명시 시 UTC 폴백 → 시스템 로컬에 위임.
      FABLE_RESET_STR=$(date -d "$FABLE_RESET_ISO" '+%m-%d %H:%M' 2>/dev/null || echo "")
    fi

    if   [ "$FABLE_INT" -ge 80 ]; then FABLE_LABEL=$(red    "fable:${FABLE_INT}%")
    elif [ "$FABLE_INT" -ge 50 ]; then FABLE_LABEL=$(yellow "fable:${FABLE_INT}%")
    else                               FABLE_LABEL=$(green  "fable:${FABLE_INT}%")
    fi

    if [ -n "$FABLE_RESET_STR" ]; then
      FABLE_LABEL="${FABLE_LABEL}$(dim "(${FABLE_RESET_STR})")"
    fi

    SECTION_FABLE="$FABLE_LABEL"
  fi
fi

# ── Assemble final output (3-line layout) ───────────────────────────────────
# 1행: 모델 | effort(있을 때만) | 브랜치 | API 상태
# 2행: 컨텍스트 | 5h(있을 때만) | 7d(있을 때만) | fable(있을 때만) | 비용
# 3행: 경로 | 시간

LINE1="$SECTION_MODEL"
if [ -n "$SECTION_EFFORT" ]; then
  LINE1="${LINE1}${SEP}${SECTION_EFFORT}"
fi
LINE1="${LINE1}${SEP}${SECTION_GIT}${SEP}${SECTION_CLAUDE_STATUS}"

LINE2="$SECTION_CTX"
if [ -n "$SECTION_FIVE_HOUR" ]; then
  LINE2="${LINE2}${SEP}${SECTION_FIVE_HOUR}"
fi
if [ -n "$SECTION_SEVEN_DAY" ]; then
  LINE2="${LINE2}${SEP}${SECTION_SEVEN_DAY}"
fi
if [ -n "$SECTION_FABLE" ]; then
  LINE2="${LINE2}${SEP}${SECTION_FABLE}"
fi
LINE2="${LINE2}${SEP}${SECTION_COST}"

LINE3="${SECTION_FOLDER}${SEP}${SECTION_TIME}"

printf '%s\n%s\n%s\n' "$LINE1" "$LINE2" "$LINE3"
