# Audit Penggunaan Skill Lokal (Skill Usage Audit)

Dokumen ini mencatat audit formal pembacaan dan penerapan 17 skill lokal dari direktori `C:\Users\FATHIR\.agents\skills` pada proyek sistem terdistribusi **Chat Room gRPC**. Setiap entri mencakup path file aktual yang dibaca, aturan teknis yang relevan, serta bukti penerapannya pada kode, pengujian, arsitektur, dan dokumentasi proyek.

---

## 1. `software-architecture`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\software-architecture\SKILL.md`
- **Judul/Bagian Instruksi**: Clean Architecture & DDD Principles, Code Quality, Anti-Patterns to Avoid, Early Return Pattern.
- **Aturan Teknis Relevan**:
  - Gunakan nama modul/kelas berbasis domain yang spesifik (bukan nama generik seperti `utils` atau `common`).
  - Terapkan pola *early return* untuk mengurangi kedalaman nesting (maksimal 3 level).
  - Pisahkan domain logic/state manajemen dari layer presentasi/CLI dan layer protokol I/O gRPC.
  - Batasi ukuran fungsi dan modul agar tetap kohesif dan mudah dipelihara.
- **Keputusan Desain/Implementasi**:
  - Memisahkan domain logika shared state ke dalam `src/chat_room/service.py` (LayananChat) dan `src/chat_room/state.py` (ChatState / In-Memory Store), terpisah dari terminal UI (`src/chat_room/client.py`).
  - Menggunakan penamaan domain eksplisit: `ChatState`, `ActiveUserManager`, `MessageDeduplicator`, `ClientMessageQueue`.
- **File Penerapan**: `src/chat_room/state.py`, `src/chat_room/service.py`, `src/chat_room/client.py`.
- **Bukti Validasi**: Struktur kode modular tanpa helper generik, nesting maksimal 2-3 level dengan early return pada validasi gRPC context dan deduplikasi request ID.

---

## 2. `api-design-principles`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\api-design-principles\SKILL.md`
- **Judul/Bagian Instruksi**: API Design Principles, Modeling Resources, Specifying Errors, Constraints & Consistency.
- **Aturan Teknis Relevan**:
  - Definisikan kontrak antarmuka yang konsisten, jelas perannya, dan idempoten bila memungkinkan.
  - Pisahkan model permintaan (request) dan model tanggapan (response) secara terstruktur.
  - Tetapkan penanganan status kode error yang standar dan prediktif bagi pemanggil API.
- **Keputusan Desain/Implementasi**:
  - Merancang kontrak IDL Protocol Buffers `proto/chat_room.proto` dengan 4 RPC eksplisit:
    1. `Join(JoinRequest) returns (JoinResponse)`: Registrasi pengguna baru ke chat room.
    2. `ListUsers(ListUsersRequest) returns (ListUsersResponse)`: Pengambilan snapshot pengguna aktif.
    3. `SendMessage(SendMessageRequest) returns (SendMessageResponse)`: Jalur RPC unary untuk pengiriman pesan dengan perlindungan `request_id`.
    4. `Chat(stream ChatFrame) returns (stream ChatFrame)`: Jalur bidirectional streaming real-time untuk pertukaran pesan dan event pengguna.
  - Standardisasi kode status gRPC (`INVALID_ARGUMENT`, `ALREADY_EXISTS`, `NOT_FOUND`, `RESOURCE_EXHAUSTED`).
- **File Penerapan**: `proto/chat_room.proto`, `src/chat_room/service.py`.
- **Bukti Validasi**: Semua 4 RPC didefinisikan dengan protobuf fields bernomor jelas, pesan status dan boolean sukses yang konsisten.

---

## 3. `python-development` (Alias) & 4. `python-development-python-scaffold`
- **Path Aktual Dibaca**:
  - `C:\Users\FATHIR\.agents\skills\python-development\SKILL.md`
  - `C:\Users\FATHIR\.agents\skills\python-development-python-scaffold\SKILL.md`
- **Judul/Bagian Instruksi**: Python Project Scaffolding, Directory Tree Conventions, pyproject.toml / requirements configuration, CLI tool structure, testing setup.
- **Aturan Teknis Relevan**:
  - Susun direktori kerja dengan standar Python production (`src/<package_name>/`, `tests/`, `docs/`, `scripts/`).
  - Konfigurasi `pyproject.toml` dan `requirements.txt` dengan batasan versi Python `>=3.10`.
  - Terapkan `type annotations` (type hints) secara disiplin pada seluruh signature fungsi dan metode.
  - Sediakan entry point yang jelas untuk CLI client dan server.
- **Keputusan Desain/Implementasi**:
  - Membangun struktur package di `src/chat_room/` dengan file `__init__.py`, `server.py`, `client.py`, `service.py`, `state.py`, `config.py`.
  - Mengonfigurasi `pyproject.toml` dengan metadata proyek, dependensi inti `grpcio`, `grpcio-tools`, `protobuf`, dan dependensi tes `pytest`.
- **File Penerapan**: `pyproject.toml`, `requirements.txt`, `src/chat_room/`.
- **Bukti Validasi**: Struktur layout `src/` standar, import absolute `from chat_room...` berfungsi dengan bersih.

---

## 5. `python-packaging`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\python-packaging\SKILL.md`
- **Judul/Bagian Instruksi**: Creating, structuring, and distributing Python packages, entry points, pyproject.toml build configuration.
- **Aturan Teknis Relevan**:
  - Gunakan `pyproject.toml` standar PEP 517/621 dengan package discovery yang rapi.
  - Sediakan console script entry points (`chat-server`, `chat-client`, `chat-benchmark`) untuk kemudahan eksekusi CLI.
- **Keputusan Desain/Implementasi**:
  - Menambahkan bagian `[project.scripts]` di `pyproject.toml` yang memetakan:
    - `chat-server = "chat_room.server:main"`
    - `chat-client = "chat_room.client:main"`
    - `chat-benchmark = "chat_room.benchmark:main"`
- **File Penerapan**: `pyproject.toml`.
- **Bukti Validasi**: Package dapat diinstal dalam mode editable (`pip install -e .`) dan modul dieksekusi via `python -m chat_room.server`.

---

## 6. `environment-setup-guide`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\environment-setup-guide\SKILL.md`
- **Judul/Bagian Instruksi**: Environment Setup Guide, Step-by-Step Tool Verification, Python Virtual Environment Setup, Troubleshooting.
- **Aturan Teknis Relevan**:
  - Jangan menginstal dependensi ke interpreter global.
  - Verifikasi versi Python (`>=3.10`), path `sys.executable`, `sys.prefix`, dan `sys.base_prefix`.
  - Sediakan file `.env.example` atau file konfigurasi default yang jelas.
  - Dokumentasikan langkah troubleshooting untuk sistem Windows dan Linux/Docker.
- **Keputusan Desain/Implementasi**:
  - Memverifikasi Python 3.11.9 yang tersedia pada sistem host Windows.
  - Membuat virtual environment di `./venv` dan memvalidasi `sys.executable` terikat pada `C:\TUGAS\KPT\RPC_CHAT\venv\Scripts\python.exe`.
  - Menulis panduan setup komprehensif pada `docs/environment-setup.md`.
- **File Penerapan**: `venv/`, `docs/environment-setup.md`, `README.md`.
- **Bukti Validasi**: Eksekusi `.\venv\Scripts\python.exe -m pip check` menghasilkan no broken requirements.

---

## 7. `async-python-patterns`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\async-python-patterns\SKILL.md`
- **Judul/Bagian Instruksi**: Async Python Patterns, Concurrency Patterns, Queues, Backpressure, Timeouts, Graceful Shutdown.
- **Aturan Teknis Relevan**:
  - Tangani komunikasi dua arah (bidirectional streaming) dengan isolasi thread/antrean per client yang aman.
  - Terapkan mekanisme backpressure atau batas kapasitas antrean (`maxsize`) agar client lambat tidak menyebabkan kehabisan memori (*memory exhaustion*).
  - Pastikan penghentian (shutdown) stream membatalkan antrean dan membersihkan resource tanpa hanging.
- **Keputusan Desain/Implementasi**:
  - Menggunakan thread-safe `queue.Queue(maxsize=100)` untuk setiap client aktif pada server gRPC.
  - Menerapkan timeout polling antrean `queue.get(timeout=0.5)` di generator streaming untuk mendeteksi `context.is_active()` secara berkala.
  - Pada client CLI, memisahkan thread pembaca input terminal dan thread penerima stream respons gRPC.
- **File Penerapan**: `src/chat_room/service.py`, `src/chat_room/state.py`, `src/chat_room/client.py`.
- **Bukti Validasi**: Stream terputus dengan bersih saat client keluar atau server dihentikan; client lambat ditangani tanpa crash server.

---

## 8. `python-testing-patterns` & 9. `pytest-skill`
- **Path Aktual Dibaca**:
  - `C:\Users\FATHIR\.agents\skills\python-testing-patterns\SKILL.md`
  - `C:\Users\FATHIR\.agents\skills\pytest-skill\SKILL.md`
- **Judul/Bagian Instruksi**: Pytest Testing Skill, Fixtures, Parametrize, Markers, Exception Testing, Conftest Patterns.
- **Aturan Teknis Relevan**:
  - Gunakan fixture pytest dengan scope dan teardown (`yield`) yang terkontrol untuk mengelola siklus hidup server gRPC tes.
  - Gunakan `pytest.raises` untuk memverifikasi `grpc.RpcError` dan status code gRPC.
  - Gunakan `@pytest.mark.parametrize` untuk pengujian input invalid, batas payload, dan skenario kegagalan.
  - Buat tes unit dan tes integrasi yang fokus dan independen dari state global persisten.
- **Keputusan Desain/Implementasi**:
  - Membuat fixture `grpc_server` dan `grpc_stub` di `tests/conftest.py` yang otomatis menjalankan in-process/local socket gRPC server dan menutupnya setelah selesai.
  - Mengimplementasikan 12 area pengujian di folder `tests/`:
    `test_join.py`, `test_list_users.py`, `test_send_message.py`, `test_chat_stream.py`, `test_broadcast.py`, `test_disconnect.py`, `test_concurrency.py`, `test_deduplication.py`, `test_timeout_retry.py`, `test_errors.py`, `test_queue_backpressure.py`, `test_server_lifecycle.py`.
- **File Penerapan**: `tests/conftest.py`, `tests/test_*.py`.
- **Bukti Validasi**: Seluruh rangkaian tes pytest dieksekusi via `.\venv\Scripts\python.exe -m pytest -v` dan lulus 100%.

---

## 10. `test-driven-development` (TDD)
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\test-driven-development\SKILL.md`
- **Judul/Bagian Instruksi**: The Iron Law: No production code without a failing test first, Red-Green-Refactor cycle, Systematic Verification.
- **Aturan Teknis Relevan**:
  - Tulis tes terlebih dahulu (RED), saksikan kegagalannya karena fungsi belum ada/belum benar.
  - Tulis kode implementasi minimal untuk membuat tes berhasil (GREEN).
  - Lakukan refaktorisasi untuk membersihkan kode tanpa mengubah perilaku (REFACTOR).
- **Keputusan Desain/Implementasi**:
  - Mendefinisikan tes kontrak RPC (`Join`, `ListUsers`, `SendMessage`, `Chat`) sebelum melengkapi logika broadcast di servicer.
  - Menulis tes deduplikasi request_id dengan simulasi retry sebelum mengimplementasikan cache `PROSES`.
  - Menguji penanganan disconnect sebelum menambahkan callback stream RPC termination.
- **File Penerapan**: Rangkaian tes di `tests/` dan implementasi di `src/chat_room/`.
- **Bukti Validasi**: Log pytest dan verifikasi failure assertions sebelum implementasi final diselesaikan.

---

## 11. `systematic-debugging`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\systematic-debugging\SKILL.md`
- **Judul/Bagian Instruksi**: The Four Phases: Root Cause Investigation, Pattern Analysis, Hypothesis and Testing, Implementation; Condition-Based Waiting.
- **Aturan Teknis Relevan**:
  - Jangan menebak-nebak (no guessing fixes). Cari akar masalah dari stack trace, error code, dan log.
  - Gunakan condition-based waiting / polling condition pada pengujian threading/concurrency daripada `time.sleep` statis yang rapuh.
  - Lakukan satu perubahan pada satu waktu saat mendiagnosis bug.
- **Keputusan Desain/Implementasi**:
  - Menggunakan synchronization primitives (`threading.Event`, condition checks) pada tes concurrency dan streaming client alih-alih arbitrary sleep.
  - Menangani race condition pendaftaran antrean dan broadcast pesan dengan lock terlokalisasi (fine-grained locking) pada `ChatState`.
- **File Penerapan**: `src/chat_room/state.py`, `tests/test_concurrency.py`.
- **Bukti Validasi**: Tidak ada flaky tests pada eksekusi pengujian konkuren multi-thread.

---

## 12. `docker-expert`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\docker-expert\SKILL.md`
- **Judul/Bagian Instruksi**: Dockerfile Optimization & Multi-Stage Builds, Security Hardening (Non-root user), Docker Compose Orchestration, Network Isolation.
- **Aturan Teknis Relevan**:
  - Pisahkan layer dependency dari layer source code untuk memaksimalkan layer caching.
  - Buat non-root user (`appuser`, UID 1001) untuk keamanan container.
  - Gunakan `docker-compose.yml` dengan healthcheck, custom network, dan resolusi DNS internal (nama service `chat-server`, bukan `localhost`).
  - Gunakan `.dockerignore` untuk mengecualikan `.git`, `venv`, `__pycache__`, dan artefak pengujian host.
- **Keputusan Desain/Implementasi**:
  - Membuat `Dockerfile` berbasis `python:3.11-slim` dengan non-root user `appuser`.
  - Membuat `.dockerignore` yang ketat.
  - Menyusun `docker-compose.yml` yang mendefinisikan service `chat-server` (port `50051`) dan service `chat-client-a` serta `chat-client-b` dalam network bridge `chat-net`.
- **File Penerapan**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`.
- **Bukti Validasi**: File konfigurasi Docker divalidasi dengan `docker compose config` dan pengujian container berhasil.

---

## 13. `python-performance-optimization`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\python-performance-optimization\SKILL.md`
- **Judul/Bagian Instruksi**: Performance Best Practices, Profiling, Lock Contention Reduction, Memory and I/O Bottlenecks.
- **Aturan Teknis Relevan**:
  - Kurangi *critical section* di dalam lock: jangan memegang lock saat operasi I/O jaringan atau menunggu antrean.
  - Gunakan snapshot data (misalnya `list(self._users.values())`) saat membaca agar lock segera dilepaskan.
  - Gunakan struktur data O(1) seperti `dict` dan `set` untuk pencarian pengguna dan tracking request ID deduplikasi.
- **Keputusan Desain/Implementasi**:
  - Pada `ChatState`, lock `threading.Lock` hanya dipegang saat memutasi dictionary `users`, `queues`, dan `PROSES`.
  - Proses `broadcast_message` mengambil snapshot daftar queue di bawah lock, kemudian melakukan `queue.put_nowait()` di luar lock utama, sehingga publisher tidak memblokir operasi registrasi pengguna.
- **File Penerapan**: `src/chat_room/state.py`.
- **Bukti Validasi**: Throughput benchmark tinggi dan latensi rendah pada pengujian beban 1, 5, dan 20 client.

---

## 14. `documentation-and-adrs`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\documentation-and-adrs\SKILL.md`
- **Judul/Bagian Instruksi**: Architecture Decision Records (ADRs), Documenting the "Why", Inline Documentation, Gotchas and Lifecycle.
- **Aturan Teknis Relevan**:
  - Rekam keputusan teknis penting menggunakan format ADR (Status, Context, Decision, Alternatives Considered, Consequences).
  - Dokumentasikan *trade-off* dan batasan arsitektur (seperti batasan in-memory deduplication saat server restart).
  - Tulis inline comments yang menjelaskan *intent/why*, bukan sekadar mengulang kode (*what*).
- **Keputusan Desain/Implementasi**:
  - Membuat ADR formal di folder `docs/decisions/`:
    - `ADR-001: In-Memory Concurrency and Message Queue Architecture`
    - `ADR-002: Request-ID Deduplication and Semantics of Unary vs Streaming RPC`
    - `ADR-003: Client Retry and Exponential Backoff Strategy`
  - Mendokumentasikan gotcha in-memory deduplication di ADR dan draf laporan proyek.
- **File Penerapan**: `docs/decisions/ADR-001.md`, `docs/decisions/ADR-002.md`, `docs/decisions/ADR-003.md`.
- **Bukti Validasi**: File ADR tersimpan dan dapat diaudit secara transparan.

---

## 15. `readme`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\readme\SKILL.md`
- **Judul/Bagian Instruksi**: The Three Purposes of a README (Local Development, Understanding the System, Production Deployment), Comprehensive Section Structure.
- **Aturan Teknis Relevan**:
  - Sediakan instruksi langkah-demi-langkah yang jelas untuk setup venv, instalasi dependensi, kompilasi proto, menjalankan server, client, tes, dan Docker.
  - Berikan tabel command, diagram alur, prasyarat sistem, dan bagian troubleshooting yang komprehensif.
  - Buat instruksi yang dapat direproduksi oleh mahasiswa lain tanpa kebingungan.
- **Keputusan Desain/Implementasi**:
  - Menulis `README.md` lengkap yang memuat ringkasan arsitektur, panduan aktivasi venv Windows/Linux, perintah `protoc`, cara menjalankan 2 client (Client A & B), eksekusi tes pytest, benchmark, serta eksekusi Docker Compose.
- **File Penerapan**: `README.md`.
- **Bukti Validasi**: Seluruh perintah diuji langsung di terminal lokal.

---

## 16. `git-workflow-and-versioning`
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\git-workflow-and-versioning\SKILL.md`
- **Judul/Bagian Instruksi**: Trunk-Based Development, Atomic Commits, Conventional Commit Messages (`feat`, `fix`, `docs`, `test`, `chore`), Pre-commit Hygiene.
- **Aturan Teknis Relevan**:
  - Lakukan komit bertahap (atomic commits) untuk setiap milestone logis.
  - Gunakan format commit konvensional: `<type>: <short description>`.
  - Jangan mencampurkan perubahan format dengan perubahan fungsional.
  - Pastikan file sensitif dan artefak virtual environment tidak masuk ke git repository.
- **Keputusan Desain/Implementasi**:
  - Menginisialisasi git repository lokal di workspace `C:\TUGAS\KPT\RPC_CHAT`.
  - Menerapkan `.gitignore` ketat.
  - Menyusun pesan commit deskriptif untuk setiap tahap (init, proto, core, client, tests, benchmark, docker, docs).
  - Menyediakan panduan kontribusi Git bagi mahasiswa di `HUMAN_RUNBOOK.md` agar setiap anggota memiliki riwayat commit nyata.
- **File Penerapan**: `.git/`, `.gitignore`, `HUMAN_RUNBOOK.md`.
- **Bukti Validasi**: Git commit history bersih dan terstruktur.

---

## 17. `k6-load-testing` (Evaluasi Kebutuhan dan Kesesuaian)
- **Path Aktual Dibaca**: `C:\Users\FATHIR\.agents\skills\k6-load-testing\SKILL.md`
- **Judul/Bagian Instruksi**: k6 Load Testing Overview, Test Configuration (VUs, duration, stages, thresholds), WebSocket Testing, Results Analysis.
- **Aturan Teknis Relevan**:
  - Gunakan tool pengujian beban yang mendukung protokol target dengan akurat.
  - Ukur latensi (p95, average) dan throughput (requests/messages per second) secara konsisten.
  - Nilai kesesuaian tool terhadap skenario streaming dua arah (bidirectional duplex streaming) dan lingkungan eksekusi aktual.
- **Evaluasi Teknis & Keputusan**:
  - **Hasil Evaluasi**: Dokumentasi `k6-load-testing` berfokus pada pengujian HTTP/REST dan WebSocket. Meskipun ekosistem k6 memiliki ekstensi eksperimental gRPC, k6 standar tidak mendukung simulasi interaktif bidirectional duplex streaming gRPC dengan logika message queuing dinamis per pengguna pada lingkungan Windows tanpa k6 binary terinstal.
  - **Keputusan**: Sesuai dengan instruksi Section 2.1 ("Terapkan jika sesuai... Jangan memaksakan tool yang tidak cocok dengan bidirectional streaming atau lingkungan aktual"), pengujian beban diimplementasikan menggunakan skrip Python mandiri berbasis pustaka resmi `grpcio` (`benchmarks/run_benchmark.py`). Skrip ini menggunakan `concurrent.futures.ThreadPoolExecutor` untuk memacu 1, 5, dan 20 client gRPC bersamaan, mengukur latensi round-trip persis serta throughput pesan, dan mengekspor hasilnya ke format CSV dan JSON.
- **File Penerapan**: `benchmarks/run_benchmark.py`, `docs/benchmark-analysis.md`.
- **Bukti Validasi**: Skrip benchmark Python berhasil menguji 1, 5, dan 20 client secara riil terhadap server gRPC dan menghasilkan data metrik aktual.
