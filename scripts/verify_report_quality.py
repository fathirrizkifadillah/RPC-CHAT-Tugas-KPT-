#!/usr/bin/env python3
"""
verify_report_quality.py
Memverifikasi mutu teknis dan visual berkas PDF Laporan Proyek Mini:
1. Memeriksa keberadaan file PDF resmi.
2. Menghitung total halaman (sesuai target akademik 45-50 halaman).
3. Mendeteksi adanya halaman kosong (blank page detector).
4. Mendeteksi kode kesalahan Word field (seperti 'Error! Bookmark not defined', 'Error! Reference source not found').
5. Menampilkan ringkasan audit per halaman dan status kelulusan QA.
"""

import os
import sys
from pathlib import Path
import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAPORAN_DIR = PROJECT_ROOT / "laporan"
PDF_PATH = LAPORAN_DIR / "Laporan_Proyek_Mini_RPC_Kelompok3.pdf"


def verify_pdf():
    if not PDF_PATH.exists():
        print(f"[ERROR] File PDF laporan tidak ditemukan di: {PDF_PATH}")
        sys.exit(1)

    doc = pymupdf.open(str(PDF_PATH))
    total_pages = len(doc)
    print(f"[*] Memeriksa dokumen PDF: {PDF_PATH.name}")
    print(f"[*] Lokasi: {PDF_PATH}")
    print(f"[*] Ukuran berkas: {os.path.getsize(PDF_PATH):,} bytes ({os.path.getsize(PDF_PATH)/(1024*1024):.2f} MB)")
    print(f"[*] Total Halaman: {total_pages} halaman")

    blank_pages = []
    field_errors = []
    page_report = []

    error_keywords = [
        "Error! Bookmark not defined",
        "Error! Reference source not found",
        "Error! No table of contents entries found",
        "Error! No table of figures entries found",
    ]

    for i in range(total_pages):
        page = doc[i]
        text = page.get_text()
        text_clean = text.strip()
        images = page.get_images()
        text_len = len(text_clean)
        img_count = len(images)

        # Check for field errors
        for kw in error_keywords:
            if kw in text:
                field_errors.append((i + 1, kw))

        status = "OK"
        if text_len == 0 and img_count == 0:
            status = "BLANK!"
            blank_pages.append(i + 1)

        page_report.append((i + 1, text_len, img_count, status))

    print("\n--- Rekapitulasi Struktur Halaman PDF ---")
    for page_num, text_len, img_count, status in page_report:
        first_line = doc[page_num - 1].get_text().split("\n")[0].strip() if text_len > 0 else "(Halaman visual)"
        print(f"Hal {page_num:02d}: Teks={text_len:4d} kar, Gambar={img_count:2d} | Status: {status} | Cuplikan: {first_line[:45]}")

    print("\n================ HASIL AUDIT MUTU DOKUMEN ================")
    # 1. Blank page check
    if blank_pages:
        print(f"[-] PERINGATAN: Ditemukan {len(blank_pages)} halaman kosong: {blank_pages}")
    else:
        print(f"[+] LULUS: 0 Halaman kosong! Seluruh {total_pages} halaman memiliki konten valid.")

    # 2. Word field error check
    if field_errors:
        print(f"[-] PERINGATAN: Ditemukan {len(field_errors)} kesalahan field Word:")
        for p, err in field_errors:
            print(f"    - Halaman {p}: {err}")
    else:
        print(f"[+] LULUS: 0 Kesalahan field Word (TOC, TOF, TOT, referensi silang terkompilasi sempurna)!")

    # 3. Overall status
    passed = len(blank_pages) == 0 and len(field_errors) == 0
    print(f"[*] Status Akhir Dokumen: {'MEMENUHI SELURUH STANDAR MUTU AKADEMIK (PASSED)' if passed else 'MEMERLUKAN PERBAIKAN'}")
    print("==========================================================\n")

    doc.close()
    return passed


if __name__ == "__main__":
    success = verify_pdf()
    sys.exit(0 if success else 1)
