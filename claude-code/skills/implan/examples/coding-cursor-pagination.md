---
created: 2026-07-03
category: implementation-plan
mode: coding
size: 1시간
session_continuity: off
retention: until-built
---

> 이 파일은 `/implan`이 생성하는 구현 플랜의 **예시**다(가상 도메인, 주문 API). 회사와 내부 정보 없음. 양식의 SSoT는 `SKILL.md`의 "플랜 출력 템플릿" 섹션이며, 이 예시의 분량과 풍부도를 양식 표준으로 삼지 않는다(SKILL.md 제약 조항의 "특정 사례 일반화 금지").

# 주문 목록 API 커서 페이지네이션 구현 플랜

## 판정 기록

| 판정 | 값 | 근거 |
|---|---|---|
| 모드 | coding | 코드 파일(Repository, Service, Controller, DTO) 생성과 수정 포함 |
| 크기 | 1시간 | 산출물 6개(수정 3, 신규 3), 의존 단계 4(Cursor 다음 Repository 다음 Service 다음 Controller). 기준표의 1시간 구간(산출물 3~8개, 의존 단계 3~5) |
| 세션연속성 | off | 크기 1시간, 실행이 당일 한 세션 내 완료. 달력 경계 없음 |
| 산출 위치 | .claude/plans/order-cursor-pagination/ | 산출 위치 규칙 1(docs/plans/ 없음, .claude/plans/ 생성) |
| 페이지네이션 방식 | 커서 | 논의 합의: offset은 깊은 페이지(10,000+)에서 성능 저하가 있고 목록 갱신 중 중복과 누락이 발생. 커서는 정렬키 기준으로 안정 |
| 커서 인코딩 | opaque base64url(JSON) | 논의 합의: 내부 정렬키 노출 차단, 향후 정렬키 변경 시 클라이언트 영향 격리 |
| 첫 페이지 조회 | `findFirstPage` 별도 메서드 | sentinel 값 주입 방식은 호출부가 가짜 기준값을 만들어야 해 오용 여지가 있음. 별도 메서드가 의도가 드러나고 쿼리 인덱스 활용은 동일 |
| 기본/최대 페이지 크기 | 20 / 100 | 기존 offset API 기본값 20과 일치(OrderController.java:41 실측). 클라이언트 마이그레이션 비용 0 |
| 기존 offset API | 유지(dual) | 논의 합의: 호환 위해 1개 분기 병행 운용 후 deprecate 예고(별도 작업) |

## 컨텍스트

- 문제(What): 주문 목록 offset 페이지네이션이 깊은 페이지에서 응답 지연을 일으키고, 목록 갱신 중 같은 주문이 중복 노출된다
- 합의: 커서 기반 신규 엔드포인트 추가. 기존 offset API는 1개 분기 동안 병행 유지 후 deprecate
- 전제: 정렬 기준 `created_at DESC, id DESC`(고유 복합키), 인덱스 `(created_at, id)` 기존 존재(스키마 실측)
- 미해소 질문: 없음

## 변경 대상

| # | 파일(전체 경로) | 작업 | 핵심 시그니처 |
|---|---|---|---|
| 1 | src/main/java/com/shop/order/Cursor.java | 신규 | `encode()` / `decode(String)` opaque base64url |
| 2 | src/main/java/com/shop/order/OrderRepository.java | 수정 | `findFirstPage(int limit)` / `findAfter(Instant createdAt, long id, int limit)` |
| 3 | src/main/java/com/shop/order/OrderService.java | 수정 | `OrderPageResponse listByCursor(Cursor c, int size)` |
| 4 | src/main/java/com/shop/order/OrderController.java | 수정 | `getOrders(String cursor, int size)` |
| 5 | src/main/java/com/shop/order/dto/OrderPageResponse.java | 신규 | `items[]`, `nextCursor`, `hasNext` |
| 6 | src/test/java/com/shop/order/CursorTest.java | 신규 | 인코딩 왕복과 깨진 입력 테스트 |

## 실행 단계

### 1. Cursor 인코딩 유틸
- 대상: Cursor.java (신규)
- 동작: `{createdAt, id}`를 JSON으로 만든 뒤 base64url로 인코딩/디코딩. 디코딩 실패 시 400(잘못된 커서) 예외를 던진다.
- 완료 검증: CursorTest에서 인코딩 후 디코딩 왕복 동치, 그리고 깨진 문자열 입력 시 예외 발생.

### 2. Repository 커서 쿼리
- 대상: OrderRepository의 `findFirstPage`, `findAfter` (신규 메서드 2개)
- 동작: `findFirstPage(limit)`는 `ORDER BY created_at DESC, id DESC LIMIT :limit`. `findAfter(createdAt, id, limit)`는 같은 정렬에 `WHERE (created_at, id) < (:createdAt, :id)` 조건 추가. 두 메서드 모두 호출부가 limit을 size+1로 넘겨 hasNext 판정용 1건 여분을 확보한다.
- 컨벤션: 기존 Repository 쿼리 스타일을 따른다(프로젝트 rules 참조)
- 완료 검증: limit=21로 호출 시 두 메서드 모두 최대 21건 반환. `findAfter`는 기준 행보다 뒤의 행만 반환.

### 3. Service 조립
- 대상: OrderService.listByCursor
- 동작: cursor가 null이면 `findFirstPage(size+1)`, 아니면 디코딩 후 `findAfter(createdAt, id, size+1)` 호출. 결과가 size를 초과하면 여분 1건을 잘라 hasNext=true로 판정하고, 잘라낸 뒤 마지막 항목으로 nextCursor를 생성해 OrderPageResponse로 반환한다.
- 완료 검증: 첫 페이지(cursor=null), 중간 페이지, 마지막 페이지(hasNext=false) 3케이스 통과.

### 4. Controller 엔드포인트
- 대상: OrderController.getOrders
- 동작: `GET /api/orders?cursor=&size=20`. size 범위(1~100)를 검증하고 초과 시 100으로 clamp. nextCursor를 응답 바디로 반환한다.
- 완료 검증: cursor 없이 호출하면 첫 페이지가 오고, 응답의 nextCursor로 재호출하면 다음 페이지가 중복과 누락 0으로 이어진다.

## 안전망

- 기존 offset 엔드포인트 유지. 신규 커서 API와 병행(dual) 운용하므로 롤백은 신규 라우트 제거뿐이고 기존 동작은 무영향.
- `Deprecation` 헤더 예고는 별도 작업(본 플랜 범위 외).

## 자가 점검 결과

- 0-결정: pass (설계 5선택 확정, 미해소 0건, 모호 동사 0건) / 결정성 재현: pass (판정 9건 전부 근거와 출처 명시)
- 게이트 보강: 없음
