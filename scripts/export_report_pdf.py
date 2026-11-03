#!/usr/bin/env python3
"""
export_report_pdf.py
Mengotomatisasi Microsoft Word COM untuk:
1. Membuka Laporan_Proyek_Mini_RPC_Kelompok3.docx.
2. Memperbarui seluruh field dokumen (nomor halaman, SEQ, referensi silang).
3. Memperbarui TablesOfContents dan TablesOfFigures/Tables secara otomatis.
4. Menyimpan dokumen DOCX yang telah tersinkronisasi.
5. Mengekspor PDF beresolusi tinggi (wdFormatPDF / FileFormat=17).
6. Menutup aplikasi Word dengan aman tanpa process hanging.
"""

import os
import sys
from pathlib import Path
import win32com.client
import pythoncom

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAPORAN_DIR = PROJECT_ROOT / "laporan"
DOCX_PATH = LAPORAN_DIR / "Laporan_Proyek_Mini_RPC_Kelompok3.docx"
PDF_PATH = LAPORAN_DIR / "Laporan_Proyek_Mini_RPC_Kelompok3.pdf"


def update_and_export():
    if not DOCX_PATH.exists():
        print(f"[ERROR] Berkas DOCX tidak ditemukan di: {DOCX_PATH}")
        sys.exit(1)

    print(f"[*] Menginisialisasi Microsoft Word COM Automation...")
    pythoncom.CoInitialize()

    word = None
    doc = None
    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False

        print(f"[*] Membuka dokumen laporan: {DOCX_PATH} ...")
        doc = word.Documents.Open(str(DOCX_PATH), ReadOnly=False)

        print("[*] Memperbarui seluruh field dokumen...")
        doc.Fields.Update()

        print(f"[*] Memperbarui {doc.TablesOfContents.Count} Table(s) of Contents...")
        for i in range(1, doc.TablesOfContents.Count + 1):
            try:
                doc.TablesOfContents(i).Update()
            except Exception as e:
                print(f"[WARN] Error updating TOC {i}: {e}")

        print(f"[*] Memperbarui {doc.TablesOfFigures.Count} Table(s) of Figures/Tables...")
        for i in range(1, doc.TablesOfFigures.Count + 1):
            try:
                doc.TablesOfFigures(i).Update()
            except Exception as e:
                print(f"[WARN] Error updating TOF/TOT {i}: {e}")

        doc.Save()
        print(f"[+] Berkas DOCX berhasil dimutakhirkan dan disimpan.")

        print(f"[*] Mengekspor dokumen ke format PDF: {PDF_PATH} ...")
        doc.SaveAs(str(PDF_PATH), FileFormat=17)
        print(f"[+] Berkas PDF resmi berhasil diekspor: {PDF_PATH} ({os.path.getsize(PDF_PATH):,} bytes)")

    except Exception as e:
        print(f"[ERROR] Gagal memproses via Word COM: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if doc is not None:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        if word is not None:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()

    print("[*] Proses ekspor selesai sempurna!")


if __name__ == "__main__":
    update_and_export()
