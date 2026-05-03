"""스캔 PDF -> 텍스트 추출 (OCR) 스크립트.

Usage: py ocr_pdf.py <input.pdf> <output.md>

kordoc이 빈 텍스트를 반환하는 스캔 PDF(이미지 PDF)에 사용.
Tesseract OCR + pdf2image(Poppler) 필요.
"""
import os
import sys

try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    print("필요 패키지: py -m pip install pytesseract pdf2image")
    sys.exit(1)

# Windows Tesseract 기본 경로
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def ocr_pdf(input_path, output_path):
    try:
        images = convert_from_path(input_path, dpi=300)
    except Exception as e:
        print(f"PDF 이미지 변환 실패: {e}")
        print("Poppler가 설치되어 있는지 확인하세요: winget install poppler")
        sys.exit(1)

    md_lines = []
    for i, image in enumerate(images, 1):
        md_lines.append(f"## Page {i}")
        md_lines.append("")
        text = pytesseract.image_to_string(image, lang="kor+eng")
        md_lines.append(text.strip())
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"OCR completed: {input_path} -> {output_path} ({len(images)} pages)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py ocr_pdf.py <input.pdf> <output.md>")
        sys.exit(1)
    ocr_pdf(sys.argv[1], sys.argv[2])
