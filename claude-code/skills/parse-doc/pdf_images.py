"""PDF에서 이미지를 추출하는 보조 스크립트.

Usage: py pdf_images.py <input.pdf> <images_dir>

kordoc이 텍스트/테이블을 변환한 뒤, 이 스크립트로 이미지만 별도 추출.
추출된 이미지 경로를 stdout에 출력.
"""
import os
import sys
import fitz  # PyMuPDF


def extract_images(pdf_path, images_dir):
    os.makedirs(images_dir, exist_ok=True)
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    doc = fitz.open(pdf_path)
    extracted = []
    img_counter = 0

    for page_num, page in enumerate(doc, 1):
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            if base_image is None:
                continue
            ext = base_image["ext"]
            img_bytes = base_image["image"]
            # 너무 작은 이미지(아이콘 등) 스킵
            if len(img_bytes) < 5000:
                continue
            img_counter += 1
            img_name = f"{basename}_page{page_num}_img{img_counter}.{ext}"
            img_path = os.path.join(images_dir, img_name)
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            extracted.append(img_path)

    doc.close()

    if extracted:
        print(f"Images extracted: {len(extracted)}개 -> {images_dir}/")
        for img in extracted:
            print(f"  - {os.path.basename(img)}")
    else:
        print("No images found.")

    return extracted


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py pdf_images.py <input.pdf> <images_dir>")
        sys.exit(1)
    extract_images(sys.argv[1], sys.argv[2])
