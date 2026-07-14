# 표현 린트 훅 (hooks/)

`style_lint.py`는 Write와 Edit로 저장되는 파일의 **새로 쓰인 텍스트**를 표현 규칙으로 검사하는 PostToolUse 훅이다. 기준과 대체 표는 `../rules/expression.md` 한 곳에 둔다. 경고 모드라 저장을 막지 않고, 위반 의심을 stderr로 돌려주어 Claude의 자가 수정을 유도한다. 신규 md의 frontmatter 부재도 검출한다(README, INDEX, MEMORY 같은 관례 파일은 제외).

## 설치

1. `style_lint.py`를 `~/.claude/hooks/`에, `../rules/expression.md`를 `~/.claude/rules/`에 복사
2. `~/.claude/settings.json`에 등록:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "python ~/.claude/hooks/style_lint.py" }
        ]
      }
    ]
  }
}
```

3. 훅 설정은 세션 시작 시 로드되므로 등록 후 새 세션부터 발효

## 프로젝트 단위로 끄기

저장소 루트(또는 상위 경로)에 `.style-lint-off` 파일을 두면 그 저장소 전체를 건너뛴다. 원문 문체 보존이 우선인 코퍼스 저장소 같은 곳에 쓴다.

## 검거 로그 (rule-hits.jsonl)

위반 검거는 stderr 경고와 별개로 `~/.claude/calibration/rule-hits.jsonl`에 한 건당 한 줄(JSON)로 누적된다. 필드는 ts, hook, rule, target, line. 어떤 표현 규칙이 실제로 자주 걸리는지 월 1회 캘리브레이션 채점 때 집계하는 용도다(집계 취지는 `../calibration/principles-check.md`의 관측 한계 절에 있다). 디렉터리가 없으면 자동 생성하며, 기록에 실패해도 린트 경고는 정상 동작한다. 누적이 필요 없으면 main() 안의 log_hits 호출 한 줄을 지우면 된다.

## 미포함 훅

로컬에서 함께 쓰는 git 정책 훅(커밋과 푸시 차단)은 환경 종속 설정이라 반출하지 않는다. 취지는 CLAUDE(GLOBAL).md 도구 제약 절에 서술되어 있다.
