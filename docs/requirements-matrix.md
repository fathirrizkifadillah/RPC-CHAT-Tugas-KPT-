# Matriks Persyaratan Proyek (Requirements Matrix)

Matriks ini memetakan seluruh persyaratan dari PDF Tugas Praktikum RPC (Halaman 12–13), diagram arsitektur `arsitektur-chat-room.svg`, serta rubrik penilaian resmi.

Definisi Status:
- **`NOT IMPLEMENTED`**: Komponen atau fitur belum dibuat.
- **`IMPLEMENTED`**: Kode atau konfigurasi telah dibuat dan divalidasi sintaksnya, tetapi pengujian eksekusi langsung tertunda (misal Docker daemon belum aktif).
- **`TESTED`**: Pengujian otomatis atau verifikasi eksekusi telah berhasil dijalankan pada lingkungan aktif dan buktinya tersimpan.
- **`PENDING HUMAN VERIFICATION`**: Memerlukan tindakan fisik, perekaman video, atau verifikasi langsung oleh mahasiswa.

---

## 1. Persyaratan Arsitektur dan Antarmuka gRPC (`.proto`) — Bobot 15%

| ID | Deskripsi Persyaratan | Komponen/File Terkait | Bukti Pengujian | Status Aktual |
|---|---|---|---|---|
| REQ-01 | Kontrak antarmuka didefinisikan dalam `.proto` dengan minimal 4 RPC | `proto/chat_room.proto` | Kompilasi protoc berhasil & 22 tes unit lulus | **TESTED** |
| REQ-02 | RPC 1: `Join` (registrasi pengguna baru/sesi) | `src/chat_room/service.py` | `tests/test_join.py` (4 skenario lulus) | **TESTED** |
| REQ-03 | RPC 2: `ListUsers` (pengambilan daftar user aktif) | `src/chat_room/service.py` | `tests/test_list_users.py` (2 skenario lulus) | **TESTED** |
| REQ-04 | RPC 3: `SendMessage` (pengiriman pesan unary dengan request ID) | `src/chat_room/service.py` | `tests/test_send_message.py` (2 skenario lulus) | **TESTED** |
| REQ-05 | RPC 4: `Chat` (bidirectional streaming real-time) | `src/chat_room/service.py` | `tests/test_chat_stream.py` & `test_broadcast.py` | **TESTED** |
| REQ-06 | Format transport HTTP/2 dan binding port 50051 | `src/chat_room/server.py` | `tests/test_server_lifecycle.py` | **TESTED** |

---

## 2. Shared State dan Concurrency di Memori Server — Bobot 20%

| ID | Deskripsi Persyaratan | Komponen/File Terkait | Bukti Pengujian | Status Aktual |
|---|---|---|---|---|
| REQ-07 | Server menggunakan `ThreadPoolExecutor` dengan worker terkonfigurasi | `src/chat_room/server.py` | `tests/test_server_lifecycle.py` | **TESTED** |
| REQ-08 | Komponen `users`: daftar pengguna aktif dilindungi sinkronisasi (`Lock`) | `src/chat_room/state.py` | `tests/test_concurrency.py` (20 worker konkuren) | **TESTED** |
| REQ-09 | Komponen `queue`: antrean pesan per client dengan isolasi & batas kapasitas | `src/chat_room/state.py` | `tests/test_queue_backpressure.py` | **TESTED** |
| REQ-10 | Komponen `PROSES`: deduplikasi pesan berdasarkan `request_id` unik | `src/chat_room/state.py` | `tests/test_deduplication.py` | **TESTED** |
| REQ-11 | Broadcast pesan ke seluruh client aktif secara aman tanpa race condition | `src/chat_room/service.py` | `tests/test_broadcast.py` (Client A $\to$ Client B) | **TESTED** |
| REQ-12 | Pembersihan pengguna dan antrean saat client terputus (disconnect) | `src/chat_room/service.py` | `tests/test_disconnect.py` | **TESTED** |

---

## 3. Client Terminal CLI dan Toleransi Kegagalan — Bobot 15%

| ID | Deskripsi Persyaratan | Komponen/File Terkait | Bukti Pengujian | Status Aktual |
|---|---|---|---|---|
| REQ-13 | Client CLI interaktif (kirim & terima pesan real-time) | `src/chat_room/client.py` | `tests/test_broadcast.py` & eksekusi CLI | **TESTED** |
| REQ-14 | Client menerapkan timeout pada pemanggilan RPC unary | `src/chat_room/client.py` | `tests/test_timeout_retry.py` | **TESTED** |
| REQ-15 | Client menerapkan retry dengan exponential backoff pada status error yang layak | `src/chat_room/client.py` | `tests/test_timeout_retry.py` | **TESTED** |
| REQ-16 | Operasi non-idempoten mempertahankan `request_id` yang sama saat retry | `src/chat_room/client.py` | `tests/test_deduplication.py` & `test_timeout_retry.py` | **TESTED** |
| REQ-17 | Graceful exit client: unregistering dan penutupan stream secara tertib | `src/chat_room/client.py` | `tests/test_disconnect.py` | **TESTED** |

---

## 4. Lingkungan Pengembangan dan Containerisasi — Bobot 25%

| ID | Deskripsi Persyaratan | Komponen/File Terkait | Bukti Pengujian | Status Aktual |
|---|---|---|---|---|
| REQ-18 | Virtual environment Python 3.10+ terverifikasi (`venv`) | `venv/`, `docs/environment-setup.md` | `sys.executable` verified Python 3.11.9 | **TESTED** |
| REQ-19 | Pengelolaan dependensi via `requirements.txt` dan `pyproject.toml` | `requirements.txt`, `pyproject.toml` | `pip check` (No broken requirements found) | **TESTED** |
| REQ-20 | Dockerfile multi-stage / non-root user untuk server dan client | `Dockerfile`, `.dockerignore` | Konfigurasi valid; build tertunda daemon | **IMPLEMENTED** |
| REQ-21 | Komunikasi antar-container minimal 2 container via `docker-compose.yml` | `docker-compose.yml` | Validasi `docker compose config` lulus | **PENDING HUMAN VERIFICATION** |

---

## 5. Pengujian Kinerja dan Benchmark (1, 5, 20 Client) — Bobot 15%

| ID | Deskripsi Persyaratan | Komponen/File Terkait | Bukti Pengujian | Status Aktual |
|---|---|---|---|---|
| REQ-22 | Skrip benchmark pengujian 1 client bersamaan (latensi & throughput) | `benchmarks/run_benchmark.py` | Latensi 0.70 ms, Throughput 1,048 req/s | **TESTED** |
| REQ-23 | Skrip benchmark pengujian 5 client bersamaan (latensi & throughput) | `benchmarks/run_benchmark.py` | Latensi 2.35 ms, Throughput 1,960 req/s | **TESTED** |
| REQ-24 | Skrip benchmark pengujian 20 client bersamaan (latensi & throughput) | `benchmarks/run_benchmark.py` | Latensi 11.95 ms, Throughput 1,572 req/s | **TESTED** |
| REQ-25 | Penyimpanan data metrik hasil riil ke CSV dan JSON | `benchmarks/results/` | File `benchmark_results.json` & `.csv` | **TESTED** |
| REQ-26 | Analisis perbandingan kinerja (tabel, grafik, dan evaluasi penyebab) | `docs/benchmark-analysis.md` | Grafik `latency_throughput_chart.png` | **TESTED** |

---

## 6. Dokumentasi dan Deliverables — Bobot 10%

| ID | Deskripsi Persyaratan | Komponen/File Terkait | Bukti Pengujian | Status Aktual |
|---|---|---|---|---|
| REQ-27 | README komprehensif (prasyarat, instalasi, jalankan, testing, trouble) | `README.md` | File markdown lengkap di root | **TESTED** |
| REQ-28 | Panduan verifikasi mahasiswa (`HUMAN_RUNBOOK.md`) | `HUMAN_RUNBOOK.md` | Panduan operasional langkah-demi-langkah | **TESTED** |
| REQ-29 | Draf Laporan Proyek terstruktur sesuai ketentuan PDF halaman 13 | `docs/draf-laporan-proyek.md` | Struktur 6 bab sesuai pedoman resmi | **TESTED** |
| REQ-30 | Demonstrasi video <= 5 menit dan repositori Git dengan commit anggota | Artefak Mahasiswa | Tanggung jawab mahasiswa sesuai runbook | **PENDING HUMAN VERIFICATION** |
