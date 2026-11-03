# QA REVISION REPORT
## AUDIT, PERBAIKAN & PENJAMINAN KUALITAS DOKUMEN AKADEMIK
### Mini Project RPC — Studi Kasus 3: Distributed Real-Time Chat Room
**Mata Kuliah**: Komputasi Paralel dan Terdistribusi  
**Institusi**: Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi  
**Penulis Utama / Penanggung Jawab**: Fathir Rizki Fadillah (NIM: `247006111129`)  
**Tanggal Audit & Revisi**: 1 November 2026  
**Direktori Output Revisi**: `C:\TUGAS\KPT\RPC\laporan\mini_project_final\revisi_final\`  

---

## A. MANDATORY SKILLS EXECUTION AUDIT

Sesuai dengan instruksi *Strict Skill Execution Policy*, seluruh keahlian lokal (*Agent Skills*) yang diwajibkan telah dibaca secara menyeluruh dan diaplikasikan dalam prosedur revisi dokumen nyata:

| Nama Skill | Berkas Panduan yang Dibaca | Prosedur Nyata yang Dieksekusi |
|---|---|---|
| **`docx`** | `skills/docx/SKILL.md` | Inspeksi struktur OpenXML DOCX, manipulasi tabel, margin, field dinamis Word (`PAGE`, `TOC`, `SEQ`), serta orkestrasi COM automation. |
| **`format-agent-skill`** | `skills/format-agent-skill/SKILL.md` | Standardisasi tata letak akademik (A4, 4-3-3-3 cm, Times New Roman 12pt, spasi 1.5, penomoran Romawi/Arab, integrasi `SEQ Gambar` & `SEQ Tabel`). |
| **`code-review`** | `skills/code-review/SKILL.md` | Audit teknis kode sumber `server.py`, `service.py`, `state.py`, `client.py`, dan `run_benchmark.py` terhadap klaim dokumentasi. |
| **`statistical-analysis`** | `skills/statistical-analysis/SKILL.md` | Evaluasi parameter tendensi sentral (Mean, Median P50), variabilitas (P95, Min, Max), dan sebaran distribusi latensi/throughput. |
| **`evaluation-reality-check`** | `skills/evaluation-reality-check/SKILL.md` | Audit metodologi pengujian beban (Unary RPC SendMessage vs Stream), sinkronisasi data tabel vs grafik, dan pencegahan fabrikasi metrik. |
| **`experiment-provenance-ledger`** | `skills/experiment-provenance-ledger/SKILL.md` | Pemetaan *traceability* data mentah (`benchmark_results.json`, `benchmark_results.csv`) ke grafik visual dan tabel laporan. |

---

## B. PERBAIKAN FORMATTING & DOKUMENTASI (FORMATTING REPAIRS)

### 1. Tipografi dan Warna (Critical Issue A)
- **Eliminasi Warna Non-Formal**: Seluruh teks biru terang (*bright blue*) pada sampul, judul bab, dan penomoran telah diubah menjadi **HITAM FORMAL (`#000000`)** sesuai konvensi akademik monokromatik.
- **Warna Logo Universitas**: Logo resmi Universitas Siliwangi dipertahankan dalam warna aslinya tanpa distorsi.
- **Konsistensi Font**: Dokumen dibersihkan dari *embedded Calibri Bold*. Seluruh teks formal, judul, sub-bab, dan tabel 100% menggunakan **Times New Roman** (Body: 12pt regular; Judul Bab: 14pt bold; Sub-bab: 12pt bold). Potongan kode program menggunakan **Consolas 9.5pt**.
- **Neutral Styling**: Kotak catatan (*callout box*) dan tabel menggunakan aksen abu-abu netral (*neutral slate gray* `#475569` dan `#F8FAFC`).

### 2. Eliminasi Duplikasi Daftar Isi (Critical Issue B)
- **Masalah Sebelumnya**: Halaman 4–7 memuat dua versi Daftar Isi (satu otomatis dengan angka Arab dan satu tabel manual "Daftar Isi Dokumen Laporan" dengan angka Romawi).
- **Perbaikan**: Menghapus seluruh tabel manual duplikat. Kini dokumen hanya memiliki **TEPAT SATU DAFTAR ISI OTOMATIS** berbasis field Word `TOC \o "1-3" \h \z \u` dengan *dot leaders* dan nomor halaman dinamis.

### 3. Perbaikan Daftar Gambar dan Daftar Tabel (Critical Issue C)
- **Masalah Sebelumnya**: Halaman 8 dan 10 memunculkan teks galat:  
  `Error! No table of figures entries found.`  
  diikuti oleh tabel rekapitulasi manual.
- **Akar Penyebab Teknis**: Mesin *Table of Figures* Word hanya mengenali paragraf *caption* yang memuat field sequence `{ SEQ Gambar }` atau `{ SEQ Tabel }`. Skrip sebelumnya tidak menyertakan field tersebut.
- **Perbaikan Nyata**:
  - Seluruh *caption* gambar kini disisipkan field dinamis `Gambar {chapter}.{ SEQ Gambar } [Judul]`.
  - Seluruh *caption* tabel disisipkan field dinamis `Tabel {chapter}.{ SEQ Tabel } [Judul]`.
  - Tabel administratif identitas proyek dikeluarkan dari penomoran `SEQ Tabel` agar tidak mengotori daftar tabel teknis.
  - Memanggil `doc.TablesOfFigures(i).Update()` melalui Word COM.
  - **Hasil**: Teks galat `Error! No table of figures entries found.` **HILANG 100%**. Daftar Gambar dan Daftar Tabel kini tampil rapi dan otomatis.

### 4. Perbaikan Struktur Judul Bab (Critical Issue D)
- **Masalah Sebelumnya**: Pada Daftar Isi sebelumnya, teks judul bab tertempel tanpa spasi:  
  `BAB IDESKRIPSI STUDI KASUS...`, `BAB IIISTRATEGI CONCURRENCY...`, dll.
- **Perbaikan**: Memperbaiki pemisahan baris dengan menyertakan spasi eksplisit sebelum *break* (`BAB I \nDESKRIPSI...`). Daftar Isi kini menampilkan entri yang bersih:  
  `BAB I DESKRIPSI STUDI KASUS DAN DIAGRAM ARSITEKTUR`.
- **Eliminasi Artefak Markdown**: Seluruh karakter *backticks* (`` ` ``) dan *asterisks* (`*`) pada judul bab dan sub-bab telah dihapus sepenuhnya.

### 5. Penomoran Halaman (Pagination)
- **Halaman Sampul (Cover)**: Bersih tanpa nomor halaman.
- **Front Matter (Lembar Identitas s.d. Daftar Tabel)**: Angka Romawi kecil (`i`, `ii`, `iii`, `iv`, `v`) di posisi tengah bawah.
- **Bagian Utama (BAB I s.d. Lampiran)**: Angka Arab dimulai kembali dari nomor `1` pada BAB I di posisi tengah bawah.
- **Running Header**: Header miring 8.5pt di kanan atas berbunyi *"Laporan Tugas Proyek Mini — Komputasi Paralel dan Terdistribusi"*.

---

## C. PERBAIKAN & VERIFIKASI TEKNIS (TECHNICAL CORRECTIONS)

### 1. Rekonsiliasi Integritas Data Kinerja (Critical Issue F — HIGH PRIORITY)
- **Masalah Sebelumnya**: Terjadi ketidaksesuaian kritis di mana Tabel 4.2 mencantumkan hasil uji lama (0.70 ms, 1.048 req/s), sementara grafik visualisasi menampilkan hasil uji aktual (1.10 ms, 681.3 req/s).
- **Hasil Investigasi Provenance**: Berkas hasil uji riil pada `benchmarks/results/benchmark_results.json` dan `benchmark_run_log.txt` merekam eksekusi tanggal 1 November 2026 pukul 16:19:27.
- **Tindakan Perbaikan**:
  - Memutakhirkan Tabel 4.2 agar **100% IDENTIK** dengan berkas mentah JSON dan CSV.
  - Menghasilkan ulang grafik batang `latency_throughput_chart.png` dengan desain monokromatik/slate yang elegan dan angka yang cocok presisi.
  - Memperbarui narasi analisis di BAB IV berdasarkan data riil tersebut:

```
+------------------------------------+-------------------+-------------------+--------------------+
| Parameter Metrik Evaluasi Kinerja  | 1 Client Konkuren | 5 Client Konkuren | 20 Client Konkuren |
+------------------------------------+-------------------+-------------------+--------------------+
| Total Permintaan (Requests)        | 50                | 250               | 1.000              |
| Permintaan Berhasil (Sukses)       | 50 (100.0%)       | 250 (100.0%)      | 1.000 (100.0%)     |
| Permintaan Gagal (Error / Timeout) | 0 (0.0%)          | 0 (0.0%)          | 0 (0.0%)           |
| Tingkat Keberhasilan (Rate)        | 100.0%            | 100.0%            | 100.0%             |
| Latensi Rata-rata (Mean)           | 1,10 ms (1.098 ms)| 5,10 ms (5.103 ms)| 19,08 ms (19.075 ms|
| Latensi Median (P50)               | 0,94 ms (0.941 ms)| 5,04 ms (5.042 ms)| 19,09 ms (19.088 ms|
| Latensi 95th Percentile (P95)      | 1,82 ms (1.818 ms)| 7,07 ms (7.071 ms)| 25,70 ms (25.704 ms|
| Latensi Minimum                    | 0,65 ms (0.650 ms)| 1,53 ms (1.534 ms)| 2,72 ms (2.724 ms) |
| Latensi Maksimum                   | 1,90 ms (1.903 ms)| 8,56 ms (8.562 ms)| 30,98 ms (30.976 ms|
| Throughput Sistem                  | 681,3 req/s       | 909,9 req/s       | 988,4 req/s        |
| Durasi Total Pengujian             | 0,0734 detik      | 0,2748 detik      | 1,0117 detik       |
+------------------------------------+-------------------+-------------------+--------------------+
```

- **Klarifikasi Lingkup Pengukuran**: Menjelaskan secara transparan bahwa benchmark mengukur latensi *round-trip* dan *throughput* pengiriman pesan Unary RPC `SendMessage` yang dikirimkan secara serentak oleh *worker threads* client, merefleksikan beban *thread contention* dan *deduplication lookup* pada server.

### 2. Penyelarasan Konfigurasi ThreadPoolExecutor & Spesifikasi Host (Critical Issue G)
- **Konfigurasi Server**: Menjelaskan kontradiksi sebelumnya (`max_workers=30` vs `50`). Kode sumber `config.py` dan `server.py` secara default mengalokasikan **30 worker threads** untuk *runtime* reguler, sedangkan skrip tolok ukur beban `run_benchmark.py` sengaja menginisialisasi **50 worker threads** untuk menyediakan ruang tampung (*headroom*) bagi 20 client bersamaan tanpa *thread starvation*.
- **Spesifikasi Perangkat Keras Nyata**: Mengganti teks generik (*AMD Ryzen / Intel Core*) dengan spesifikasi riil yang diinspeksi langsung dari PowerShell Windows:
  - Processor: `Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz` (4 Core Fisik, 8 Logical Processors)
  - Memori RAM: `8.0 GB Physical RAM`
  - Sistem Operasi: `Microsoft Windows 11 Pro 64-bit (Version 10.0.26200, Build 26200)`
  - Lingkungan Python: `Python 3.11.9 (CPython)`
  - Pustaka: `gRPC v1.85.0`, `Protocol Buffers v7.36.2`

### 3. Penomoran Gambar di Dalam Karya Seni Diagram (Critical Issue E)
- **Masalah Sebelumnya**: Pada diagram arsitektur terdapat teks hardcoded seperti `Gambar 3.1` atau `Gambar 3.5` yang bertentangan dengan nomor caption Word (misal: `Gambar 1.1`).
- **Perbaikan**: Seluruh teks penomoran internal di dalam diagram telah dihapus menggunakan skrip `generate_revised_visuals.py`, menyisakan hanya judul deskriptif. Caption eksternal Word kini menjadi **satu-satunya rujukan otoritatif** untuk nomor gambar.

### 4. Validasi Git History & Kontribusi Tim (Critical Issue H & I)
- **Repositori Riil**: Menghubungkan ke remote Git nyata:  
  `https://github.com/fathirrizkifadillah/RPC-CHAT-Tugas-KPT-.git` (cabang `main`).
- **Commit Riil**: Mencantumkan commit otentik `5b16ef4` oleh Fathir Rizki Fadillah.
- **Eliminasi Data Dummy**: Menghapus persentase kontribusi fiktif (35%, 33%, 32%) dan hash commit buatan (`a1b2c3d`, dll). Identitas anggota 2 dan 3 ditandai secara transparan sebagai *placeholder* yang menunggu konfirmasi pengguna.
- **Klarifikasi Video Demonstrasi**: Menghapus klaim durasi video 4 menit 50 detik yang belum direkam. Skenario video 5 menit diposisikan sebagai *rencana struktur demonstrasi terencana*.

### 5. Penyempurnaan Lampiran (Critical Issue J)
- **Lampiran A**: Diubah dari kode terpotong menjadi *"Cuplikan Implementasi Kode Sumber Service Logic (`src/chat_room/service.py`)"* dengan potongan kode inti yang bersih dan berbobot.
- **Lampiran B**: Diubah menjadi *"Cuplikan Implementasi Kode Sumber State Management (`src/chat_room/state.py`)"*.
- **Lampiran C**: Menyajikan data mentah riil `benchmark_results.json` dan `benchmark_results.csv` secara lengkap.

### 6. Lembar Identitas & Integritas Akademik (Critical Issue K)
- Halaman diubah menjadi **"LEMBAR IDENTITAS PROYEK"** (bukan pengesahan karena belum ditandatangani pengampu).
- Pernyataan integritas akademik dilengkapi blok tanda tangan konfirmasi untuk *human review*.

---

## D. MATRIKS VALIDASI KUALITAS VISUAL (VISUAL QA CHECKLIST)

| Komponen Dokumen | Kriteria Kualitas Evaluasi | Status Hasil | Catatan Verifikasi Visual |
|---|---|:---:|---|
| **Halaman Sampul (Cover)** | Desain monokromatik hitam formal, logo UNSIL warna asli, tanpa nomor halaman. | **PASS** | Teks hitam formal, logo UNSIL 2.1 inci di tengah, bersih tanpa *blue text*. |
| **Lembar Identitas Proyek** | Tabel administratif bersih, pernyataan integritas, blok tanda tangan. | **PASS** | Pas 1 halaman penuh (Halaman `i`), tabel rapi, tidak memicu `SEQ Tabel`. |
| **Kata Pengantar** | Redaksi akademik formal, bebas frasa redundan, tanda tangan kota/tanggal. | **PASS** | Halaman `ii`, redaksi *“studi kasus yang representatif”* tervalidasi. |
| **Daftar Isi (TOC)** | Tepat 1 TOC otomatis Word, dot leaders, nomor halaman akurat, tanpa duplikat. | **PASS** | Halaman `iii`–`iv`, field `TOC \o "1-3" \h \z \u` terupdate sempurna. |
| **Daftar Gambar (TOF)** | Tepat 1 TOF otomatis Word, bebas teks error, nomor `Gambar X.Y` runtut. | **PASS** | Halaman `v`, 23 entri gambar terdaftar lengkap tanpa pesan galat. |
| **Daftar Tabel (TOT)** | Tepat 1 TOT otomatis Word, bebas teks error, nomor `Tabel X.Y` runtut. | **PASS** | Halaman `vi`, 8 entri tabel teknis terdaftar lengkap tanpa tabel administratif. |
| **BAB I (Arsitektur)** | Penomoran Arab mulai halaman 1, 3 diagram beresolusi tinggi tanpa nomor internal. | **PASS** | Halaman 1–4, diagram 01, 02, 03 tertanam proporsional, caption `Gambar 1.1`–`1.3`. |
| **BAB II (Protobuf IDL)** | Listing syntax proto3 dalam kotak Consolas, tabel enum `FrameType`. | **PASS** | Halaman 5–8, kode proto terformat rapi dengan latar `#F8FAFC`, `Tabel 2.1`. |
| **BAB III (Concurrency)** | Diagram state dedup & lifecycle disconnect, penjelasan RLock & Drop-Oldest. | **PASS** | Halaman 9–14, diagram 05 (`Gambar 3.1`) & 04 (`Gambar 3.2`), `Tabel 3.1`. |
| **BAB IV (Kinerja & Bukti)** | Tabel 4.2 cocok dengan Grafik 4.1, 17 screenshot terminal, 22 tes pytest. | **PASS** | Halaman 15–29, data 1.10 ms / 681.3 req/s cocok 100%, 17 screenshot terbaca jelas. |
| **BAB V (Kontribusi Tim)** | Matriks tanggung jawab transparan, riwayat Git aktual remote GitHub. | **PASS** | Halaman 30–31, tanpa hash palsu, status konfirmasi anggota jelas. |
| **BAB VI (Tautan & Video)** | Repositori GitHub resmi, skenario demonstrasi 5 menit terstruktur. | **PASS** | Halaman 32–33, tautan aktif, jadwal demonstrasi realistis. |
| **Daftar Pustaka** | Standar IEEE, 8 referensi primer (gRPC, Tanenbaum, RFC 7540, Python docs). | **PASS** | Halaman 34, format *hanging indent* rapi. |
| **Lampiran A, B, C** | Cuplikan kode service dan state, dump lengkap JSON & CSV benchmark. | **PASS** | Halaman 35–38, data mentah dapat diverifikasi dan diaudit langsung. |
| **Inspeksi Halaman PDF** | Total 46 halaman, zero blank pages, zero text overlapping. | **PASS** | Diaudit via PyMuPDF: 46 halaman valid, 0 halaman kosong. |

---

## E. BERKAS HASIL AKHIR PADA DIREKTORI REVISI

Semua artefak revisi tersedia di `C:\TUGAS\KPT\RPC\laporan\mini_project_final\revisi_final\`:

1. [**`LAPORAN_MINI_PROJECT_RPC_REVISI.docx`**](file:///C:/TUGAS/KPT/RPC/laporan/mini_project_final/revisi_final/LAPORAN_MINI_PROJECT_RPC_REVISI.docx) (1.99 MB) — Dokumen Microsoft Word hasil perbaikan penuh, siap diedit jika diperlukan penyesuaian nama kelompok.
2. [**`LAPORAN_MINI_PROJECT_RPC_REVISI.pdf`**](file:///C:/TUGAS/KPT/RPC/laporan/mini_project_final/revisi_final/LAPORAN_MINI_PROJECT_RPC_REVISI.pdf) (2.85 MB) — Dokumen PDF akademik 46 halaman tervalidasi visual sempurna, siap dikumpulkan ke dosen.
3. [**`QA_REVISION_REPORT.md`**](file:///C:/TUGAS/KPT/RPC/laporan/mini_project_final/revisi_final/QA_REVISION_REPORT.md) — Dokumen laporan penjaminan kualitas ini.
4. Direktori `assets/diagrams/`, `assets/charts/`, dan `assets/screenshots/` memuat seluruh berkas sumber visual beresolusi tinggi (300 DPI).

---

## F. INFORMASI YANG MEMERLUKAN TINDAKAN PENGGUNA (REMAINING USER INPUT)

Sebelum pengumpulan akhir ke portal akademik / LMS:
1. **Nama & NIM Rekan Kelompok (Jika Berkelompok)**:  
   Jika proyek ini dikumpulkan sebagai tugas kelompok beranggotakan 2 atau 3 mahasiswa, buka [**`LAPORAN_MINI_PROJECT_RPC_REVISI.docx`**](file:///C:/TUGAS/KPT/RPC/laporan/mini_project_final/revisi_final/LAPORAN_MINI_PROJECT_RPC_REVISI.docx) dan gantikan teks placeholder `[Anggota Kelompok 2]` serta `[NIM Mahasiswa 2]` pada Halaman Sampul, Lembar Identitas, dan Tabel 5.1 dengan data asli rekan Anda. Jika dikerjakan individu, bagian anggota tambahan dapat dihapus.
2. **Perekaman Video Demonstrasi (Maksimal 5 Menit)**:  
   Lakukan perekaman video mengikuti panduan skenario pada Tabel 6.1 (BAB VI Halaman 32–33), unggah rekaman ke YouTube / Google Drive, lalu masukkan tautan URL video tersebut ke berkas dokumen.
