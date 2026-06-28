---
name: parse-doc
description: 문서 파일(HWP, HWPX, PDF, XLSX, DOCX, PPTX, PPT, XLS, DOC, ODF)을 Markdown으로 변환합니다. 스캔 PDF는 OCR 자동 실행, 이미지는 Claude 멀티모달로 해석합니다.
disable-model-invocation: true
allowed-tools: Read, Write, Bash, Glob
---

## 역할

`.local.claude/docs/original/`에 있는 문서를 Markdown으로 변환하여 `.local.claude/docs/parsed/`에 저장한다.
내부적으로 kordoc(HWP/HWPX/PDF/XLSX/DOCX)과 python-pptx(PPTX/PPT)를 사용하지만, 사용자는 파일 확장자만 신경 쓰면 된다.

## 외부 데이터 의존

| 데이터 | 경로 | 필수/선택 | 부재 시 동작 |
|--------|------|:------:|------------|
| 프로젝트 컨텍스트 | `CLAUDE.md` | 선택 | 일반 가정으로 진행, `[프로젝트 규칙 미확인]` 태그 |
| 봇 인덱스 | `bot/INDEX.md` 또는 `.local.claude/ONBOARDING.md` | 선택 | 디렉터리 Glob 으로 fallback |
| 비즈니스 규칙 | `.local.claude/biz-rules.md` | 선택 | 일반 SW 관점으로만 진행 (Tier 1) |
| 모듈 상세 | `.local.claude/modules/{name}.md` | 선택 | 코드 Grep 직접 fallback |
| 원본 디렉터리 | `.local.claude/docs/original/` | **필수** | "원본 없음 — `original/` 에 파일 배치 후 재시도" 안내 후 종료 |
| 파서 도구 | `pptx2md.py`, `pdf_images.py`, Tesseract | 선택 | 미설치 시 "미지원" + 설치 가이드 제공 |
| OCR 언어팩 | Tesseract `kor` / `eng` 팩 | 선택 | 미설치 시 OCR 생략 — 이미지 텍스트 인식 불가 |

## 다른 스킬과의 경계

| 질문 | 담당 | 이 스킬에서 |
|------|------|-----------|
| "바이너리·외부 문서(HWP/PDF/XLSX 등)를 Markdown 으로 변환" | **이 스킬** | ✓ 핵심 (포맷 변환까지) |
| "변환된 문서에서 지식 추출·지식 베이스 반영" | /absorb | 다루지 않음 (parse-doc 산출물을 absorb 입력으로 사용) |
| "parsed/ 누적 문서 흡수 확인·아카이브·만료 관리" | /garden | 다루지 않음 (수명 관리는 garden) |
| "사람용·AI용 이중 문서 분리·재구성" | /dualize-docs | 다루지 않음 (이 스킬은 원본→Markdown 변환만) |

## 디렉터리 구조

```
.local.claude/docs/
├── original/    ← 원본 파일을 여기에 놓기
└── parsed/      ← 파싱된 Markdown 출력
```

## 사용법

| 입력 | 동작 |
|------|------|
| `/parse-doc 파일명.hwp` | original/ 내 해당 파일을 파싱 |
| `/parse-doc 파일명.pptx` | 동일 |
| `/parse-doc *.pdf` | original/ 내 모든 PDF 파싱 |
| `/parse-doc` (인자 없음) | original/ 내 미파싱 파일 전체 자동 파싱 |
| `/parse-doc list` | original/과 parsed/ 현황 표시 |

## 동작

> **[1M 활용]** 다음을 **단일 메시지에서 병렬로 호출**:
> - Bash 병렬: `ls .local.claude/docs/original/`, `ls .local.claude/docs/parsed/`, `which tesseract` / `which npx` / `py --version` 등 파서 도구 가용성 확인, 각 파일 확장자별 파싱 명령(kordoc / pptx2md / officeparser) 을 여러 파일에 대해 동시 실행
> - Read: 이미 파싱된 `.local.claude/docs/parsed/*.md` 목록을 병렬로 확인(스킵 판단)
> - Glob: 인자가 패턴(`*.pdf` 등)일 때 원본 디렉터리에서 병렬 매칭

### 1. 파일 확인

```bash
ls .local.claude/docs/original/
```

인자가 있으면 해당 파일만, 없으면 전체 파일 대상.

### 2. 라우팅 (확장자 기반)

| 확장자 | 파서 | 명령어 |
|--------|------|--------|
| `.hwp` | kordoc | `npx kordoc "{파일}" -o "{출력}.md" --silent` |
| `.hwpx` | kordoc | 동일 |
| `.pdf` | kordoc | 동일 |
| `.xlsx` | kordoc | 동일 |
| `.docx` | kordoc | 동일 |
| `.pptx` | python-pptx | `py .claude/skills/parse-doc/pptx2md.py "{파일}" "{출력}.md"` |
| `.xls` | xlrd | `py .claude/skills/parse-doc/xls2md.py "{파일}" "{출력}.md"` |
| `.ppt` | officeParser | `npx officeparser "{파일}" --toText=true > "{출력}.md"` |
| `.doc` | officeParser | 동일 |
| `.odt/.odp/.ods` | officeParser | 동일 |

출력 파일명: 원본 파일명에서 확장자만 `.md`로 변경.
예: `회의록.hwp` → `회의록.md`

### 3. 파싱 실행

각 파일에 대해:

```bash
# 파일 존재 확인
FILE=".local.claude/docs/original/{파일명}"
if [ ! -f "$FILE" ]; then
    echo "파일을 찾을 수 없습니다: $FILE"
    exit 1
fi

# 확장자 추출
EXT="${FILE##*.}"
BASENAME=$(basename "$FILE" ".$EXT")
OUTPUT=".local.claude/docs/parsed/${BASENAME}.md"

# 이미 파싱된 파일은 스킵 (강제 재파싱은 --force)
if [ -f "$OUTPUT" ]; then
    echo "이미 파싱됨: $OUTPUT (재파싱하려면 삭제 후 재실행)"
fi

# 확장자별 라우팅
case "$EXT" in
    hwp|hwpx|xlsx|docx)
        npx kordoc "$FILE" -o "$OUTPUT" --silent
        ;;
    pdf)
        npx kordoc "$FILE" -o "$OUTPUT" --silent
        # 스캔 PDF 감지: kordoc 결과가 빈 텍스트면 OCR 시도
        if [ ! -s "$OUTPUT" ] || [ "$(wc -c < "$OUTPUT")" -lt 50 ]; then
            echo "[WARN] 텍스트가 거의 없음 — 스캔 PDF로 판단, OCR 시도..."
            py .claude/skills/parse-doc/ocr_pdf.py "$FILE" "$OUTPUT"
        fi
        # PDF 이미지 추출 (텍스트 파싱과 별도)
        py .claude/skills/parse-doc/pdf_images.py "$FILE" ".local.claude/docs/parsed/images"
        ;;
    pptx)
        py .claude/skills/parse-doc/pptx2md.py "$FILE" "$OUTPUT"
        ;;
    xls)
        py .claude/skills/parse-doc/xls2md.py "$FILE" "$OUTPUT"
        ;;
    ppt|doc|odt|odp|ods)
        npx officeparser "$FILE" --toText=true > "$OUTPUT"
        ;;
    txt|csv|json|xml|md)
        echo "텍스트 파일 — Read 도구로 직접 읽기 가능. 파싱 불필요."
        ;;
    png|jpg|jpeg|gif|bmp|tiff)
        echo "이미지 파일 — Read 도구로 읽으면 Claude 멀티모달로 해석 가능."
        ;;
    *)
        echo "미지원: .$EXT"
        ;;
esac
```

### 4. 미지원/실패 시 대응

파싱 불가능하거나 실패한 파일이 있으면, **왜 안 되는지** + **대안 2가지**(변환/라이브러리 설치)를 안내한다.

#### 미지원 확장자

| 확장자 | 상태 | 비고 |
|--------|:----:|------|
| `.ppt` | [OK] 지원 | officeParser (텍스트 추출 수준) |
| `.doc` | [OK] 지원 | officeParser |
| `.xls` | [OK] 지원 | xlrd → Markdown 테이블 변환 |
| `.odt/.odp/.ods` | [OK] 지원 | officeParser |
| `.txt/.csv/.json/.xml` | 파싱 불필요 | Read 도구로 직접 읽기 안내 |
| 이미지(`.png/.jpg`) | 파싱 불필요 | Read 도구로 읽으면 Claude 멀티모달 해석 안내 |

#### 파싱 실패

| 실패 원인 | 증상 | 대안 1: 변환 | 대안 2: 라이브러리 |
|----------|------|------------|------------------|
| 암호화된 HWP | kordoc 에러 또는 빈 출력 | 암호 해제 후 재저장 | kordoc 배포용 복호화 시도 — 실패 시 원본 작성자에게 요청 |
| 스캔 PDF (이미지 PDF) | 빈 문자열 또는 깨진 텍스트 | Adobe Acrobat에서 OCR 적용 후 재저장 | 아래 Tesseract 설치 가이드 참조 |
| 대용량 PDF (100MB+) | 타임아웃 | 페이지 분할: `npx kordoc 파일.pdf --pages 1-20` | — |
| PPTX 차트/SmartArt | 해당 요소만 텍스트 미추출 | — | 차트는 이미지로 추출되므로 Claude 멀티모달 해석으로 대체 |
| HWP/HWPX 이미지 | kordoc이 이미지 미추출 | HWP를 PDF로 변환 후 pdf_images.py로 추출 | 한컴오피스에서 PDF로 내보내기 → kordoc(텍스트) + pdf_images.py(이미지) |

#### Tesseract OCR 설치 가이드 (스캔 PDF/이미지 문서용)

스캔 PDF나 이미지 파일의 텍스트 추출이 필요할 때:
1. Tesseract 설치: `winget install UB-Mannheim.TesseractOCR`
2. 한국어 데이터: 설치 시 Korean 체크 또는 `tessdata/kor.traineddata` 수동 추가
3. Poppler 설치 (pdf2image용): `winget install poppler` 또는 GitHub에서 다운로드 후 PATH 추가
4. Python 패키지: `py -m pip install pytesseract pdf2image` (이미 설치됨)
5. 설치 후 이 스킬의 라우팅 테이블에 스캔 PDF 분기 추가 가능

대안 2(라이브러리)를 사용자가 선택하면, 설치 명령을 안내하고 스킬 라우팅 테이블에 추가할지 제안한다.

### 5. 이미지 해석

#### 이미지 추출

| 포맷 | 추출 도구 | 실행 |
|------|----------|------|
| PPTX | pptx2md.py (python-pptx) | 텍스트 파싱과 동시에 자동 추출 |
| PDF | pdf_images.py (PyMuPDF) | kordoc 파싱 후 별도 실행: `py .claude/skills/parse-doc/pdf_images.py "{파일}" ".local.claude/docs/parsed/images"` |
| HWP/HWPX | — | 현재 추출 도구 없음 — 미지원 |

PDF 이미지 추출 시 5KB 미만 소형 이미지(아이콘, 장식)는 자동 스킵.

#### 해석 흐름 (PPTX/PDF 공통)

파싱 완료 후 `parsed/images/`에 이미지가 있으면:
1. 추출된 이미지 파일 목록 표시
2. 각 이미지를 **Read 도구로 읽어** Claude 멀티모달로 해석
3. 해석 결과를 Markdown 파일에 텍스트 설명으로 삽입
4. 원본 이미지 참조는 유지하고, 바로 아래에 설명 추가

```markdown
![이미지](images/발표자료_slide3_img1.png)

> **[이미지 해석]** 시스템 아키텍처 다이어그램. 클라이언트 → API Gateway → 마이크로서비스 3개(인증, 주문, 재고) → PostgreSQL DB 구조.
```

### 6. 결과 보고

파싱 완료 후:
```
파싱 완료:
| 파일 | 파서 | 결과 | 크기 |
|------|------|------|------|
| 회의록.hwp | kordoc | [OK] 회의록.md | 2.3KB |
| 발표자료.pptx | officeParser | [OK] 발표자료.md | 5.1KB |

파싱된 파일은 `.local.claude/docs/parsed/`에 저장되었습니다.
내용을 확인하려면 Read로 직접 읽으세요.
```

### 6. list 모드

```bash
echo "=== original/ ==="
ls -la .local.claude/docs/original/

echo "=== parsed/ ==="
ls -la .local.claude/docs/parsed/
```

미파싱 파일 표시:
```
| 원본 파일 | 파싱 상태 |
|----------|----------|
| 회의록.hwp | [OK] parsed/회의록.md |
| 발표자료.pptx | [FAIL] 미파싱 |
```

## 인자 없이 호출 시

original/ 디렉터리의 모든 파일을 스캔하여:
1. parsed/에 대응 .md가 없는 파일만 파싱
2. 이미 파싱된 파일은 스킵
3. 결과 요약 보고

## 다음 스킬 연결

파싱 완료 후, 문서 성격에 따라 다음 작업을 안내한다:

| 문서 성격 | 판단 기준 (파일명/내용 키워드) | 안내 |
|----------|--------------------------|------|
| 요구사항/RFP/제안요청 | "요구", "RFP", "제안", "사양", "규격" | → `/daily-todos`에 할 일 추출, 또는 `.local.claude/projects/`에 PRD 초안 생성 |
| 회의록/미팅노트 | "회의", "미팅", "minutes", "논의" | → 요약 + 액션 아이템 추출을 제안 |
| 규격서/기술문서 | "spec", "규격", "표준", "기술" | → `/biz-rules`에 관련 규칙 추출 반영 검토 |
| 고객사 자료 | 고객사명 (`.local.claude/customers/` 파일명 매칭) | → `.local.claude/customers/{고객사}.md` 업데이트 검토 |
| 기타 | — | → "파싱 완료. 이 문서로 무엇을 하시겠습니까?" |

안내는 **제안만** 한다. 자동 실행하지 않음.

## 분량 임계

| 산출물 | 임계 1 (알림) | 임계 2 (분리) |
|--------|:----------:|:----------:|
| `parsed/{file}.md` (변환 결과) | 500줄 | 원본 페이지·시트·섹션 단위로 분할 출력 (예: `{file}-part1.md`) |
| `parsed/images/` 누적 | 50개 | 문서별 하위 디렉터리(`parsed/images/{문서명}/`)로 그룹화 |

parsed/ 산출물은 즉시 자동 로드 대상이 아니므로(`@` 미사용) 임계는 가독성·후속 흡수 효율 기준. 대용량 PDF(100MB+ / 200페이지+)는 `pages` 분할로 변환 자체를 나눈다 (검증 시나리오 참조). 누적 정리·아카이브는 `/garden` 위임.

## 제약조건

- 원본 파일은 반드시 `.local.claude/docs/original/`에 위치해야 함
- 파싱 결과는 Markdown (텍스트 + 테이블)
- PPTX 이미지: pptx2md.py가 자동 추출 → Claude 멀티모달로 해석 → 텍스트 설명 삽입
- PDF 이미지: pdf_images.py(PyMuPDF)로 추출 → 동일하게 해석
- HWP/HWPX 이미지: 현재 추출 도구 없음 — 미지원
- .ppt(구형 PowerPoint 97-2003)는 미지원 — .pptx로 변환 후 사용
- 대용량 파일(100MB+)은 시간이 걸릴 수 있음
- 암호화된 HWP/배포용 HWP는 kordoc이 복호화 시도하지만 실패할 수 있음

## 검증 시나리오

공통 3블록(빈 / 부분 / 풀 데이터)은 **CONTRACT §6-1** 참조.

### 이 스킬의 고유 실패 시나리오

**[의존성 부재]** Tesseract / pptx2md / 기타 변환 도구 미설치
- 신호: `which tesseract` / `pptx2md --version` 실패
- 대응: 설치 가이드 제시 후 중단 (사용자가 설치 완료 시 재실행)

**[환경·규모]** PDF 200페이지 이상
- 신호: 페이지 수 200+ 감지
- 대응: `pages` 파라미터 분할 권장 + timeout 경고 표시, 부분 처리 후 병합 전략 안내
