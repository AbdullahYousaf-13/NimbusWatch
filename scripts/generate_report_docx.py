from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT_DIR / "docs" / "NIMBUSWATCH_FINAL_REPORT.md"
OUTPUT_PATH = ROOT_DIR / "docs" / "NIMBUSWATCH_FINAL_REPORT.docx"

COVER_LINES = [
    ("Cloud Based Malicious Traffic Detection System Using Hybrid Cloud Architecture", "Title"),
    ("", "Normal"),
    ("Submitted By:", "Normal"),
    ("Muhammad Abdullah (BCS223133)", "Normal"),
    ("", "Normal"),
    ("Submitted To:", "Normal"),
    ("Dr. Muhammad Masroor Ahmed", "Normal"),
    ("", "Normal"),
    ("Spring-2026", "Normal"),
    ("Department of Computer Science", "Normal"),
    ("Capital University of Science & Technology, Islamabad", "Normal"),
]


def add_field_run(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(separate)
    run._r.append(end)


def add_page_number(paragraph) -> None:
    add_field_run(paragraph, " PAGE ")


def add_table_of_contents(paragraph) -> None:
    add_field_run(paragraph, r' TOC \o "1-2" \h \z \u ')


def set_page_number_start(section, start: int) -> None:
    sect_pr = section._sectPr
    pg_num_type = sect_pr.find(qn("w:pgNumType"))
    if pg_num_type is None:
        pg_num_type = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num_type)
    pg_num_type.set(qn("w:start"), str(start))


def clean_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = text.replace("â€™", "'")
    text = text.replace("–", "-")
    return text.strip()


def apply_proposal_styles(document: Document) -> None:
    section = document.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.25)
    section.right_margin = Inches(1.25)
    section.header_distance = Inches(0.5)
    section.footer_distance = Inches(0.5)

    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.space_before = Pt(0)

    title = document.styles["Title"]
    title.font.name = "Times New Roman"
    title.font.size = Pt(26)
    title.paragraph_format.space_after = Pt(15)

    heading1 = document.styles["Heading 1"]
    heading1.font.name = "Times New Roman"
    heading1.font.size = Pt(14)
    heading1.font.bold = True
    heading1.paragraph_format.space_before = Pt(24)
    heading1.paragraph_format.space_after = Pt(0)

    heading2 = document.styles["Heading 2"]
    heading2.font.name = "Times New Roman"
    heading2.font.size = Pt(13)
    heading2.font.bold = True
    heading2.paragraph_format.space_before = Pt(10)
    heading2.paragraph_format.space_after = Pt(0)

    heading3 = document.styles["Heading 3"]
    heading3.font.name = "Times New Roman"
    heading3.font.size = Pt(12)
    heading3.font.bold = True
    heading3.paragraph_format.space_before = Pt(8)
    heading3.paragraph_format.space_after = Pt(0)


def add_cover_page(document: Document) -> None:
    for text, style_name in COVER_LINES:
        paragraph = document.add_paragraph(style=style_name)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if text:
            run = paragraph.add_run(text)
            run.font.name = "Times New Roman"
            if style_name == "Title":
                run.bold = True
        else:
            paragraph.add_run("")


def add_toc_page(document: Document) -> None:
    toc_section = document.add_section(WD_SECTION_START.NEW_PAGE)
    paragraph = document.add_paragraph(style="Heading 1")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("Table of Contents")
    toc_paragraph = document.add_paragraph()
    add_table_of_contents(toc_paragraph)
    document.add_paragraph("Right-click inside the table of contents in Microsoft Word and choose 'Update Field' before final printing.")
    content_section = document.add_section(WD_SECTION_START.NEW_PAGE)
    content_section.footer.is_linked_to_previous = False
    footer = content_section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number(footer)
    set_page_number_start(content_section, 1)
    document.sections[0].different_first_page_header_footer = True
    toc_section.different_first_page_header_footer = False
    content_section.different_first_page_header_footer = False


def set_cell_text(cell, text: str) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def add_arrow_paragraph(document: Document, text: str = "↓") -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(14)


def add_caption(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.italic = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)


def add_architecture_diagram(document: Document) -> None:
    table = document.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(1.7)
    table.columns[1].width = Inches(2.2)
    table.columns[2].width = Inches(1.7)
    set_cell_text(table.cell(0, 0), "Users / Analysts")
    set_cell_text(table.cell(0, 1), "Cloud Run Inference API")
    set_cell_text(table.cell(0, 2), "Hugging Face Space")

    add_arrow_paragraph(document)

    table2 = document.add_table(rows=1, cols=3)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.autofit = False
    table2.columns[0].width = Inches(1.7)
    table2.columns[1].width = Inches(2.2)
    table2.columns[2].width = Inches(1.7)
    set_cell_text(table2.cell(0, 0), "Cloud Scheduler")
    set_cell_text(table2.cell(0, 1), "Cloud Storage Artifacts")
    set_cell_text(table2.cell(0, 2), "Cloud Logging / Monitoring")

    add_arrow_paragraph(document)

    table3 = document.add_table(rows=1, cols=1)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table3.autofit = False
    table3.columns[0].width = Inches(2.4)
    set_cell_text(table3.cell(0, 0), "Vertex AI Training Job")
    add_caption(document, "Figure 1. NimbusWatch hybrid-cloud architecture.")


def add_data_flow_diagram(document: Document) -> None:
    steps = [
        "CICIDS2017 Source CSV Files",
        "Curated Dataset",
        "Preprocessing and Feature Selection",
        "HistGradientBoostingClassifier Training",
        "Artifact Generation",
        "Inference Service",
    ]
    for index, step in enumerate(steps):
        table = document.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table.columns[0].width = Inches(3.8)
        set_cell_text(table.cell(0, 0), step)
        if index < len(steps) - 1:
            add_arrow_paragraph(document)
    add_caption(document, "Figure 2. NimbusWatch data and model flow.")


def add_cross_cloud_diagram(document: Document) -> None:
    table = document.add_table(rows=1, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.1)
    table.columns[1].width = Inches(2.1)
    table.columns[2].width = Inches(2.1)
    set_cell_text(table.cell(0, 0), "Google Cloud\nTraining + Artifacts")
    set_cell_text(table.cell(0, 1), "Artifact Packaging and Sync")
    set_cell_text(table.cell(0, 2), "Hugging Face\nSecondary Deployment")
    add_caption(document, "Figure 3. Cross-cloud integration and deployment sync.")


def add_required_diagram(document: Document, heading_text: str) -> None:
    if heading_text == "4. Final System Architecture":
        add_architecture_diagram(document)
    elif heading_text == "5. Data Handling, Optimization, Scheduling, and Virtual Machines":
        add_data_flow_diagram(document)
    elif heading_text == "11. System Integration: How One Cloud Connects with Another Cloud":
        add_cross_cloud_diagram(document)


def build_body(document: Document, lines: list[str]) -> None:
    body_started = False
    in_code_block = False
    code_lines: list[str] = []
    bullet_pattern = re.compile(r"^[-*]\s+(.*)")
    numbered_pattern = re.compile(r"^\d+\.\s+(.*)")

    for raw_line in lines:
        line = raw_line.rstrip()

        if line.startswith("```"):
            if in_code_block:
                paragraph = document.add_paragraph(style="Normal")
                paragraph.paragraph_format.left_indent = Inches(0.35)
                run = paragraph.add_run("\n".join(code_lines))
                run.font.name = "Courier New"
                run.font.size = Pt(10)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not line.strip():
            if body_started:
                document.add_paragraph("")
            continue

        if line.startswith("# "):
            if not body_started:
                body_started = True
                continue
            heading = clean_inline(line[2:])
            document.add_paragraph(heading, style="Heading 1")
            add_required_diagram(document, heading)
            continue

        if line.startswith("## "):
            heading = clean_inline(line[3:])
            document.add_paragraph(heading, style="Heading 1")
            add_required_diagram(document, heading)
            body_started = True
            continue

        if line.startswith("### "):
            document.add_paragraph(clean_inline(line[4:]), style="Heading 2")
            body_started = True
            continue

        if line.startswith("#### "):
            document.add_paragraph(clean_inline(line[5:]), style="Heading 3")
            body_started = True
            continue

        bullet_match = bullet_pattern.match(line)
        if bullet_match:
            document.add_paragraph(clean_inline(bullet_match.group(1)), style="List Bullet")
            body_started = True
            continue

        numbered_match = numbered_pattern.match(line)
        if numbered_match:
            document.add_paragraph(clean_inline(numbered_match.group(1)), style="List Number")
            body_started = True
            continue

        paragraph = document.add_paragraph(style="Normal")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.add_run(clean_inline(line))
        body_started = True


def main() -> None:
    document = Document()
    apply_proposal_styles(document)
    add_cover_page(document)
    add_toc_page(document)
    lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines()
    build_body(document, lines)
    document.save(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
