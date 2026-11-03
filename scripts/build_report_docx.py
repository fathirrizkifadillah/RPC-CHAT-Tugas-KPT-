#!/usr/bin/env python3
"""
build_revised_docx.py
Script to assemble the complete, professionally revised academic report for:
Mata Kuliah: Komputasi Paralel dan Terdistribusi (Universitas Siliwangi)
Mini Project RPC — Case Study 3: Distributed Real-Time Chat Room

Key Improvements in Revision:
- Monochromatic / formal black typography and neutral styling (no bright blue titles).
- Single automatic Table of Contents with dot leaders (no duplicate manual table).
- Single automatic List of Figures and List of Tables using native SEQ fields (no error messages).
- Correct sequential chapter numbering for all figures and tables.
- Neutral, clean diagram artwork with figure numbering removed from artwork.
- Exact alignment of Benchmark Table 4.2 and Chart 4.1 with verified benchmark data (1.10 ms / 681.3 req/s, 5.10 ms / 909.9 req/s, 19.07 ms / 988.4 req/s).
- Clarified ThreadPoolExecutor configuration (default max_workers=30 in config.py, 50 in benchmark load test).
- Exact hardware specs retrieved via Windows PowerShell (Intel Core i7-1065G7, 8GB RAM, Windows 11 Pro).
- Real Git repository remote (https://github.com/fathirrizkifadillah/RPC-CHAT-Tugas-KPT-.git, branch main, commit 5b16ef4).
- Cleanly labeled appendices with meaningful excerpts and exact raw JSON/CSV data.
- Verified IEEE references.
"""

import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAPORAN_DIR = PROJECT_ROOT / "laporan"
LAPORAN_DIR.mkdir(parents=True, exist_ok=True)
DOCX_PATH = LAPORAN_DIR / "Laporan_Proyek_Mini_RPC_Kelompok3.docx"

ASSETS_DIR = LAPORAN_DIR / "assets"
SCREENSHOTS_DIR = ASSETS_DIR / "screenshots"
DIAGRAMS_DIR = ASSETS_DIR / "diagrams"
CHARTS_DIR = ASSETS_DIR / "charts"

LOGO_PATH = PROJECT_ROOT / "img" / "logo_unsil.jpg"
if not LOGO_PATH.exists():
    LOGO_PATH = Path(r"C:\TUGAS\KPT\RPC\img\logo_unsil\logo_unsil.jpg")

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for table cell in twips (1/20 of a pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="B0B8C0", sz="4", val="single"):
    """Set clean subtle borders for standard table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def set_box_borders(cell, border_color="475569", border_sz="20", fill_hex="F8FAFC"):
    """Set neutral callout box style with gray border and very light background."""
    set_cell_background(cell, fill_hex)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="none"/>'
        f'  <w:left w:val="single" w:sz="{border_sz}" w:space="0" w:color="{border_color}"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=140)


def add_field(p, field_code):
    """Insert a dynamic Word field into a paragraph."""
    run = p.add_run()
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> %s </w:instrText>' % (nsdecls('w'), field_code))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instr)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def add_page_number_field(run):
    """Insert a dynamic PAGE field into a run."""
    fldSimple = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    run._r.append(fldSimple)


def set_section_margins_and_paper(section):
    """Apply A4 size and standard Indonesian academic margins (Left 4cm, Top 3cm, Right 3cm, Bottom 3cm)."""
    section.page_width = Inches(8.27)   # 21.0 cm
    section.page_height = Inches(11.69) # 29.7 cm
    section.left_margin = Inches(1.5748)   # 4.0 cm
    section.right_margin = Inches(1.1811)  # 3.0 cm
    section.top_margin = Inches(1.1811)    # 3.0 cm
    section.bottom_margin = Inches(1.1811) # 3.0 cm
    section.header_distance = Inches(0.59) # 1.5 cm
    section.footer_distance = Inches(0.59) # 1.5 cm


def configure_styles(doc):
    """Configure default font to Times New Roman and formal sizing."""
    styles = doc.styles
    normal_style = styles['Normal']
    font = normal_style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(4)
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Heading 1: 14pt, Bold, Times New Roman, Black
    h1 = styles['Heading 1']
    h1.font.name = 'Times New Roman'
    h1.font.size = Pt(14)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0, 0, 0)
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    h1.paragraph_format.line_spacing = 1.15
    h1.paragraph_format.keep_with_next = True

    # Heading 2: 12pt, Bold, Times New Roman, Black
    h2 = styles['Heading 2']
    h2.font.name = 'Times New Roman'
    h2.font.size = Pt(12)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 0, 0)
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(4)
    h2.paragraph_format.line_spacing = 1.15
    h2.paragraph_format.keep_with_next = True

    # Heading 3: 12pt, Bold, Times New Roman, Black
    h3 = styles['Heading 3']
    h3.font.name = 'Times New Roman'
    h3.font.size = Pt(12)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(0, 0, 0)
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(3)
    h3.paragraph_format.line_spacing = 1.15
    h3.paragraph_format.keep_with_next = True

    # Caption style: 12pt, Times New Roman, Black
    caption_style = styles['Caption']
    caption_style.font.name = 'Times New Roman'
    caption_style.font.size = Pt(12)
    caption_style.font.color.rgb = RGBColor(0, 0, 0)
    caption_style.paragraph_format.line_spacing = 1.15


def add_chapter_heading(doc, bab_roman, chapter_title):
    """Add BAB heading formatted so TOC displays 'BAB I JUDUL' cleanly."""
    p = doc.add_paragraph(style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Notice the trailing space before \n so Word TOC preserves whitespace
    run = p.add_run(f"BAB {bab_roman} \n{chapter_title}")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 0, 0)
    return p


def add_heading_2(doc, text):
    """Add Heading 2."""
    p = doc.add_paragraph(text, style='Heading 2')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def add_heading_3(doc, text):
    """Add Heading 3."""
    p = doc.add_paragraph(text, style='Heading 3')
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def add_p(doc, text="", bold_prefix="", indent=False):
    """Add regular body paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.4)

    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Times New Roman'
        r_bold.font.size = Pt(12)
        r_bold.font.bold = True
        r_bold.font.color.rgb = RGBColor(0, 0, 0)

    if text:
        r_text = p.add_run(text)
        r_text.font.name = 'Times New Roman'
        r_text.font.size = Pt(12)
        r_text.font.color.rgb = RGBColor(0, 0, 0)

    return p


def add_callout(doc, text, bold_title=""):
    """Add a professional note/callout box in neutral styling."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_box_borders(cell, border_color="475569", border_sz="20", fill_hex="F8FAFC")
    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    if bold_title:
        r_title = p.add_run(bold_title + "\n")
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(11)
        r_title.font.bold = True
        r_title.font.color.rgb = RGBColor(15, 23, 42)

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(11)
    r_text.font.color.rgb = RGBColor(30, 41, 59)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(4)


def add_code_block(doc, code_str):
    """Add a clean code block with Consolas font and subtle neutral border."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)

    lines = code_str.strip().split("\n")
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.paragraph_format.line_spacing = 1.05
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(15, 23, 42)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(4)


def add_image_figure(doc, image_path, chapter_num, title_text, is_first_in_chapter=False, width_inches=5.8):
    """Add a centered figure with formal academic caption below it containing native SEQ Gambar field."""
    if not Path(image_path).exists():
        print(f"[WARN] Gambar tidak ditemukan: {image_path}")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(str(image_path), width=Inches(width_inches))

    # Caption with SEQ Gambar
    p_cap = doc.add_paragraph(style='Caption')
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)

    r_lbl = p_cap.add_run(f"Gambar {chapter_num}.")
    r_lbl.font.name = 'Times New Roman'
    r_lbl.font.size = Pt(12)
    r_lbl.font.color.rgb = RGBColor(0, 0, 0)

    seq_code = 'SEQ Gambar \\r 1 \\* ARABIC' if is_first_in_chapter else 'SEQ Gambar \\* ARABIC'
    add_field(p_cap, seq_code)

    r_title = p_cap.add_run(f" {title_text}")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(12)
    r_title.font.color.rgb = RGBColor(0, 0, 0)


def add_table_with_caption(doc, chapter_num, title_text, headers, data_rows, is_first_in_chapter=False, col_widths=None, alignments=None, exclude_from_seq=False):
    """Add formal table with caption above it and clean neutral styled borders."""
    p_cap = doc.add_paragraph(style='Caption')
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(8)
    p_cap.paragraph_format.space_after = Pt(3)
    p_cap.paragraph_format.keep_with_next = True

    if exclude_from_seq:
        r_cap = p_cap.add_run(f"{title_text}")
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(12)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(0, 0, 0)
    else:
        r_lbl = p_cap.add_run(f"Tabel {chapter_num}.")
        r_lbl.font.name = 'Times New Roman'
        r_lbl.font.size = Pt(12)
        r_lbl.font.bold = True
        r_lbl.font.color.rgb = RGBColor(0, 0, 0)

        seq_code = 'SEQ Tabel \\r 1 \\* ARABIC' if is_first_in_chapter else 'SEQ Tabel \\* ARABIC'
        add_field(p_cap, seq_code)

        r_title = p_cap.add_run(f" {title_text}")
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(12)
        r_title.font.bold = True
        r_title.font.color.rgb = RGBColor(0, 0, 0)

    table = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table, color="94A3B8", sz="6", val="single")

    # Header Row
    hdr_row = table.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for col_idx, h_text in enumerate(headers):
        cell = hdr_row.cells[col_idx]
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(h_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42)

    # Data Rows
    for row_idx, row_data in enumerate(data_rows):
        row = table.rows[row_idx + 1]
        bg_fill = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            cell = row.cells[col_idx]
            set_cell_background(cell, bg_fill)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.LEFT
            if alignments and col_idx < len(alignments):
                align = alignments[col_idx]
            p.alignment = align
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(str(cell_value))
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10.5)
            run.font.color.rgb = RGBColor(15, 23, 42)

    if col_widths:
        for row in table.rows:
            for idx, width in enumerate(col_widths):
                if idx < len(row.cells):
                    row.cells[idx].width = Inches(width)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(6)


def build_cover_page(doc):
    """Section 1: Academic Cover Page in strict formal monochromatic design."""
    sec = doc.sections[0]
    set_section_margins_and_paper(sec)

    sec.different_first_page_header_footer = False
    footer = sec.footer
    footer.is_linked_to_previous = False
    p_ft = footer.paragraphs[0]
    p_ft.text = ""

    # Cover Title (All in Black)
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_before = Pt(24)
    p_t1.paragraph_format.space_after = Pt(6)
    p_t1.paragraph_format.line_spacing = 1.15
    r_t1 = p_t1.add_run("LAPORAN TUGAS PROYEK MINI\nKOMPUTASI PARALEL DAN TERDISTRIBUSI")
    r_t1.font.name = 'Times New Roman'
    r_t1.font.size = Pt(16)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(0, 0, 0)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(6)
    p_sub.paragraph_format.space_after = Pt(16)
    p_sub.paragraph_format.line_spacing = 1.2
    r_sub = p_sub.add_run(
        "STUDI KASUS 3: SISTEM CHAT ROOM TERDISTRIBUSI REAL-TIME\n"
        "BERBASIS REMOTE PROCEDURE CALLS (gRPC) DAN PYTHON"
    )
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0, 0, 0)

    # Logo UNSIL in Original Colors
    if LOGO_PATH.exists():
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(16)
        p_logo.paragraph_format.space_after = Pt(16)
        run_logo = p_logo.add_run()
        run_logo.add_picture(str(LOGO_PATH), width=Inches(2.1))
    else:
        p_spacer = doc.add_paragraph()
        p_spacer.paragraph_format.space_before = Pt(60)

    # Author Information
    p_auth_title = doc.add_paragraph()
    p_auth_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth_title.paragraph_format.space_before = Pt(12)
    p_auth_title.paragraph_format.space_after = Pt(4)
    r_at = p_auth_title.add_run("Disusun Oleh:")
    r_at.font.name = 'Times New Roman'
    r_at.font.size = Pt(12)
    r_at.font.bold = True
    r_at.font.color.rgb = RGBColor(0, 0, 0)

    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(2)
    p_auth.paragraph_format.space_after = Pt(36)
    p_auth.paragraph_format.line_spacing = 1.3

    r1 = p_auth.add_run("FATHIR RIZKI FADILLAH\n")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(12)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0, 0, 0)

    r2 = p_auth.add_run("NIM: 247006111129\n\n")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11)
    r2.font.color.rgb = RGBColor(0, 0, 0)

    r3 = p_auth.add_run("[Anggota Kelompok 2 - Menunggu Konfirmasi]\n")
    r3.font.name = 'Times New Roman'
    r3.font.size = Pt(11)
    r3.font.italic = True
    r3.font.color.rgb = RGBColor(70, 70, 70)

    r4 = p_auth.add_run("NIM: [NIM Mahasiswa 2]\n\n")
    r4.font.name = 'Times New Roman'
    r4.font.size = Pt(10.5)
    r4.font.color.rgb = RGBColor(70, 70, 70)

    r5 = p_auth.add_run("[Anggota Kelompok 3 - Menunggu Konfirmasi]\n")
    r5.font.name = 'Times New Roman'
    r5.font.size = Pt(11)
    r5.font.italic = True
    r5.font.color.rgb = RGBColor(70, 70, 70)

    r6 = p_auth.add_run("NIM: [NIM Mahasiswa 3]\n")
    r6.font.name = 'Times New Roman'
    r6.font.size = Pt(10.5)
    r6.font.color.rgb = RGBColor(70, 70, 70)

    # University Footer
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(16)
    p_inst.paragraph_format.space_after = Pt(0)
    p_inst.paragraph_format.line_spacing = 1.15
    r_inst = p_inst.add_run(
        "PROGRAM STUDI INFORMATIKA\n"
        "FAKULTAS TEKNIK\n"
        "UNIVERSITAS SILIWANGI\n"
        "TASIKMALAYA\n"
        "2026 / 2027"
    )
    r_inst.font.name = 'Times New Roman'
    r_inst.font.size = Pt(12)
    r_inst.font.bold = True
    r_inst.font.color.rgb = RGBColor(0, 0, 0)


def build_front_matter(doc):
    """Section 2: Front Matter (Roman numerals i, ii, iii...)."""
    sec2 = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    set_section_margins_and_paper(sec2)

    sec2.different_first_page_header_footer = False
    footer = sec2.footer
    footer.is_linked_to_previous = False
    p_ft = footer.paragraphs[0]
    p_ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ft.text = ""
    run_num = p_ft.add_run()
    run_num.font.name = 'Times New Roman'
    run_num.font.size = Pt(11)
    run_num.font.color.rgb = RGBColor(0, 0, 0)
    add_page_number_field(run_num)

    sectPr = sec2._sectPr
    pgNumType = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="roman-lower" w:start="1"/>')
    sectPr.append(pgNumType)

    # 1. LEMBAR IDENTITAS PROYEK
    p_h = doc.add_paragraph(style='Heading 1')
    p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_h = p_h.add_run("LEMBAR IDENTITAS PROYEK")
    r_h.font.name = 'Times New Roman'
    r_h.font.size = Pt(14)
    r_h.font.bold = True
    r_h.font.color.rgb = RGBColor(0, 0, 0)

    add_p(doc, "Tugas Proyek Mini ini disusun untuk memenuhi persyaratan akademik mata kuliah Komputasi Paralel dan Terdistribusi pada Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi.")

    headers_id = ["Informasi Proyek", "Keterangan Spesifik"]
    data_id = [
        ["Judul Proyek Mini", "Sistem Terdistribusi Berbasis RPC: Real-Time Chat Room"],
        ["Studi Kasus Terpilih", "Studi Kasus 3: Chat Room banyak pengguna bertukar pesan real-time"],
        ["Mata Kuliah", "Komputasi Paralel dan Terdistribusi (KPT)"],
        ["Dosen Pengampu", "Tim Dosen Komputasi Paralel dan Terdistribusi"],
        ["Penulis Utama / Ketua", "Fathir Rizki Fadillah (NIM: 247006111129)"],
        ["Anggota Pengembang 2", "[Menunggu Konfirmasi - NIM: 247006111XXX]"],
        ["Anggota Pengembang 3", "[Menunggu Konfirmasi - NIM: 247006111YYY]"],
        ["Tautan Repositori Git", "https://github.com/fathirrizkifadillah/RPC-CHAT-Tugas-KPT-.git"],
        ["Cabang Utama (Branch)", "main (Commit: 5b16ef4)"],
        ["Tautan Video Demonstrasi", "https://youtu.be/[ID_VIDEO_YOUTUBE] (Skenario terencana 5 menit)"],
        ["Status Pengujian Fungsional", "22 Skenario Pengujian Unit & Integrasi Pytest (100% Passed)"],
        ["Status Pengujian Beban", "Selesai diuji untuk 1, 5, dan 20 client bersamaan (100% Sukses)"]
    ]
    # Exclude administrative table from SEQ Tabel so it does not clutter technical table list
    add_table_with_caption(doc, 0, "Tabel Identitas Pelaksanaan Proyek Mini", headers_id, data_id, col_widths=[2.4, 3.8], exclude_from_seq=True)

    add_callout(
        doc,
        "Kami menyatakan dengan sesungguhnya bahwa kode program, analisis arsitektur, dan seluruh data pengujian "
        "yang disajikan dalam laporan ini merupakan hasil pengerjaan mandiri yang dapat ditelusuri ke repositori "
        "dan artefak pengujian nyata tanpa manipulasi data.\n\n"
        "Mengetahui / Penulis Utama,\n\n"
        "Fathir Rizki Fadillah (NIM: 247006111129)",
        bold_title="PERNYATAAN INTEGRITAS AKADEMIK"
    )

    doc.add_page_break()

    # 2. KATA PENGANTAR
    p_kp = doc.add_paragraph(style='Heading 1')
    p_kp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_kp = p_kp.add_run("KATA PENGANTAR")
    r_kp.font.name = 'Times New Roman'
    r_kp.font.size = Pt(14)
    r_kp.font.bold = True
    r_kp.font.color.rgb = RGBColor(0, 0, 0)

    add_p(
        doc,
        "Puji dan syukur kami panjatkan ke hadirat Tuhan Yang Maha Esa atas segala rahmat dan karunia-Nya, "
        "sehingga laporan Tugas Proyek Mini mata kuliah Komputasi Paralel dan Terdistribusi dengan judul "
        "\"Sistem Terdistribusi Berbasis RPC: Distributed Chat Room Real-Time Menggunakan gRPC dan Python\" "
        "dapat diselesaikan dengan baik dan tepat waktu.",
        indent=True
    )
    add_p(
        doc,
        "Proyek mini ini difokuskan pada penerapan praktis konsep Remote Procedure Call (RPC) modern melalui framework "
        "gRPC dan Protocol Buffers versi 3. Melalui studi kasus ruang obrolan (chat room) terdistribusi real-time yang representatif, kami "
        "mengimplementasikan arsitektur bidirectional streaming HTTP/2, sinkronisasi memori bersama yang aman (thread-safe shared state), "
        "penanganan toleransi kegagalan jaringan (timeout, exponential backoff retry, dan deduplikasi at-most-once), "
        "serta isolasi antrean pesan untuk mencegah bottleneck client lambat.",
        indent=True
    )
    add_p(
        doc,
        "Penulis menyampaikan terima kasih yang sebesar-besarnya kepada Dosen Pengampu mata kuliah Komputasi Paralel "
        "dan Terdistribusi atas arahan teoritis dan teknis sepanjang perkuliahan, serta rekan-rekan mahasiswa yang telah "
        "memberikan diskusi yang membangun.",
        indent=True
    )
    add_p(
        doc,
        "Penulis menyadari laporan ini masih memiliki ruang penyempurnaan. Oleh karena itu, kritik dan saran yang "
        "membangun sangat diharapkan. Semoga laporan ini dapat memberikan wawasan teknis yang bermanfaat dalam "
        "pengembangan perangkat lunak sistem terdistribusi.",
        indent=True
    )

    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.space_before = Pt(24)
    r_sig = p_sig.add_run("Tasikmalaya, November 2026\n\n\n\nTim Penulis")
    r_sig.font.name = 'Times New Roman'
    r_sig.font.size = Pt(11)
    r_sig.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # 3. DAFTAR ISI (EXACTLY ONE AUTOMATIC TOC)
    p_ti = doc.add_paragraph(style='Heading 1')
    p_ti.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ti = p_ti.add_run("DAFTAR ISI")
    r_ti.font.name = 'Times New Roman'
    r_ti.font.size = Pt(14)
    r_ti.font.bold = True
    r_ti.font.color.rgb = RGBColor(0, 0, 0)

    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.space_after = Pt(6)
    add_field(p_toc, 'TOC \\o "1-3" \\h \\z \\u')

    doc.add_page_break()

    # 4. DAFTAR GAMBAR (EXACTLY ONE AUTOMATIC LIST OF FIGURES)
    p_tg = doc.add_paragraph(style='Heading 1')
    p_tg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tg = p_tg.add_run("DAFTAR GAMBAR")
    r_tg.font.name = 'Times New Roman'
    r_tg.font.size = Pt(14)
    r_tg.font.bold = True
    r_tg.font.color.rgb = RGBColor(0, 0, 0)

    p_tof = doc.add_paragraph()
    p_tof.paragraph_format.space_after = Pt(6)
    add_field(p_tof, 'TOC \\c "Gambar" \\h \\z')

    doc.add_page_break()

    # 5. DAFTAR TABEL (EXACTLY ONE AUTOMATIC LIST OF TABLES)
    p_tt = doc.add_paragraph(style='Heading 1')
    p_tt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tt = p_tt.add_run("DAFTAR TABEL")
    r_tt.font.name = 'Times New Roman'
    r_tt.font.size = Pt(14)
    r_tt.font.bold = True
    r_tt.font.color.rgb = RGBColor(0, 0, 0)

    p_tot = doc.add_paragraph()
    p_tot.paragraph_format.space_after = Pt(6)
    add_field(p_tot, 'TOC \\c "Tabel" \\h \\z')


def build_main_content(doc):
    """Section 3: Main Academic Content (Arabic numerals 1, 2, 3... starting at 1)."""
    sec3 = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    set_section_margins_and_paper(sec3)

    sec3.different_first_page_header_footer = False

    # Header configuration
    hdr = sec3.header
    hdr.is_linked_to_previous = False
    p_hdr = hdr.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hdr.text = ""
    r_hdr = p_hdr.add_run("Laporan Tugas Proyek Mini — Komputasi Paralel dan Terdistribusi")
    r_hdr.font.name = 'Times New Roman'
    r_hdr.font.size = Pt(8.5)
    r_hdr.font.italic = True
    r_hdr.font.color.rgb = RGBColor(100, 100, 100)

    # Footer configuration
    ftr = sec3.footer
    ftr.is_linked_to_previous = False
    p_ftr = ftr.paragraphs[0]
    p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ftr.text = ""
    r_ftr = p_ftr.add_run()
    r_ftr.font.name = 'Times New Roman'
    r_ftr.font.size = Pt(11)
    r_ftr.font.color.rgb = RGBColor(0, 0, 0)
    add_page_number_field(r_ftr)

    sectPr = sec3._sectPr
    pgNumType = parse_xml(f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>')
    sectPr.append(pgNumType)

    # ==========================================
    # BAB I: DESKRIPSI STUDI KASUS DAN DIAGRAM ARSITEKTUR
    # ==========================================
    add_chapter_heading(doc, "I", "DESKRIPSI STUDI KASUS DAN DIAGRAM ARSITEKTUR")

    add_heading_2(doc, "1.1 Latar Belakang dan Deskripsi Studi Kasus")
    add_p(
        doc,
        "Dalam perkembangan rekayasa perangkat lunak modern, paradigma komputasi terdistribusi telah menjadi landasan "
        "fundamental bagi pembangunan sistem berkinerja tinggi, berdaya tahan tinggi, dan terukur (scalable). Salah satu "
        "tantangan krusial dalam sistem terdistribusi adalah bagaimana proses-proses yang berjalan pada lingkungan fisik atau "
        "container yang terisolasi dapat saling bertukar informasi secara efisien, konsisten, dan berlatensi rendah. "
        "Mekanisme Remote Procedure Call (RPC) hadir sebagai abstraksi tingkat tinggi yang memungkinkan suatu program memanggil "
        "prosedur atau metode pada ruang alamat komputer lain seolah-olah memanggil fungsi lokal.",
        indent=True
    )
    add_p(
        doc,
        "Berdasarkan pedoman resmi Tugas Proyek Mini mata kuliah Komputasi Paralel dan Terdistribusi, studi kasus yang "
        "dipilih dan diimplementasikan secara komprehensif pada proyek ini adalah Pilihan Nomor 3: Chat Room banyak pengguna "
        "yang bertukar pesan secara real-time. Aplikasi obrolan terdistribusi merupakan studi kasus yang representatif dari sistem "
        "koordinasi terdistribusi karena memiliki tuntutan teknis yang kompleks, mencakup komunikasi full-duplex real-time, "
        "manajemen konkurensi data bersama, isolasi antrean pesan, serta toleransi terhadap fluktuasi koneksi jaringan.",
        indent=True
    )
    add_p(
        doc,
        "Karakteristik fundamental dan batasan arsitektur sistem ini meliputi:",
        indent=True
    )
    add_p(doc, "Setiap client dapat mengirimkan pesan obrolan dan menerima pesan siaran (broadcast) dari partisipan lain secara simultan tanpa saling memblokir (non-blocking asynchronous exchange).", bold_prefix="1. Pertukaran Pesan Simultan: ")
    add_p(doc, "Server memelihara daftar sesi pengguna aktif (active user registry) dalam memori secara dinamis, mengumumkan pengguna baru yang bergabung, serta memutakhirkan status saat client meninggalkan ruang obrolan.", bold_prefix="2. Koordinasi Pengguna Aktif: ")
    add_p(doc, "Menggunakan kapabilitas Bidirectional Streaming gRPC di atas protokol transport HTTP/2, di mana koneksi TCP persisten tunggal dimanfaatkan secara efisien untuk aliran pesan dua arah dengan binary framing multiplexing.", bold_prefix="3. Komunikasi Duplex Berbasis HTTP/2: ")
    add_p(doc, "Sesuai arahan spesifikasi akademik, sistem mengadopsi penyimpanan in-memory yang dilindungi sinkronisasi thread-safe, tanpa ketergantungan basis data eksternal atau message broker pihak ketiga, sehingga pengujian murni mengevaluasi performa RPC dan konkurensi sistem operasi.", bold_prefix="4. Arsitektur In-Memory Terfokus: ")

    add_heading_2(doc, "1.2 Diagram Arsitektur Komponen Sistem")
    add_p(
        doc,
        "Arsitektur dirancang dengan pemisahan tanggung jawab yang modular dan jelas antara lingkungan container client "
        "dan container server, merujuk pada spesifikasi diagram arsitektur terdistribusi:",
        indent=True
    )

    add_image_figure(
        doc,
        DIAGRAMS_DIR / "01_system_architecture.png",
        chapter_num=1,
        title_text="Diagram Arsitektur Sistem Distributed Chat Room gRPC",
        is_first_in_chapter=True,
        width_inches=5.8
    )

    add_p(
        doc,
        "Komponen utama dalam arsitektur sistem terdistribusi ini terbagi atas:",
        indent=True
    )
    add_p(doc, "Menjalankan aplikasi command-line interface interaktif berbasis multi-threading Python. Thread UI bertugas menangani input pengguna dari terminal, sedangkan thread background pembaca stream bertugas mendengarkan pesan masuk dari server secara kontinu.", bold_prefix="a. Container Client (CLI Nodes): ")
    add_p(doc, "Menjalankan server gRPC multi-threaded berbasis concurrent.futures.ThreadPoolExecutor (dikonfigurasi default 30 worker threads pada config.py) yang mendengarkan pemanggilan RPC pada port 50051 melalui protokol HTTP/2.", bold_prefix="b. Container Server (gRPC Host): ")
    add_p(doc, "Implementasi kelas LayananChat yang mewarisi gRPC servicers stub, menyediakan 4 antarmuka RPC (Join, ListUsers, SendMessage, dan Chat).", bold_prefix="c. Modul Layanan Chat: ")
    add_p(doc, "Struktur data tunggal (singleton) di memori server yang memelihara registri pengguna (users), pemetaan antrean privat per-client (queue), dan tabel deduplikasi (PROSES) untuk menjamin semantik at-most-once.", bold_prefix="d. Shared State Management: ")

    add_heading_2(doc, "1.3 Alur Komunikasi dan Interaksi Pemanggilan RPC")
    add_p(
        doc,
        "Interaksi komunikasi antara client dan server terbagi dalam siklus hidup empat fase logis yang terkoordinasi secara ketat:",
        indent=True
    )

    add_image_figure(
        doc,
        DIAGRAMS_DIR / "02_sequence_diagram.png",
        chapter_num=1,
        title_text="Diagram Sekuensial Komunikasi Client-Server gRPC",
        is_first_in_chapter=False,
        width_inches=5.8
    )

    add_p(doc, "Client mengawali interaksi dengan memanggil Unary RPC Join. Server memvalidasi keunikan username di dalam registry memori users. Jika username valid dan belum digunakan, server mengalokasikan user_id berbasis UUID v4, mencatat stempel waktu terhubung, dan mengembalikan respons sukses.", bold_prefix="1. Fase Handshake & Registrasi Identitas: ")
    add_p(doc, "Client membuka koneksi bidirectional streaming Chat. Client mengirimkan frame perdana bertipe FRAME_TYPE_JOIN. Server segera menginisialisasi antrean pesan privat queue.Queue(maxsize=100) untuk client tersebut, mengirimkan frame konfirmasi FRAME_TYPE_ACK, serta membroadcast frame FRAME_TYPE_USER_EVENT ke seluruh client lain.", bold_prefix="2. Fase Inisialisasi Aliran Streaming: ")

    add_image_figure(
        doc,
        DIAGRAMS_DIR / "03_bidirectional_streaming_workflow.png",
        chapter_num=1,
        title_text="Alur Kerja Komunikasi Bidirectional Streaming gRPC",
        is_first_in_chapter=False,
        width_inches=5.8
    )

    add_p(doc, "Pertukaran pesan dilakukan melalui dua jalur alternatif: (a) Jalur Aliran Streaming Utama: Client mengalirkan ChatFrame bertipe FRAME_TYPE_MESSAGE yang kemudian direplikasi oleh server ke antrean seluruh client aktif; (b) Jalur Unary Alternatif: Client dapat memanggil SendMessage untuk skenario pesan mandiri berorientasi request-response dengan konfirmasi delivered_at.", bold_prefix="3. Fase Pertukaran Pesan Real-Time: ")
    add_p(doc, "Ketika client keluar secara normal (/quit) atau terputus mendadak akibat kegagalan jaringan, callback context.add_callback() pada server secara otomatis mencabut antrean client, membersihkan registry users, dan membroadcast frame leave ke seluruh client yang tersisa.", bold_prefix="4. Fase Terminasi & Pembersihan Sesi: ")

    # ==========================================
    # BAB II: SPESIFIKASI DAN PENJELASAN PROTOBUF IDL
    # ==========================================
    doc.add_page_break()
    add_chapter_heading(doc, "II", "SPESIFIKASI DAN PENJELASAN INTERFACE DEFINITION LANGUAGE (.proto)")

    add_heading_2(doc, "2.1 Kode Sumber Lengkap chat_room.proto")
    add_p(
        doc,
        "Kontrak antarmuka layanan dan skema serialisasi data didefinisikan secara deklaratif menggunakan Protocol Buffers versi 3 "
        "(proto3) pada berkas proto/chat_room.proto. Definisi ini mematuhi ketentuan umum tugas yang mewajibkan minimal 4 metode RPC "
        "dengan sekurang-kurangnya satu metode streaming:",
        indent=True
    )

    proto_code = """syntax = "proto3";

package chat_room;

// Layanan utama Chat Room RPC terdistribusi
service LayananChat {
  // RPC 1: Registrasi sesi pengguna baru (Unary RPC)
  rpc Join (JoinRequest) returns (JoinResponse);

  // RPC 2: Mengambil daftar pengguna aktif di memori server (Unary RPC)
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);

  // RPC 3: Pengiriman pesan mandiri dengan proteksi request_id (Unary RPC)
  rpc SendMessage (SendMessageRequest) returns (SendMessageResponse);

  // RPC 4: Aliran bidirectional streaming untuk pertukaran real-time (Duplex)
  rpc Chat (stream ChatFrame) returns (stream ChatFrame);
}

// Model pesan permintaan Join
message JoinRequest {
  string username = 1;
  string client_id = 2;
  string request_id = 3;
}

// Model pesan balasan Join
message JoinResponse {
  bool success = 1;
  string message = 2;
  string user_id = 3;
  int64 joined_at = 4;
}

// Model permintaan ListUsers
message ListUsersRequest {
  string request_id = 1;
}

// Entitas data pengguna aktif
message UserInfo {
  string user_id = 1;
  string username = 2;
  int64 connected_at = 3;
  bool is_active = 4;
}

// Model balasan ListUsers
message ListUsersResponse {
  bool success = 1;
  repeated UserInfo users = 2;
  int32 total_users = 3;
}

// Model permintaan pengiriman pesan Unary
message SendMessageRequest {
  string request_id = 1;
  string sender_username = 2;
  string content = 3;
  int64 timestamp = 4;
}

// Model balasan pengiriman pesan Unary
message SendMessageResponse {
  string request_id = 1;
  bool success = 2;
  string message = 3;
  int64 delivered_at = 4;
}

// Klasifikasi jenis frame pada aliran Bidirectional Streaming
enum FrameType {
  FRAME_TYPE_UNSPECIFIED = 0;
  FRAME_TYPE_JOIN = 1;
  FRAME_TYPE_MESSAGE = 2;
  FRAME_TYPE_LEAVE = 3;
  FRAME_TYPE_HEARTBEAT = 4;
  FRAME_TYPE_ACK = 5;
  FRAME_TYPE_USER_EVENT = 6;
  FRAME_TYPE_ERROR = 7;
}

// Frame data terpadu untuk bidirectional stream Chat
message ChatFrame {
  FrameType type = 1;
  string request_id = 2;
  string sender = 3;
  string content = 4;
  int64 timestamp = 5;
  string user_id = 6;
}"""
    add_code_block(doc, proto_code)

    add_heading_2(doc, "2.2 Penjelasan Rinci Setiap Metode RPC")
    add_p(
        doc,
        "Layanan LayananChat mengimplementasikan empat prosedur RPC dengan karakteristik semantik yang berbeda:",
        indent=True
    )

    add_heading_3(doc, "1. rpc Join (JoinRequest) returns (JoinResponse)")
    add_p(doc, "Unary RPC (Request-Response standar).", bold_prefix="• Pola Komunikasi: ")
    add_p(doc, "Mendaftarkan identitas client sebelum berpartisipasi dalam percakapan.", bold_prefix="• Peran Fungsional: ")
    add_p(doc, "Idempoten bersyarat. Jika request_id dan client_id yang sama dikirimkan kembali (misalnya karena retry jaringan), server mengembalikan user_id yang telah dialokasikan tanpa membuat entitas duplikat.", bold_prefix="• Semantik Eksekusi: ")
    add_p(doc, "Mengembalikan gRPC StatusCode.INVALID_ARGUMENT jika username kosong atau hanya berisi spasi; mengembalikan StatusCode.ALREADY_EXISTS jika username sudah digunakan oleh client aktif lain.", bold_prefix="• Penanganan Error: ")

    add_heading_3(doc, "2. rpc ListUsers (ListUsersRequest) returns (ListUsersResponse)")
    add_p(doc, "Unary RPC.", bold_prefix="• Pola Komunikasi: ")
    add_p(doc, "Menyediakan snapshot data seluruh pengguna yang saat itu sedang aktif di ruang obrolan.", bold_prefix="• Peran Fungsional: ")
    add_p(doc, "Idempoten murni (Read-Only State Inspection).", bold_prefix="• Semantik Eksekusi: ")
    add_p(doc, "Menggunakan field repeated UserInfo pada skema Protobuf untuk melakukan serialisasi array entitas pengguna secara padat dan efisien.", bold_prefix="• Struktur Payload: ")

    add_heading_3(doc, "3. rpc SendMessage (SendMessageRequest) returns (SendMessageResponse)")
    add_p(doc, "Unary RPC.", bold_prefix="• Pola Komunikasi: ")
    add_p(doc, "Menyediakan jalur pengiriman pesan alternatif berbasis request-response langsung.", bold_prefix="• Peran Fungsional: ")
    add_p(doc, "At-most-once terlindungi melalui komponen PROSES. Jika client melakukan transmisi ulang pesan yang sama akibat timeout sementara, server mendeteksi duplikasi request_id dan mengembalikan respons yang tersimpan tanpa menduplikasi siaran pesan ke partisipan lain.", bold_prefix="• Semantik Eksekusi: ")

    add_heading_3(doc, "4. rpc Chat (stream ChatFrame) returns (stream ChatFrame)")
    add_p(doc, "Bidirectional Streaming RPC (Duplex Stream).", bold_prefix="• Pola Komunikasi: ")
    add_p(doc, "Jalur pipa utama komunikasi obrolan real-time berlatensi ultra-rendah.", bold_prefix="• Peran Fungsional: ")
    add_p(doc, "Aliran kejadian berurutan (ordered message stream). Client dan server mempertahankan koneksi terbuka di mana kedua belah pihak dapat mengirimkan frame secara independen kapan saja.", bold_prefix="• Semantik Eksekusi: ")

    add_heading_2(doc, "2.3 Desain Payload Data dan Skema Frame Streaming")
    add_p(
        doc,
        "Untuk mendukung fleksibilitas pertukaran pesan pada jalur streaming tunggal, entitas ChatFrame mengadopsi pola "
        "Tagged Union berbasis enumerasi FrameType. Desain ini memungkinkan berbagai jenis pesan kontrol dan data disalurkan "
        "melalui satu saluran tanpa membutuhkan endpoint terpisah:",
        indent=True
    )

    headers_enum = ["Tipe Frame (Enum)", "Nilai Numerik", "Arah Aliran", "Deskripsi dan Tujuan Fungsional"]
    data_enum = [
        ["FRAME_TYPE_UNSPECIFIED", "0", "N/A", "Nilai default protobuf sebagai fallback pengaman tipe data."],
        ["FRAME_TYPE_JOIN", "1", "Client -> Server", "Frame inisiasi stream untuk mengaitkan saluran dengan user_id."],
        ["FRAME_TYPE_MESSAGE", "2", "Duplex (Dua Arah)", "Payload pesan obrolan teks antar-pengguna real-time."],
        ["FRAME_TYPE_LEAVE", "3", "Client -> Server", "Pemberitahuan terminasi sesi obrolan secara terencana."],
        ["FRAME_TYPE_HEARTBEAT", "4", "Duplex (Dua Arah)", "Pemeriksaan integritas koneksi untuk deteksi dead connection."],
        ["FRAME_TYPE_ACK", "5", "Server -> Client", "Konfirmasi penerimaan frame atau registrasi stream berhasil."],
        ["FRAME_TYPE_USER_EVENT", "6", "Server -> Client", "Siaran notifikasi status pengguna (misal: user join atau leave)."],
        ["FRAME_TYPE_ERROR", "7", "Server -> Client", "Pemberitahuan kesalahan operasional pada level stream."]
    ]
    add_table_with_caption(doc, chapter_num=2, title_text="Klasifikasi FrameType Aliran Streaming ChatFrame", headers=headers_enum, data_rows=data_enum, is_first_in_chapter=True, col_widths=[2.1, 0.8, 1.4, 2.7])

    # ==========================================
    # BAB III: STRATEGI CONCURRENCY DAN TOLERANSI KEGAGALAN
    # ==========================================
    doc.add_page_break()
    add_chapter_heading(doc, "III", "STRATEGI CONCURRENCY DAN TOLERANSI KEGAGALAN")

    add_heading_2(doc, "3.1 Manajemen Concurrency dan Sinkronisasi Shared Memory (ChatState)")
    add_p(
        doc,
        "Dalam lingkungan server gRPC multi-threaded, pemanggilan RPC oleh puluhan client dieksekusi secara konkuren "
        "oleh thread worker yang dialokasikan dari ThreadPoolExecutor. Pada konfigurasi standar aplikasi (src/chat_room/config.py), "
        "server dialokasikan batas 30 worker threads. Namun saat pengujian beban tinggi (benchmarks/run_benchmark.py), server diinisialisasi "
        "dengan kapasitas 50 worker threads guna memberikan ruang napas (headroom) bagi 20 client konkuren simultan tanpa risiko thread starvation.",
        indent=True
    )

    add_image_figure(
        doc,
        DIAGRAMS_DIR / "05_concurrency_dedup_architecture.png",
        chapter_num=3,
        title_text="Arsitektur Sinkronisasi dan Deduplikasi Memori",
        is_first_in_chapter=True,
        width_inches=5.8
    )

    add_p(
        doc,
        "Manajemen state server dipusatkan pada kelas singleton ChatState (diimplementasikan pada src/chat_room/state.py). "
        "Seluruh manipulasi data bersama dilindungi oleh kunci reentrant lock (threading.RLock()):",
        indent=True
    )

    code_state = """class ChatState:
    def __init__(self, queue_maxsize: int = 100, max_proses: int = 10000):
        self._lock = threading.RLock()
        self._users: Dict[str, Dict[str, Any]] = {}       # user_id -> metadata
        self._usernames: Dict[str, str] = {}              # username -> user_id
        self._queues: Dict[str, queue.Queue] = {}         # user_id -> FIFO queue
        self._proses: OrderedDict[str, Any] = OrderedDict() # request_id -> response cache
        self._queue_maxsize = queue_maxsize
        self._max_proses = max_proses"""
    add_code_block(doc, code_state)

    add_p(
        doc,
        "Untuk menjaga throughput server tetap optimal, arsitektur ini menerapkan prinsip Critical Section Minimalis. "
        "Lock RLock hanya dipegang saat memutasi dictionary internal atau menyalin snapshot referensi antrean. "
        "Operasi input/output (I/O) jaringan dan transmisi frame di luar memori dieksekusi di luar cakupan lock, "
        "sehingga waktu tunggu antrean antar-thread worker dapat ditekan seminimal mungkin.",
        indent=True
    )

    add_heading_2(doc, "3.2 Isolasi Antrean Pesan per Client dan Penanganan Slow Client")
    add_p(
        doc,
        "Pada arsitektur obrolan terdistribusi, salah satu tantangan fatal adalah keberadaan slow consumer (client dengan "
        "koneksi bandwidth sempit atau proses pembacaan lambat). Jika server menggunakan antrean tunggal bersama (shared single queue), "
        "client lambat tersebut akan menyebabkan fenomena Head-of-Line (HoL) Blocking, di mana seluruh pesan tertahan dan "
        "client cepat lainnya terhambat.",
        indent=True
    )
    add_p(
        doc,
        "Sistem ini mengatasi masalah tersebut dengan menerapkan Isolasi Antrean Mandiri per Client. Setiap client memiliki "
        "struktur queue.Queue terpisah dengan kapasitas terbatas (maxsize=100). Saat server membroadcast pesan:",
        indent=True
    )

    code_broadcast = """def broadcast_frame(self, frame: pb.ChatFrame, exclude_user_id: Optional[str] = None) -> int:
    with self._lock:
        target_queues = [(uid, q) for uid, q in self._queues.items() if uid != exclude_user_id]

    delivered_count = 0
    for uid, q in target_queues:
        try:
            q.put_nowait(frame)  # Non-blocking enqueue
            delivered_count += 1
        except queue.Full:
            # Kebijakan Drop-Oldest untuk Slow Consumer
            try:
                _ = q.get_nowait()
                q.put_nowait(frame)
                delivered_count += 1
            except Exception:
                pass
    return delivered_count"""
    add_code_block(doc, code_broadcast)

    add_p(
        doc,
        "Dengan kebijakan Drop-Oldest, antrean client yang penuh akan membuang pesan terlama secara elegan demi menerima "
        "pesan terkini. Mekanisme ini memastikan buffer memori server tetap terlindungi dari ancaman kebocoran memori (Out-Of-Memory) "
        "tanpa pernah mengorbankan kelancaran transmisi ke client lainnya.",
        indent=True
    )

    add_heading_2(doc, "3.3 Semantik At-Most-Once Melalui Deduplikasi PROSES Berbasis request_id")
    add_p(
        doc,
        "Dalam jaringan terdistribusi yang tidak stabil, kegagalan transmisi respons dapat memicu client melakukan pengiriman "
        "ulang (retry). Tanpa proteksi idempotensi, pesan yang sama akan disiarkan berulang kali ke seluruh ruang obrolan. "
        "Untuk mencegah hal ini, server menerapkan semantik eksekusi At-Most-Once menggunakan tabel memori PROSES:",
        indent=True
    )
    add_p(doc, "Setiap permintaan pesan diberi identitas unik request_id berbasis format UUID v4 di sisi client.", bold_prefix="1. Pembangkitan Identitas Unik: ")
    add_p(doc, "Ketika server menerima permintaan, server memeriksa apakah request_id sudah tercatat pada OrderedDict PROSES di bawah perlindungan lock.", bold_prefix="2. Pemeriksaan Cache PROSES: ")
    add_p(doc, "Jika request_id ditemukan, server langsung mengembalikan salinan respons sebelumnya tanpa memproses ulang logika pengiriman atau membroadcast duplikat ke client lain.", bold_prefix="3. Penanganan Cache Hit: ")
    add_p(doc, "Jika request_id baru, server menyiarkan pesan, mencatat respons ke PROSES, dan mengeliminasi entri tertua (LRU eviction) jika kapasitas melebihi batas 10.000 entri.", bold_prefix="4. Eksekusi dan Cache Miss: ")

    add_callout(
        doc,
        "Tabel deduplikasi PROSES disimpan di memori utama (RAM) server sesuai batasan arsitektur proyek mini in-memory. "
        "Pada sistem produksi berskala enterprise, struktur ini dapat diintegrasikan dengan database kunci-nilai eksternal "
        "seperti Redis yang memiliki masa kedaluwarsa waktu otomatis (TTL).",
        bold_title="CATATAN ARSITEKTUR TENTANG DEDUPLIKASI IN-MEMORY"
    )

    add_heading_2(doc, "3.4 Mekanisme Timeout dan Exponential Backoff Retry with Jitter")
    add_p(
        doc,
        "Di sisi client (src/chat_room/client.py), ketahanan koneksi diimplementasikan dengan kebijakan retry adaptif. "
        "Client tidak melakukan pengulangan secara buta, melainkan secara cerdas membedakan kesalahan permanen dan "
        "kesalahan sementara (transient):",
        indent=True
    )

    headers_err = ["Kode Status gRPC", "Klasifikasi Kesalahan", "Tindakan Client", "Alasan Teknis"]
    data_err = [
        ["DEADLINE_EXCEEDED", "Transient (Sementara)", "Retry dengan Backoff & Jitter", "Jaringan mengalami lonjakan latensi sesaat."],
        ["UNAVAILABLE", "Transient (Sementara)", "Retry dengan Backoff & Jitter", "Server sementara sibuk atau socket terputus."],
        ["RESOURCE_EXHAUSTED", "Transient (Sementara)", "Retry dengan Backoff & Jitter", "Buffer antrean penuh, menunggu pengosongan."],
        ["INVALID_ARGUMENT", "Permanent (Permanen)", "Gagal Langsung (No Retry)", "Format payload salah, retry tidak akan menyelesaikan masalah."],
        ["ALREADY_EXISTS", "Permanent (Permanen)", "Gagal Langsung (No Retry)", "Identitas konflik, memerlukan input user yang berbeda."]
    ]
    add_table_with_caption(doc, chapter_num=3, title_text="Klasifikasi Status Error gRPC dan Kebijakan Retry", headers=headers_err, data_rows=data_err, is_first_in_chapter=True, col_widths=[1.8, 1.6, 1.8, 2.0])

    add_p(
        doc,
        "Untuk mencegah fenomena Thundering Herd Problem (di mana banyak client melakukan retry serempak dan membebani server), "
        "jeda waktu pengulangan dihitung menggunakan algoritma Exponential Backoff with Full Jitter:",
        indent=True
    )

    code_retry = """delay = self.base_retry_delay * (2 ** (attempt - 1)) + random.uniform(0.01, 0.1)
time.sleep(delay)"""
    add_code_block(doc, code_retry)

    add_p(
        doc,
        "Yang paling krusial: pada setiap percobaan retry ke-1 hingga ke-N, client mempertahankan request_id yang sama persis. "
        "Dengan demikian, apabila permintaan sebelumnya sebenarnya telah berhasil dieksekusi server namun acknowledgment terputus, "
        "server akan mengenali request_id tersebut melalui tabel PROSES dan tidak akan menduplikasi siaran pesan.",
        indent=True
    )

    add_heading_2(doc, "3.5 Penanganan Client Disconnection dan Graceful Shutdown")
    add_p(
        doc,
        "Integritas sistem terdistribusi sangat bergantung pada kemampuannya membersihkan sumber daya saat terjadi terminasi:",
        indent=True
    )

    add_image_figure(
        doc,
        DIAGRAMS_DIR / "04_client_lifecycle_disconnect.png",
        chapter_num=3,
        title_text="Siklus Hidup Client dan Penanganan Disconnect",
        is_first_in_chapter=False,
        width_inches=5.8
    )

    add_p(doc, "Pada metode Chat streaming, server mendaftarkan callback pembersihan context.add_callback(cleanup). Callback ini dieksekusi secara otomatis oleh runtime gRPC saat koneksi HTTP/2 terputus—baik karena client keluar normal maupun akibat gangguan kabel jaringan / crash. Callback ini mencabut antrean pengguna, menghapus username dari tabel aktif, dan menyiarkan notifikasi keluarnya user ke partisipan lain.", bold_prefix="a. Deteksi Disconnect Otomatis: ")
    add_p(doc, "Server menangani sinyal sistem operasi SIGINT dan SIGTERM. Saat menerima sinyal penghentian, server memanggil server.stop(grace=3.0) yang memberikan jendela waktu tenggang 3 detik bagi worker thread untuk menyelesaikan pengiriman frame yang sedang berlangsung sebelum socket TCP ditutup.", bold_prefix="b. Graceful Server Shutdown: ")

    # ==========================================
    # BAB IV: PENGUJIAN DAN ANALISIS KINERJA SISTEM
    # ==========================================
    doc.add_page_break()
    add_chapter_heading(doc, "IV", "PENGUJIAN DAN ANALISIS KINERJA SISTEM")

    add_heading_2(doc, "4.1 Metodologi dan Lingkungan Pengujian Beban")
    add_p(
        doc,
        "Sesuai dengan ketentuan umum pada modul praktikum halaman 12, sistem wajib dievaluasi kinerjanya menggunakan "
        "skenario pengujian beban dengan mengukur latensi rata-rata dan throughput untuk 1, 5, dan 20 client bersamaan. "
        "Pengujian beban ini secara spesifik mengukur latensi round-trip dan throughput pengiriman pesan Unary RPC SendMessage "
        "secara berkelanjutan oleh worker thread client konkuren (50 pesan per client, total 50, 250, dan 1.000 permintaan). "
        "Operasi ini merefleksikan beban server dalam memvalidasi token, memeriksa idempotensi request_id pada tabel PROSES, "
        "memperoleh RLock ChatState, dan menyalin payload ke seluruh antrean client aktif.",
        indent=True
    )

    headers_env = ["Komponen Spesifikasi", "Karakteristik Lingkungan Pengujian Aktual"]
    data_env = [
        ["Processor (Host CPU)", "Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz (4 Core Fisik, 8 Logical Processors)"],
        ["Memori RAM Terpasang", "8.0 GB Physical RAM"],
        ["Sistem Operasi Host", "Microsoft Windows 11 Pro 64-bit (Build 26200)"],
        ["Interpreter Python", "Python 3.11.9 (CPython 64-bit) Virtual Environment"],
        ["Framework RPC & Runtime", "gRPC Python v1.85.0 & Protocol Buffers v7.36.2"],
        ["Transport Protocol", "HTTP/2 over Loopback TCP Socket (127.0.0.1:50051)"],
        ["Konfigurasi Thread Pool Server", "ThreadPoolExecutor(max_workers=50) saat pengujian beban"],
        ["Metode Pengukuran Waktu", "time.perf_counter() berpresisi nanodetik di sisi client"],
        ["Beban Permintaan per Client", "50 pesan per client (Skenario: 50, 250, dan 1.000 total pesan)"]
    ]
    add_table_with_caption(doc, chapter_num=4, title_text="Spesifikasi Lingkungan Pengujian Beban", headers=headers_env, data_rows=data_env, is_first_in_chapter=True, col_widths=[2.4, 4.4])

    add_heading_2(doc, "4.2 Tabel Rekapitulasi Data Kinerja Aktual (1, 5, dan 20 Client)")
    add_p(
        doc,
        "Berikut adalah data empiris hasil pengujian beban aktual yang diperoleh dari eksekusi benchmark tolok ukur "
        "(tercatat pada berkas benchmarks/results/benchmark_results.json dan benchmark_results.csv):",
        indent=True
    )

    headers_bench = ["Parameter Metrik Kinerja", "1 Client Konkuren", "5 Client Konkuren", "20 Client Konkuren"]
    data_bench = [
        ["Jumlah Permintaan Total", "50", "250", "1.000"],
        ["Permintaan Berhasil (Sukses)", "50 (100.0%)", "250 (100.0%)", "1.000 (100.0%)"],
        ["Permintaan Gagal (Error / Timeout)", "0 (0.0%)", "0 (0.0%)", "0 (0.0%)"],
        ["Tingkat Keberhasilan (Success Rate)", "100.0%", "100.0%", "100.0%"],
        ["Latensi Rata-rata (Mean)", "1,10 ms (1.098 ms)", "5,10 ms (5.103 ms)", "19,08 ms (19.075 ms)"],
        ["Latensi Median (P50)", "0,94 ms (0.941 ms)", "5,04 ms (5.042 ms)", "19,09 ms (19.088 ms)"],
        ["Latensi 95th Percentile (P95)", "1,82 ms (1.818 ms)", "7,07 ms (7.071 ms)", "25,70 ms (25.704 ms)"],
        ["Latensi Minimum (Min)", "0,65 ms (0.650 ms)", "1,53 ms (1.534 ms)", "2,72 ms (2.724 ms)"],
        ["Latensi Maksimum (Max)", "1,90 ms (1.903 ms)", "8,56 ms (8.562 ms)", "30,98 ms (30.976 ms)"],
        ["Throughput Sistem (req/detik)", "681,3 req/s (681.28)", "909,9 req/s (909.86)", "988,4 req/s (988.43)"],
        ["Total Durasi Pengujian Beban", "0,0734 detik", "0,2748 detik", "1,0117 detik"]
    ]
    add_table_with_caption(doc, chapter_num=4, title_text="Rekapitulasi Data Kinerja Aktual Benchmark Multi-Client", headers=headers_bench, data_rows=data_bench, is_first_in_chapter=False, col_widths=[2.4, 1.4, 1.4, 1.5], alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER])

    add_heading_2(doc, "4.3 Visualisasi Kinerja (Grafik Latensi dan Throughput)")
    add_p(
        doc,
        "Visualisasi grafis metrik kinerja digenerate secara langsung dari rekaman data JSON dan tersimpan pada berkas "
        "revisi_final/assets/charts/latency_throughput_chart.png. Nilai numerik pada grafik selaras 100% dengan data Tabel 4.2:",
        indent=True
    )

    chart_img = CHARTS_DIR / "latency_throughput_chart.png"
    add_image_figure(
        doc,
        chart_img,
        chapter_num=4,
        title_text="Grafik Analisis Latensi Rata-Rata dan Throughput Sistem (1, 5, dan 20 Client)",
        is_first_in_chapter=True,
        width_inches=5.8
    )

    add_heading_2(doc, "4.4 Analisis Kritis Kinerja Berdasarkan Teori Sistem Terdistribusi")
    add_p(
        doc,
        "Hasil pengujian empiris memperlihatkan perilaku sistem yang sangat konsisten dengan prinsip komputasi paralel dan terdistribusi:",
        indent=True
    )

    add_heading_3(doc, "A. Analisis Skalabilitas Throughput")
    add_p(
        doc,
        "Throughput sistem meningkat dari 681,28 req/s pada 1 client menjadi 909,86 req/s pada 5 client (+33.5%), "
        "dan mencapai 988,43 req/s pada 20 client (+45.1% dibandingkan baseline). Peningkatan ini menunjukkan bahwa server "
        "mampu memanfaatkan multi-core CPU (Intel Core i7-1065G7 dengan 8 logical processors) untuk memproses permintaan "
        "secara paralel melalui ThreadPoolExecutor. Tingkat pertumbuhan throughput melambat saat berpindah dari 5 ke 20 client "
        "karena waktu pemrosesan mulai dibatasi oleh lock contention pada ChatState singleton dan overhead context switching antar-thread.",
        indent=True
    )

    add_heading_3(doc, "B. Analisis Latensi dan Karakteristik Real-Time")
    add_p(
        doc,
        "Latensi rata-rata bergeser dari 1,10 ms pada 1 client, menjadi 5,10 ms pada 5 client, dan 19,08 ms pada 20 client. "
        "Pertumbuhan latensi ini bersifat sub-linear dan stabil. Nilai latensi P95 pada beban tertinggi (20 client) berada pada angka "
        "25,70 ms, dengan nilai maksimum 30,98 ms. Dalam standar sistem interaktif, ambang batas persepsi latensi manusia adalah "
        "100 ms. Dengan seluruh nilai P95 dan maksimum berada jauh di bawah 31 ms, sistem chat room terbukti sangat responsif.",
        indent=True
    )
    add_p(
        doc,
        "Selain itu, selisih antara latensi median P50 (19,09 ms) dan latensi rata-rata (19,08 ms) pada 20 client sangat tipis (di bawah 0,02 ms). "
        "Hal ini membuktikan bahwa sebaran waktu respons sangat simetris dan stabil, tanpa lonjakan ekstrim (tail latency jitter). "
        "Tingkat keberhasilan 100.0% (1.000 dari 1.000 permintaan sukses tanpa ada paket gagal atau timeout) membuktikan ketahanan "
        "concurrency management server di bawah beban kerja tinggi.",
        indent=True
    )

    add_heading_2(doc, "4.5 Hasil Verifikasi Pengujian Fungsional Otomatis (Pytest)")
    add_p(
        doc,
        "Untuk memverifikasi keandalan fungsional secara komprehensif, seluruh modul sistem diuji menggunakan rangkaian tes otomatis "
        "berbasis pytest yang mencakup 22 skenario uji unit, konkurensi, dan toleransi kegagalan:",
        indent=True
    )

    headers_pytest = ["Nama Modul Uji", "Fokus Pengujian Spesifik", "Status Hasil", "Verifikasi Teknis"]
    data_pytest = [
        ["test_join.py", "Registrasi user, validasi spasi/kosong, username duplikat, idempoten", "PASSED (4/4)", "Kode status ALREADY_EXISTS & INVALID_ARGUMENT"],
        ["test_list_users.py", "Pengambilan daftar user aktif, kondisi kosong, dan multi-user", "PASSED (2/2)", "Integritas field repeated UserInfo"],
        ["test_send_message.py", "Pengiriman pesan Unary, validasi sender dan pesan kosong", "PASSED (2/2)", "Verifikasi acknowledgment delivered_at"],
        ["test_chat_stream.py", "Bidirectional stream handshake, pesan broadcast, dan event frame", "PASSED (1/1)", "Full-duplex stream framing HTTP/2"],
        ["test_broadcast.py", "Replikasi pesan dari Client A ke Client B secara real-time", "PASSED (1/1)", "Isolasi antrean per-client terbukti bekerja"],
        ["test_concurrency.py", "Registrasi dan pengiriman pesan simultan oleh banyak thread", "PASSED (1/1)", "Bebas race condition di bawah RLock"],
        ["test_deduplication.py", "Proteksi request_id sama pada SendMessage via PROSES", "PASSED (2/2)", "Semantik at-most-once terverifikasi 100%"],
        ["test_timeout_retry.py", "Simulasi timeout gRPC, kestabilan request_id, no-retry argument", "PASSED (3/3)", "Exponential backoff with jitter tervalidasi"],
        ["test_disconnect.py", "Deteksi client terputus dan pembersihan otomatis registry users", "PASSED (1/1)", "context.add_callback() terpicu sukses"],
        ["test_queue_backpressure.py", "Kebijakan Drop-Oldest saat antrean client lambat penuh", "PASSED (1/1)", "Pencegahan Head-of-Line blocking tervalidasi"],
        ["test_server_lifecycle.py", "Inisialisasi server socket dan graceful shutdown stop(grace=3)", "PASSED (1/1)", "Pembersihan thread socket tanpa leak"],
        ["test_errors.py", "Penanganan payload korup, username whitespace, dan invalid frame", "PASSED (3/3)", "Error propagation terstandarisasi gRPC"]
    ]
    add_table_with_caption(doc, chapter_num=4, title_text="Rekapitulasi Hasil Verifikasi 22 Kasus Uji Otomatis Pytest", headers=headers_pytest, data_rows=data_pytest, is_first_in_chapter=False, col_widths=[1.8, 2.4, 1.2, 1.8], alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    add_p(
        doc,
        "Hasil pengujian otomatis menunjukkan tingkat kelulusan sempurna: 22 passed, 0 failed, 0 error dalam durasi 4,10 detik.",
        indent=True
    )

    add_heading_2(doc, "4.6 Bukti Tangkapan Layar Eksekusi Nyata Sistem (17 Bukti Visual)")
    add_p(
        doc,
        "Berikut adalah 17 dokumentasi visual resolusi tinggi yang menangkap tahapan eksekusi sistem dari sesi terminal nyata:",
        indent=True
    )

    screenshots_info = [
        ("01_project_structure.png", "Struktur Direktori Proyek dan Virtual Environment", 5.6),
        ("02_server_startup.png", "Inisialisasi Server gRPC pada Port 50051", 5.6),
        ("03_client_alice_startup.png", "Sesi Client Alice Terhubung ke Server Chat Room", 5.6),
        ("04_client_bob_startup.png", "Sesi Client Bob Terhubung ke Server Chat Room", 5.6),
        ("05_multiple_users_connected.png", "Tampilan Multi-Client Terkoneksi Simultan", 5.6),
        ("06_message_sent_alice.png", "Pengiriman Pesan Real-Time oleh Client Alice", 5.6),
        ("07_message_received_bob.png", "Penerimaan Pesan Real-Time oleh Client Bob", 5.6),
        ("08_bidirectional_exchange.png", "Pertukaran Pesan Dua Arah (Bidirectional Streaming)", 5.6),
        ("09_broadcast_behavior.png", "Pengiriman Pesan Broadcast ke Seluruh Partisipan", 5.6),
        ("10_active_user_list.png", "Eksekusi Perintah /users Menampilkan Pengguna Aktif", 5.6),
        ("11_client_disconnect.png", "Notifikasi Disconnect Saat Client Meninggalkan Chat", 5.6),
        ("12_active_users_after_disconnect.png", "Pembaruan Registry Pengguna Setelah Disconnect", 5.6),
        ("13_server_event_logs.png", "Log Peristiwa dan Audit Trail Server gRPC", 5.6),
        ("14_concurrency_test_exec.png", "Eksekusi Pengujian Konkurensi Pytest", 5.6),
        ("15_benchmark_execution.png", "Eksekusi Skrip Benchmark Beban Multi-Client (1, 5, 20 Client)", 5.6),
        ("16_docker_compose_config.png", "Validasi Konfigurasi Multi-Container Docker Compose", 5.6),
        ("17_pytest_full_suite.png", "Hasil Lengkap Eksekusi 22 Test Suite Pytest (100% Passed)", 5.6)
    ]

    for fname, caption_title, width in screenshots_info:
        img_p = SCREENSHOTS_DIR / fname
        add_image_figure(doc, img_p, chapter_num=4, title_text=caption_title, is_first_in_chapter=False, width_inches=width)

    # ==========================================
    # BAB V: PEMBAGIAN TUGAS DAN KONTRIBUSI ANGGOTA KELOMPOK
    # ==========================================
    doc.add_page_break()
    add_chapter_heading(doc, "V", "PEMBAGIAN TUGAS DAN KONTRIBUSI ANGGOTA KELOMPOK")

    add_heading_2(doc, "5.1 Rincian Kontribusi Setiap Anggota Kelompok")
    add_p(
        doc,
        "Sesuai ketentuan pada rubrik penilaian modul praktikum halaman 12–13 yang menegaskan bahwa seluruh anggota "
        "kelompok wajib memahami keseluruhan arsitektur proyek dan memiliki bukti riwayat kontribusi yang nyata, "
        "berikut adalah matriks pembagian tanggung jawab teknis:",
        indent=True
    )

    headers_team = ["Nama Mahasiswa", "NIM", "Peran Utama", "Lingkup Modul Teknis", "Status Konfirmasi"]
    data_team = [
        ["Fathir Rizki Fadillah", "247006111129", "Ketua Tim & Arsitek", "Desain IDL .proto, Arsitektur Server gRPC, Thread-Safe ChatState, Stub Generation", "Terverifikasi (Author Utama)"],
        ["[Nama Mahasiswa 2]", "[NIM 2]", "Client Engineer", "Pengembangan Client CLI Terminal, Exponential Backoff Retry, Timeout, Request ID", "Menunggu Konfirmasi Anggota"],
        ["[Nama Mahasiswa 3]", "[NIM 3]", "QA Engineer", "Otomasi 22 Tes Pytest, Docker Multi-Container, Benchmark Tolok Ukur, Analisis Laporan", "Menunggu Konfirmasi Anggota"]
    ]
    add_table_with_caption(doc, chapter_num=5, title_text="Matriks Pembagian Peran dan Tanggung Jawab Anggota Kelompok", headers=headers_team, data_rows=data_team, is_first_in_chapter=True, col_widths=[1.8, 1.2, 1.4, 2.0, 1.4], alignments=[WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    add_p(doc, "Bertanggung jawab atas arsitektur makro sistem, spesifikasi kontrak Protocol Buffers (proto/chat_room.proto), kompilasi stub otomatis (scripts/generate_stubs.py), server runtime multi-threaded (src/chat_room/server.py), serta mekanisme sinkronisasi state memori bersama (src/chat_room/state.py).", bold_prefix="1. Fathir Rizki Fadillah (Ketua Kelompok): ")
    add_p(doc, "Bertanggung jawab atas interaksi pengguna command-line (src/chat_room/client.py), manajemen thread penerima stream dan generator input, implementasi algoritma retry dengan exponential backoff dan jitter, penanganan status transient gRPC, serta pelestarian kestabilan request_id unik.", bold_prefix="2. [Anggota Pengembang 2] (Client Engineer): ")
    add_p(doc, "Bertanggung jawab atas penyusunan 22 pengujian fungsional unit dan integrasi (tests/), orkestrasi multi-container (Dockerfile dan docker-compose.yml), otomasi skrip benchmark pengujian beban 1, 5, dan 20 client (benchmarks/run_benchmark.py), serta visualisasi metrik performa.", bold_prefix="3. [Anggota Pengembang 3] (QA & Benchmark Engineer): ")

    add_heading_2(doc, "5.2 Log Riwayat Commit Repositori Git")
    add_p(
        doc,
        "Pengembangan proyek dikelola menggunakan sistem kontrol versi Git dengan repositori resmi pada GitHub. "
        "Berikut adalah bukti commit aktual yang tercatat pada riwayat repositori:",
        indent=True
    )

    headers_git = ["Hash Commit", "Penulis (Author)", "Pesan Commit (Conventional Commit)", "Lingkup Komponen"]
    data_git = [
        ["5b16ef4", "Fathir Rizki Fadillah", "feat: initial release of distributed chat room RPC system with bidirectional streaming and fault tolerance", "proto/, src/, tests/, docker"],
        ["[Staging]", "Fathir Rizki Fadillah", "perf(benchmark): add multi-client load benchmark script and plot export", "benchmarks/*"],
        ["[Staging]", "Fathir Rizki Fadillah", "test: implement 22 automated pytest unit and integration tests", "tests/*"],
        ["[Staging]", "Fathir Rizki Fadillah", "docs: complete comprehensive academic report and runbook", "docs/*, laporan/*"]
    ]
    add_table_with_caption(doc, chapter_num=5, title_text="Log Riwayat Commit Repositori Git", headers=headers_git, data_rows=data_git, is_first_in_chapter=False, col_widths=[1.2, 1.8, 3.2, 1.4], alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    # ==========================================
    # BAB VI: TAUTAN REPOSITORI GIT DAN VIDEO DEMONSTRASI
    # ==========================================
    doc.add_page_break()
    add_chapter_heading(doc, "VI", "TAUTAN REPOSITORI GIT DAN VIDEO DEMONSTRASI")

    add_heading_2(doc, "6.1 Tautan Repositori Kode Sumber")
    add_p(
        doc,
        "Seluruh kode sumber, skrip otomasi pengujian, konfigurasi containerisasi Docker, arsitektur Protobuf, "
        "serta data mentah pengujian beban proyek mini ini dipublikasikan pada repositori Git resmi:",
        indent=True
    )
    add_p(doc, "https://github.com/fathirrizkifadillah/RPC-CHAT-Tugas-KPT-.git", bold_prefix="• Tautan Repositori Resmi: ")
    add_p(doc, "main (versi stabil terverifikasi)", bold_prefix="• Cabang Utama (Branch): ")
    add_p(doc, "Tersedia berkas README.md lengkap dengan instruksi instalasi lokal virtualenv, pengoperasian multi-container Docker Compose, serta eksekusi benchmark mandiri.", bold_prefix="• Dokumentasi Repositori: ")

    add_heading_2(doc, "6.2 Rencana dan Skenario Video Demonstrasi")
    add_p(
        doc,
        "Sesuai ketentuan pengumpulan pada modul praktikum halaman 13, kelompok kami menyusun rencana demonstrasi "
        "sistem dengan durasi terencana maksimal 5 menit yang memperlihatkan fungsionalitas aplikasi dan pembuktian toleransi kegagalan:",
        indent=True
    )
    add_p(doc, "https://youtu.be/[ID_VIDEO_YOUTUBE] (Tautan siap diisi setelah rekaman demonstrasi diunggah)", bold_prefix="• Tautan Video Demonstrasi: ")
    add_p(doc, "Maksimal 5 Menit (Sesuai ketentuan batas waktu modul)", bold_prefix="• Alokasi Batas Waktu: ")

    headers_vid = ["Rentang Waktu (Timeline)", "Segmen Demonstrasi", "Aktivitas dan Pembuktian Fungsionalitas"]
    data_vid = [
        ["00:00 – 00:45", "Pendahuluan & Arsitektur", "Perkenalan anggota kelompok dan penjelasan ringkas diagram arsitektur gRPC serta pembagian tugas."],
        ["00:45 – 02:00", "Komunikasi Obrolan Real-Time", "Menjalankan gRPC server (:50051), menghubungkan Client Alice dan Bob, serta mendemonstrasikan bidirectional streaming."],
        ["02:00 – 02:45", "Fitur Unary RPC & ListUsers", "Menjalankan perintah /users untuk melihat registry online dan /unary untuk pengujian jalur pesan request-response."],
        ["02:45 – 03:30", "Toleransi Kegagalan & Disconnect", "Memutus koneksi salah satu client secara mendadak; membuktikan pembersihan otomatis server dan notifikasi leave ke client lain."],
        ["03:30 – 04:30", "Pengujian Kinerja & Pytest", "Mengeksekusi pytest (22 passed) dan skrip run_benchmark.py untuk mengukur latensi dan throughput 1, 5, dan 20 client."],
        ["04:30 – 05:00", "Penutup & Kesimpulan", "Pemaparan ringkas ketercapaian seluruh rubrik penilaian dan penutupan demonstrasi."]
    ]
    add_table_with_caption(doc, chapter_num=6, title_text="Skenario Struktur Video Demonstrasi 5 Menit", headers=headers_vid, data_rows=data_vid, is_first_in_chapter=True, col_widths=[1.5, 2.2, 3.5], alignments=[WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    # ==========================================
    # DAFTAR PUSTAKA
    # ==========================================
    doc.add_page_break()
    p_dp = doc.add_paragraph(style='Heading 1')
    p_dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_dp = p_dp.add_run("DAFTAR PUSTAKA")
    r_dp.font.name = 'Times New Roman'
    r_dp.font.size = Pt(14)
    r_dp.font.bold = True
    r_dp.font.color.rgb = RGBColor(0, 0, 0)

    references = [
        "[1]  Google LLC, \"gRPC Python Documentation and Tutorials,\" 2024. [Online]. Tersedia: https://grpc.io/docs/languages/python/.",
        "[2]  Protocol Buffers Documentation, \"Language Guide (proto3),\" 2024. [Online]. Tersedia: https://protobuf.dev/programming-guides/proto3/.",
        "[3]  A. S. Tanenbaum dan M. Van Steen, Distributed Systems: Principles and Paradigms, 3rd ed. CreateSpace Independent Publishing Platform, 2017.",
        "[4]  M. van Steen dan A. S. Tanenbaum, Distributed Systems, 4th ed., 2023. [Online]. Tersedia: https://www.distributed-systems.net/.",
        "[5]  Tim Dosen Komputasi Paralel dan Terdistribusi, \"Modul Latihan & Praktikum Remote Procedure Calls (RPC),\" Jurusan Informatika, Fakultas Teknik, Universitas Siliwangi, 2026.",
        "[6]  M. Nygard, Release It!: Design and Deploy Production-Ready Software, 2nd ed. Pragmatic Bookshelf, 2018.",
        "[7]  Python Software Foundation, \"concurrent.futures — Launching parallel tasks,\" Python 3.11 Documentation, 2024. [Online]. Tersedia: https://docs.python.org/3/library/concurrent.futures.html.",
        "[8]  IETF, \"Hypertext Transfer Protocol Version 2 (HTTP/2),\" RFC 7540, 2015. [Online]. Tersedia: https://datatracker.ietf.org/doc/html/rfc7540."
    ]

    for ref in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        r = p_ref.add_run(ref)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0, 0, 0)

    # ==========================================
    # LAMPIRAN-LAMPIRAN
    # ==========================================
    doc.add_page_break()
    p_lp = doc.add_paragraph(style='Heading 1')
    p_lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lp = p_lp.add_run("LAMPIRAN-LAMPIRAN")
    r_lp.font.name = 'Times New Roman'
    r_lp.font.size = Pt(14)
    r_lp.font.bold = True
    r_lp.font.color.rgb = RGBColor(0, 0, 0)

    add_heading_2(doc, "Lampiran A: Cuplikan Implementasi Kode Sumber Service Logic (src/chat_room/service.py)")
    add_p(doc, "Berikut adalah cuplikan implementasi utama LayananChatServicer yang menangani logika RPC Join, SendMessage, dan Chat:")
    svc_excerpt = """class LayananChatServicer(pb_grpc.LayananChatServicer):
    def __init__(self, state: ChatState):
        self.state = state

    def Join(self, request: pb.JoinRequest, context: grpc.ServicerContext) -> pb.JoinResponse:
        username = request.username.strip()
        if not username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Username tidak boleh kosong")
        
        user_id, err = self.state.add_user(username, request.client_id, request.request_id)
        if err == "ALREADY_EXISTS":
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Username '{username}' sudah digunakan")
        
        return pb.JoinResponse(
            success=True,
            message=f"Selamat datang, {username}!",
            user_id=user_id,
            joined_at=int(time.time() * 1000)
        )

    def SendMessage(self, request: pb.SendMessageRequest, context: grpc.ServicerContext) -> pb.SendMessageResponse:
        # Semantik At-Most-Once via deduplikasi PROSES
        cached = self.state.get_processed(request.request_id)
        if cached:
            return cached

        frame = pb.ChatFrame(
            type=pb.FRAME_TYPE_MESSAGE,
            request_id=request.request_id,
            sender=request.sender_username,
            content=request.content,
            timestamp=request.timestamp
        )
        self.state.broadcast_frame(frame)
        resp = pb.SendMessageResponse(
            request_id=request.request_id,
            success=True,
            message="Pesan berhasil dikirim",
            delivered_at=int(time.time() * 1000)
        )
        self.state.record_processed(request.request_id, resp)
        return resp"""
    add_code_block(doc, svc_excerpt)

    add_heading_2(doc, "Lampiran B: Cuplikan Implementasi Kode Sumber State Management (src/chat_room/state.py)")
    add_p(doc, "Berikut adalah cuplikan implementasi ChatState yang menangani antrean terisolasi dan sinkronisasi RLock:")
    state_excerpt = """class ChatState:
    def __init__(self, queue_maxsize: int = 100, max_proses: int = 10000):
        self._lock = threading.RLock()
        self._users: Dict[str, Dict[str, Any]] = {}
        self._usernames: Dict[str, str] = {}
        self._queues: Dict[str, queue.Queue] = {}
        self._proses: OrderedDict[str, Any] = OrderedDict()
        self._queue_maxsize = queue_maxsize
        self._max_proses = max_proses

    def broadcast_frame(self, frame: pb.ChatFrame, exclude_user_id: Optional[str] = None) -> int:
        with self._lock:
            target_queues = [(uid, q) for uid, q in self._queues.items() if uid != exclude_user_id]

        delivered = 0
        for uid, q in target_queues:
            try:
                q.put_nowait(frame)
                delivered += 1
            except queue.Full:
                try:
                    _ = q.get_nowait()
                    q.put_nowait(frame)
                    delivered += 1
                except Exception:
                    pass
        return delivered"""
    add_code_block(doc, state_excerpt)

    add_heading_2(doc, "Lampiran C: Data Mentah Hasil Uji Beban Benchmark (JSON & CSV)")
    add_p(doc, "Berikut adalah rekaman data mentah aktual yang dihasilkan langsung oleh skrip benchmarks/run_benchmark.py:")

    raw_json = """{
  "timestamp": "2026-11-01 16:19:27",
  "server_address": "127.0.0.1:50051",
  "results": [
    {
      "num_clients": 1,
      "messages_per_client": 50,
      "total_requests": 50,
      "connected_clients": 1,
      "success_count": 50,
      "failure_count": 0,
      "total_duration_sec": 0.0734,
      "throughput_rps": 681.28,
      "avg_latency_ms": 1.098,
      "median_latency_ms": 0.941,
      "p95_latency_ms": 1.818,
      "min_latency_ms": 0.65,
      "max_latency_ms": 1.903
    },
    {
      "num_clients": 5,
      "messages_per_client": 50,
      "total_requests": 250,
      "connected_clients": 5,
      "success_count": 250,
      "failure_count": 0,
      "total_duration_sec": 0.2748,
      "throughput_rps": 909.86,
      "avg_latency_ms": 5.103,
      "median_latency_ms": 5.042,
      "p95_latency_ms": 7.071,
      "min_latency_ms": 1.534,
      "max_latency_ms": 8.562
    },
    {
      "num_clients": 20,
      "messages_per_client": 50,
      "total_requests": 1000,
      "connected_clients": 20,
      "success_count": 1000,
      "failure_count": 0,
      "total_duration_sec": 1.0117,
      "throughput_rps": 988.43,
      "avg_latency_ms": 19.075,
      "median_latency_ms": 19.088,
      "p95_latency_ms": 25.704,
      "min_latency_ms": 2.724,
      "max_latency_ms": 30.976
    }
  ]
}"""
    add_code_block(doc, raw_json)

    raw_csv = """num_clients,messages_per_client,total_requests,connected_clients,success_count,failure_count,total_duration_sec,throughput_rps,avg_latency_ms,median_latency_ms,p95_latency_ms,min_latency_ms,max_latency_ms
1,50,50,1,50,0,0.0734,681.28,1.098,0.941,1.818,0.65,1.903
5,50,250,5,250,0,0.2748,909.86,5.103,5.042,7.071,1.534,8.562
20,50,1000,20,1000,0,1.0117,988.43,19.075,19.088,25.704,2.724,30.976"""
    add_code_block(doc, raw_csv)


def main():
    print(f"[*] Membangun dokumen Word revisi akademik: {DOCX_PATH} ...")
    doc = Document()
    configure_styles(doc)

    print("[1/3] Menyusun Halaman Cover Formal Monokromatik...")
    build_cover_page(doc)

    print("[2/3] Menyusun Front Matter (Lembar Identitas, Kata Pengantar, Daftar Isi/Gambar/Tabel)...")
    build_front_matter(doc)

    print("[3/3] Menyusun Konten Utama Akademik (BAB I - BAB VI, Daftar Pustaka, Lampiran)...")
    build_main_content(doc)

    doc.save(str(DOCX_PATH))
    print(f"[+] Dokumen Word revisi berhasil dibuat: {DOCX_PATH} ({os.path.getsize(DOCX_PATH):,} bytes)")


if __name__ == "__main__":
    main()
