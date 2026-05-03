"""XLS (Excel 97-2003) -> Markdown 변환 스크립트.

Usage: py xls2md.py <input.xls> <output.md>
"""
import sys
import xlrd


def xls_to_md(input_path, output_path):
    wb = xlrd.open_workbook(input_path)
    md_lines = []

    for sheet in wb.sheets():
        md_lines.append(f"## {sheet.name}")
        md_lines.append("")

        if sheet.nrows == 0:
            md_lines.append("(빈 시트)")
            md_lines.append("")
            continue

        for row_idx in range(sheet.nrows):
            cells = []
            for col_idx in range(sheet.ncols):
                cell = sheet.cell(row_idx, col_idx)
                value = str(cell.value).strip()
                if cell.ctype == xlrd.XL_CELL_NUMBER:
                    if value.endswith(".0"):
                        value = value[:-2]
                cells.append(value)
            md_lines.append("| " + " | ".join(cells) + " |")
            if row_idx == 0:
                md_lines.append("| " + " | ".join(["---"] * len(cells)) + " |")

        md_lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"Converted: {input_path} -> {output_path} ({len(wb.sheets())} sheets)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: py xls2md.py <input.xls> <output.md>")
        sys.exit(1)
    xls_to_md(sys.argv[1], sys.argv[2])
