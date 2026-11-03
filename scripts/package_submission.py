#!/usr/bin/env python3
"""
package_submission.py
Script pengemasan berkas pengumpulan Proyek Mini Sistem Terdistribusi Berbasis RPC
sesuai ketentuan akademik pada panduan 'Latihan & Praktikum RPC' (halaman 13):
Format berkas: Kelompok<no>_ProyekRPC.zip (berisi laporan PDF dan kode sumber).

Studi Kasus 3: Real-Time Distributed Chat Room dengan gRPC dan Protocol Buffers.
Kelompok: Kelompok 3
Nama File Output: Kelompok3_ProyekRPC.zip
"""

import os
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAPORAN_DIR = PROJECT_ROOT / "laporan"
ZIP_PATH = LAPORAN_DIR / "Kelompok3_ProyekRPC.zip"

INCLUDE_DIRS = ["proto", "src", "tests", "benchmarks", "docs", "scripts"]
INCLUDE_ROOT_FILES = [
    "Dockerfile",
    "docker-compose.yml",
    "README.md",
    "requirements.txt",
    "HUMAN_RUNBOOK.md",
    "pyproject.toml",
    ".dockerignore",
    ".gitignore",
    "arsitektur-chat-room.svg",
]


def create_submission_zip():
    print(f"[*] Menyiapkan paket arsip pengumpulan resmi: {ZIP_PATH} ...")
    LAPORAN_DIR.mkdir(parents=True, exist_ok=True)

    pdf_path = LAPORAN_DIR / "Laporan_Proyek_Mini_RPC_Kelompok3.pdf"
    docx_path = LAPORAN_DIR / "Laporan_Proyek_Mini_RPC_Kelompok3.docx"
    qa_path = LAPORAN_DIR / "QA_REVISION_REPORT.md"

    if not pdf_path.exists():
        print(f"[!] PERINGATAN: Laporan PDF utama tidak ditemukan di {pdf_path}")

    with zipfile.ZipFile(str(ZIP_PATH), "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Tambahkan Laporan Utama PDF (Wajib sesuai ketentuan Halaman 13)
        if pdf_path.exists():
            zf.write(pdf_path, arcname="Laporan_Proyek_Mini_RPC_Kelompok3.pdf")
            print(f"  + Ditambahkan ke root ZIP: Laporan_Proyek_Mini_RPC_Kelompok3.pdf")

        # 2. Tambahkan Naskah Word DOCX & Laporan QA sebagai pelengkap transparansi
        if docx_path.exists():
            zf.write(docx_path, arcname="Laporan_Proyek_Mini_RPC_Kelompok3.docx")
            print(f"  + Ditambahkan ke root ZIP: Laporan_Proyek_Mini_RPC_Kelompok3.docx")
        if qa_path.exists():
            zf.write(qa_path, arcname="QA_REVISION_REPORT.md")
            print(f"  + Ditambahkan ke root ZIP: QA_REVISION_REPORT.md")

        # 3. Tambahkan File Konfigurasi dan Dokumentasi Root
        for fname in INCLUDE_ROOT_FILES:
            fpath = PROJECT_ROOT / fname
            if fpath.exists():
                zf.write(fpath, arcname=f"source_code/{fname}")
                print(f"  + Ditambahkan: source_code/{fname}")

        # 4. Tambahkan Direktori Kode Sumber, Pengujian, Benchmark, dan Panduan
        for dname in INCLUDE_DIRS:
            dpath = PROJECT_ROOT / dname
            if dpath.exists():
                for root, dirs, files in os.walk(dpath):
                    # Filter out cache directories and venv
                    dirs[:] = [
                        d for d in dirs
                        if d not in ("__pycache__", ".pytest_cache") and not d.endswith(".egg-info")
                    ]
                    for file in files:
                        if file.endswith((".pyc", ".pyo", ".tmp")):
                            continue
                        full_p = Path(root) / file
                        rel_p = full_p.relative_to(PROJECT_ROOT)
                        zf.write(full_p, arcname=f"source_code/{rel_p.as_posix()}")
                        print(f"  + Ditambahkan: source_code/{rel_p.as_posix()}")

    file_size_mb = os.path.getsize(ZIP_PATH) / (1024 * 1024)
    print(f"[+] Pengemasan berhasil! Berkas: {ZIP_PATH.name} ({file_size_mb:.2f} MB)")


if __name__ == "__main__":
    create_submission_zip()
