---
created: 2026-06-01 14:30
category: handover
work_type: debug
project: shop-api
type: session-handover
retention: 14d
topic: order-api-intermittent-500
valid_until: 2026-06-15
model: large-context
source_session_branch: fix/order-api-500
source_session_last_commit: a1b2c3d
edge_cases_detected: ["#2"]
---

# 인계: debug/order-api-intermittent-500

> 이 파일은 `/session-handoff`가 생성하는 인계 문서의 **예시**다 (일반 가상 도메인 — 주문 API). 실제 자격증명·내부 정보 없음. 양식의 SSoT는 `SKILL.md`의 §템플릿이며, 이 예시를 양식 표준으로 삼지 않는다.

## 다음 세션 모델 지침

read 후 순차 수행:
1. frontmatter `work_type` (debug) + `edge_cases_detected` (#2 dirty git) 분기 식별
2. § "진입 read 의무" 모든 절대 경로 read (병렬 가능)
3. § "환경 상태" 미커밋 변경 + 중단된 부하 테스트 재연결 확인
4. § "stale 검증" 자가 점검 1회
5. § "다음 액션 우선순위" 1번(잔여 가설 H3 검증) 진입
6. 발견/정정/결정 표 = raw 기록 (재실행 X)

## 진입 read 의무

| # | type | 절대 경로 | 식별 채널 | 목적 |
|:---:|---|---|:---:|---|
| 1 | code-ref | src/main/java/com/shop/order/OrderService.java:142 | A | 주문 생성 트랜잭션 진입점 — 커넥션 점유 구간 |
| 2 | code-ref | src/main/resources/application.yml:23 | A | 커넥션 풀 max-pool-size=10 (의심 지점) |
| 3 | session-output | .claude/handoff/debug-2026-06-01-1430-order-api-intermittent-500.md | A | 본 문서 |
| 4 | external | logs/order-api-2026-06-01.log | A/B | 500 발생 시각·스택 raw |

식별 채널: A=본 대화 직접 read / B=사용자 명시 / C=메모리 인덱스 grep.

## 본 세션 raw 컨텍스트

### git 상태

```
## fix/order-api-500
 M src/main/java/com/shop/order/OrderService.java
 M src/main/resources/application.yml
?? scripts/load-test-order.sh
```

미커밋 3건 — OrderService 타임아웃 로깅 추가 + 풀 size 실험값(10→20) + 부하 테스트 스크립트(신규, untracked).

### 변경 / 신규 파일

| 경로 | 작업 | git 추적 |
|---|---|---|
| src/main/java/com/shop/order/OrderService.java | 타임아웃 로깅 추가 (실험) | tracked |
| src/main/resources/application.yml | max-pool-size 10→20 (실험, 커밋 보류) | tracked |
| scripts/load-test-order.sh | 동시 100 요청 재현 스크립트 (신규) | untracked |

### 정량 지표

| 지표 | 값 | 비고 |
|---|---|---|
| 재현 시도 | 7회 | 동시 50 이상에서 재현, 10에서는 미재현 |
| 가설 — 배제 | 2 (H1 DB 데드락 / H2 외부 결제 게이트웨이 타임아웃) | |
| 가설 — 잔여 | 1 (H3 커넥션 풀 고갈) | |
| 진단 도구 | 3 (스레드 덤프 / 풀 메트릭 / 부하 스크립트) | |
| 검증 | [미측정] | H3 확정 검증 미완 (다음 액션) |

### 발견 / 단정 정정

| # | 발견 / 단정 | 정정 / 검증 |
|:---:|---|---|
| 1 | 초기 단정 "DB 데드락" | 정정 — 데드락 로그 0건. 스레드 덤프상 다수 스레드가 `getConnection` 대기 → 풀 고갈(H3)로 방향 전환 |
| 2 | 500은 결제 게이트웨이 타임아웃 | 배제 — 결제 응답 정상(p99 220ms). 500은 결제 호출 이전 단계에서 발생 |

### 자가 점검 게이트 (재현 명령)

```bash
# 동시 100 요청 — 50+ 에서 500 재현
bash scripts/load-test-order.sh --concurrency 100 --requests 1000
```

## 환경 상태

| 항목 | 값 |
|---|---|
| 중단된 작업 | 부하 테스트 중단 (concurrency 100 실행 중 세션 종료) |
| DB 쓰기 | 없음 (조회·재현만, 롤백됨) |
| 미커밋 | application.yml 풀 size 실험값 20 (커밋 보류 — H3 검증 후 결정) |
| 로그 자격증명 | application.yml DB URL에 평문 비밀번호 노출 → 본 문서·로그 인용 시 `[REDACTED-PWD]` 처리 |

## 다음 액션 우선순위

### 1. H3(풀 고갈) 확정 검증 (★★★)

| 항목 | 값 |
|---|---|
| 진입 path | scripts/load-test-order.sh 실행 + 풀 대기·활성 커넥션 메트릭 관찰 |
| 가치 | ★★★ |
| 부작용 | 없음 (로컬 부하만, DB 롤백) |
| 예상 소요 | 30분 |
| 관련 참조 | § "진입 read 의무" #2 |

### 2. 수정 방향 결정 (★★)

풀 size 상향(임시) vs 트랜잭션 구간 단축(근본). H3 확정 후 § 사용자 트리거 대기 참조.

## stale 검증 (재진입 시 1회)

| 항목 | 검증 명령 | 갱신 가능성 |
|---|---|---|
| git HEAD | `git log -1 --format=%H` ≠ a1b2c3d → 진행됨 | high |
| 미커밋 상태 | `git status --porcelain` 변동 | high |
| 로그 파일 | logs/ 회전 시 당일 로그 소실 가능 | medium |

## 작업 유형별 추가 raw

### [debug 시]

| 필드 | 값 |
|---|---|
| 재현 단계 | `load-test-order.sh --concurrency 100`, 50+ 에서 500 |
| 배제 가설 | H1 DB 데드락 / H2 결제 게이트웨이 타임아웃 |
| 잔여 가설 | H3 커넥션 풀 고갈 |
| 다음 검증 | 풀 대기 메트릭 + size 20 대조 |

## 사용자 트리거 대기 (모델 단독 진입 불가)

| # | 대기 항목 | 사용자 액션 | 비고 |
|:---:|---|---|---|
| 1 | 수정 방향 (임시 상향 vs 근본 단축) | 방향 선택 | 운영 영향도 판단 필요 |
