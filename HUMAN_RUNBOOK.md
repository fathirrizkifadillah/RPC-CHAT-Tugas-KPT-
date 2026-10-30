# Panduan Verifikasi Mahasiswa (Human Runbook)

Dokumen ini berisi panduan operasional langkah-demi-langkah bagi mahasiswa untuk memverifikasi, menjalankan demonstrasi langsung, menguji Docker, merekam video demo (maks. 5 menit), dan melengkapi laporan akhir proyek.

---

## 1. Status Pekerjaan: Agent vs Mahasiswa

### A. Telah Selesai Dikerjakan oleh AI Agent (Tervalidasi di Workspace):
- [x] Pembacaan dan pemenuhan spesifikasi PDF Praktikum RPC & diagram `arsitektur-chat-room.svg`.
- [x] Pembacaan dan pembuatan audit 17 skill lokal (`docs/skill-usage-audit.md`).
- [x] Pembuatan dan verifikasi virtual environment (`venv`) dengan Python 3.11.9.
- [x] Instalasi dependensi proyek (`grpcio`, `grpcio-tools`, `protobuf`, `pytest`, `tabulate`, `matplotlib`).
- [x] Perancangan dan kompilasi IDL Protocol Buffers (`proto/chat_room.proto`).
- [x] Implementasi lengkap Server, Shared State (`users`, `queue`, `PROSES`), dan Client CLI.
- [x] Implementasi timeout, exponential backoff retry, dan deduplikasi `request_id`.
- [x] Pembuatan dan eksekusi 22 automated tests (Pytest) dengan hasil **100% PASS**.
- [x] Konfigurasi Dockerfile dan `docker-compose.yml` (validasi sintaks via `docker compose config`).
- [x] Eksekusi benchmark awal 1, 5, dan 20 client dengan data nyata (JSON, CSV, dan grafik PNG).
- [x] Pembuatan seluruh dokumentasi arsitektur, ADRs, environment setup, matriks persyaratan, dan draf laporan.

### B. Harus Dijalankan / Dilengkapi oleh Mahasiswa:
- [ ] Menjalankan demonstrasi langsung 2 client di dua terminal lokal atau via Docker container.
- [ ] Menjalankan Docker Desktop daemon dan menguji `docker compose up` antar-container.
- [ ] Mengambil tangkapan layar (screenshot) eksekusi Server, Client A, Client B, dan hasil tes.
- [ ] Merekam video demonstrasi (durasi maksimal 5 menit) dan mengunggahnya ke YouTube / Google Drive.
- [ ] Melakukan Git commit dengan akun masing-masing anggota kelompok untuk memenuhi rubrik riwayat commit.
- [ ] Mengisi identitas kelompok, NIM, tautan Git, tautan video pada `docs/draf-laporan-proyek.md`, lalu mengonversinya ke format PDF.
- [ ] Mengompresi file proyek ke format `Kelompok<no>_ProyekRPC.zip`.

---

## 2. Langkah Operasional Mahasiswa

### LANGKAH 1: Aktivasi Virtual Environment di Komputer Anda
- **Tujuan**: Memastikan Anda menggunakan interpreter dan pustaka yang terisolasi di dalam `venv`.
- **Lingkungan**: Terminal PowerShell (Windows) pada folder proyek `C:\TUGAS\KPT\RPC_CHAT`.
- **Command**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Atau jalankan langsung: `.\venv\Scripts\python.exe <perintah>` jika ada kebijakan eksekusi PowerShell).*
- **Hasil yang Diharapkan**: Prompt terminal menampilkan prefix `(venv)`.
- **Cara Verifikasi**:
  ```powershell
  python -c "import grpc, google.protobuf; print('Environment Siap!')"
  ```
- **Jika Gagal**: Jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` lalu ulangi aktivasi.

---

### LANGKAH 2: Demonstrasi Chat Antar 2 Client di Terminal Berbeda
- **Tujuan**: Membuktikan bahwa Client A dapat mengirim pesan yang langsung diterima oleh Client B secara real-time via gRPC broadcast.
- **Lingkungan**: Tiga jendela terminal berbeda pada host Anda.

#### Jendela 1 — Menjalankan Server:
```powershell
.\venv\Scripts\python.exe src/chat_room/server.py --port 50051
```
- *Output*: `[*] gRPC Chat Server Berhasil Dijalankan di 0.0.0.0:50051`.

#### Jendela 2 — Menjalankan Client A (Alice):
```powershell
.\venv\Scripts\python.exe src/chat_room/client.py --server localhost:50051 --username Alice
```
- *Output*: Muncul pesan `[SUCCESS] Berhasil bergabung sebagai Alice`.

#### Jendela 3 — Menjalankan Client B (Bob):
```powershell
.\venv\Scripts\python.exe src/chat_room/client.py --server localhost:50051 --username Bob
```
- *Output*: Muncul pesan bergabung, dan di terminal Alice muncul notifikasi `🔔 Pengguna 'Bob' sedang aktif di room`.

#### Uji Interaksi:
1. Di terminal Alice, ketik: `Halo Bob, ini Alice!` lalu tekan Enter.
2. Di terminal Bob, amati pesan muncul: `[XX:XX:XX] <Alice>: Halo Bob, ini Alice!`.
3. Di terminal Bob, ketik: `/users` untuk melihat daftar pengguna aktif.
4. Di terminal Bob, ketik: `/unary Pesan via unary` untuk menguji pengiriman Unary RPC.
5. Di terminal Alice, ketik: `/exit` untuk keluar. Terminal Bob akan menerima notifikasi `🔔 Pengguna 'Alice' telah keluar dari room`.

- **Bukti yang Perlu Disimpan**: Screenshot ketiga jendela terminal berdampingan (Server, Alice, Bob) untuk dokumen laporan.

---

### LANGKAH 3: Menjalankan Pengujian Otomatis (Pytest)
- **Tujuan**: Membuktikan bahwa seluruh 22 pengujian otomatis lolos pada komputer Anda.
- **Lingkungan**: Terminal PowerShell di root proyek.
- **Command**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest -v
  ```
- **Hasil yang Diharapkan**: Output `22 passed in X.XXs` dengan warna hijau.
- **Bukti yang Perlu Disimpan**: Screenshot terminal hasil eksekusi pytest untuk laporan proyek.

---

### LANGKAH 4: Pengujian Komunikasi Antar-Container (Docker)
- **Tujuan**: Memenuhi persyaratan demo pada 2 komputer atau 2 container berbeda (PDF Halaman 12).
- **Prasyarat**: Pastikan aplikasi **Docker Desktop** telah dibuka dan status Docker daemon bertuliskan *Engine Running*.
- **Command Build & Run**:
  ```powershell
  # 1. Build image container
  docker compose build

  # 2. Jalankan server chat di background
  docker compose up -d chat-server

  # 3. Periksa status container server
  docker compose ps

  # 4. Hubungkan Client A melalui container di terminal 1:
  docker compose run --rm chat-client-a

  # 5. Hubungkan Client B melalui container di terminal 2:
  docker compose run --rm chat-client-b
  ```
- **Hasil yang Diharapkan**: Client A dan Client B yang berjalan di container terpisah berhasil bertukar pesan melalui jaringan bridge Docker (`chat-net`) ke service `chat-server:50051`.
- **Hentikan Container**:
  ```powershell
  docker compose down
  ```
- **Bukti yang Perlu Disimpan**: Screenshot terminal `docker compose ps` dan interaksi client container.

---

### LANGKAH 5: Menjalankan Ulang Benchmark Kinerja (1, 5, 20 Client)
- **Tujuan**: Mengonfirmasi hasil latensi dan throughput akhir untuk laporan.
- **Command**:
  ```powershell
  .\venv\Scripts\python.exe benchmarks/run_benchmark.py --clients 1,5,20 --messages 50
  ```
- **Hasil yang Diharapkan**: Tabel rekapitulasi kinerja tercetak di layar dan file grafik diperbarui di `benchmarks/results/latency_throughput_chart.png`.
- **Bukti yang Perlu Disimpan**: File `benchmark_results.csv`, `benchmark_results.json`, dan file gambar `latency_throughput_chart.png`.

---

### LANGKAH 6: Pengambilan Video Demo (Maksimal 5 Menit)
- **Skenario Video Rekomendasi**:
  1. **Menit 0:00 - 0:45**: Perkenalan anggota kelompok, judul proyek, dan penjelasan singkat arsitektur gRPC (`arsitektur-chat-room.svg`).
  2. **Menit 0:45 - 2:00**: Menjalankan server, lalu membuka Client A dan Client B. Menunjukkan pertukaran pesan real-time (bidirectional stream).
  3. **Menit 2:00 - 2:45**: Menunjukkan pemanggilan RPC `/users` (ListUsers) dan `/unary` (SendMessage dengan request_id).
  4. **Menit 2:45 - 3:30**: Menunjukkan toleransi kegagalan: mematikan salah satu client dan melihat event disconnect tertangani dengan bersih.
  5. **Menit 3:30 - 4:30**: Menjalankan skrip benchmark kinerja (`run_benchmark.py`) dan memperlihatkan grafik performa pada 1, 5, dan 20 client.
  6. **Menit 4:30 - 5:00**: Penutup dan kesimpulan singkat.
- **Unggah**: Simpan video ke YouTube (Unlisted) atau Google Drive (akses publik) dan tempel tautannya ke laporan.

---

### LANGKAH 7: Git Workflow dan Riwayat Commit Anggota
- **Tujuan**: Memenuhi persyaratan rubrik bahwa kode disimpan di repositori Git dengan riwayat commit dari *setiap anggota kelompok*.
- **Panduan**:
  1. Inisialisasi remote repository GitHub kelompok Anda:
     ```powershell
     git remote add origin https://github.com/[USERNAME]/[NAMA_REPO_PROYEK_RPC].git
     ```
  2. Setiap anggota melakukan commit bagian tugasnya menggunakan identitas git masing-masing:
     ```powershell
     git config user.name "Nama Anggota 1"
     git config user.email "email_anggota1@kampus.ac.id"
     git commit -m "feat: implementasi server gRPC dan in-memory state"
     ```
  3. Push branch ke GitHub:
     ```powershell
     git push -u origin main
     ```

---

### LANGKAH 8: Finalisasi Laporan dan Pengumpulan ZIP
- **Tujuan**: Menyiapkan berkas pengumpulan sesuai format resmi PDF halaman 13.
- **Format Berkas**:
  - `Kelompok<no>_ProyekRPC.zip`
- **Isi Berkas ZIP**:
  1. Laporan proyek final dalam format PDF (dikonversi dari `docs/draf-laporan-proyek.md` setelah diisi identitas lengkap, screenshot, dan link video).
  2. Seluruh kode sumber (`proto/`, `src/`, `tests/`, `benchmarks/`, `docs/`, `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `README.md`).
  *Catatan: Pastikan folder `venv/` dan `__pycache__/` TIDAK dimasukkan ke dalam zip.*
