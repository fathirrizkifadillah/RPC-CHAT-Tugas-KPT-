# Draf Laporan Proyek Mini: Sistem Terdistribusi Berbasis RPC
## Studi Kasus: Chat Room Banyak Pengguna yang Bertukar Pesan Secara Real-Time

**Mata Kuliah**: Komputasi Paralel dan Terdistribusi  
**Program Studi**: Informatika / Ilmu Komputer  
**Tahun Akademik**: 2026 / 2027  

---

### IDENTITAS KELOMPOK

> *[MAHASISWA: Silakan isi nomor kelompok, nama anggota, dan NIM yang sebenarnya pada tabel di bawah ini]*

| No | Nama Lengkap Mahasiswa | NIM | Peran / Kontribusi Utama | Riwayat Commit Git Utama |
|:---:|---|:---:|---|---|
| 1 | `[NAMA ANGGOTA 1]` *(Ketua)* | `[NIM ANGGOTA 1]` | Desain IDL `.proto`, Arsitektur Server gRPC, Implementasi State | `feat: ...`, `fix: ...` |
| 2 | `[NAMA ANGGOTA 2]` | `[NIM ANGGOTA 2]` | Implementasi Client CLI, Toleransi Kegagalan (Retry & Timeout) | `feat: ...`, `test: ...` |
| 3 | `[NAMA ANGGOTA 3]` | `[NIM ANGGOTA 3]` | Pengujian Otomatis (Pytest), Dockerization & Skrip Benchmark | `test: ...`, `docs: ...` |

- **Tautan Repositori Git**: `https://github.com/[USERNAME]/[NAMA_REPO_PROYEK_RPC]` *(Wajib mencantumkan riwayat commit nyata setiap anggota)*
- **Tautan Video Demonstrasi (Maks. 5 Menit)**: `https://youtu.be/[ID_VIDEO_DEMO]` atau `https://drive.google.com/file/d/[ID_VIDEO]/view`

---

## 1. Deskripsi Studi Kasus dan Diagram Arsitektur

### 1.1 Deskripsi Studi Kasus
Studi kasus yang dipilih adalah **Nomor 3: Chat Room banyak pengguna yang bertukar pesan secara real-time**.  
Sistem ini memungkinkan banyak pengguna (client) di mesin/container berbeda untuk saling terhubung, meregistrasikan username mereka, melihat pengguna yang sedang online, serta bertukar pesan secara langsung (*broadcast*) dengan latensi rendah memanfaatkan teknologi gRPC berbasis protokol transport HTTP/2.

### 1.2 Diagram Arsitektur Komponen dan Alur RPC
Arsitektur sistem dibangun berdasarkan referensi desain `arsitektur-chat-room.svg` yang terdiri atas dua kontainer utama:

```
+------------------------------------+           +---------------------------------------------+
|          CONTAINER CLIENT          |           |              CONTAINER SERVER               |
|                                    |           |                                             |
|  +------------------------------+  |           |  +---------------------------------------+  |
|  |         Client CLI A         |  |   gRPC    |  |              gRPC Server              |  |
|  |   (kirim + terima pesan)     |  |<--------->|  |   (ThreadPoolExecutor, :50051)        |  |
|  +------------------------------+  |  Port     |  +---------------------------------------+  |
|                                    |  50051    |                      |                      |
|  +------------------------------+  |           |                      v                      |
|  |         Client CLI B         |  |  HTTP/2   |  +---------------------------------------+  |
|  |   (kirim + terima pesan)     |  |<--------->|  |              LayananChat              |  |
|  +------------------------------+  |           |  | (Join, ListUsers, SendMessage, Chat)  |  |
|                                    |           |  +---------------------------------------+  |
|  +------------------------------+  |           |                      |                      |
|  |         Client CLI N         |  |           |                      v                      |
|  |   (simulasi beban 20 client) |  |<--------->|  +---------------------------------------+  |
|  +------------------------------+  |           |  |        State Bersama di Memori        |  |
|                                    |           |  |  * users : daftar user aktif (Lock)   |  |
|                                    |           |  |  * queue : antrean pesan per client   |  |
|                                    |           |  |  * PROSES: deduplikasi request_id     |  |
|                                    |           |  +---------------------------------------+  |
+------------------------------------+           +---------------------------------------------+
```

### 1.3 Alur Pemanggilan Remote Procedure Call (RPC)
1. **Fase Registrasi / Join**:
   - Client memanggil Unary RPC `Join(JoinRequest)` dengan membawa `username`, `client_id`, dan `request_id`.
   - Server memvalidasi keunikan username di memori `users`. Jika sukses, server mengembalikan `user_id` unik dan membroadcast event pengguna masuk.
2. **Fase Pengambilan Pengguna Aktif**:
   - Client memanggil Unary RPC `ListUsers(ListUsersRequest)` untuk mendapatkan snapshot seluruh anggota yang sedang aktif.
3. **Fase Pengiriman Unary `SendMessage`**:
   - Client mengirimkan pesan via `SendMessage(SendMessageRequest)`. Server memeriksa `request_id` di `PROSES`. Jika baru, pesan dibroadcast ke semua antrean client aktif dan acknowledgment dikembalikan ke pengirim.
4. **Fase Chat Interaktif Real-Time (`Chat`)**:
   - Client membuka aliran dua arah (*bidirectional streaming*) `Chat(stream ChatFrame)`.
   - Server mengaitkan `queue.Queue` khusus untuk client tersebut.
   - Pesan yang dikirim pengguna lain langsung di-push ke antrean dan di-yield secara instan ke layar terminal client.

---

## 2. Antarmuka Layanan Protocol Buffers (`.proto`)

Kontrak antarmuka didefinisikan dalam file `proto/chat_room.proto`:

```protobuf
syntax = "proto3";

package chat_room;

// Service LayananChat sesuai arsitektur diagram dan spesifikasi PDF Praktikum RPC
service LayananChat {
  // RPC 1: Join / Registrasi sesi pengguna
  rpc Join (JoinRequest) returns (JoinResponse);

  // RPC 2: Mengambil daftar pengguna aktif di memori server
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);

  // RPC 3: Jalur Unary untuk pengiriman pesan dengan perlindungan request_id
  rpc SendMessage (SendMessageRequest) returns (SendMessageResponse);

  // RPC 4: Jalur Bidirectional Streaming untuk pertukaran pesan real-time
  rpc Chat (stream ChatFrame) returns (stream ChatFrame);
}

message JoinRequest {
  string username = 1;
  string client_id = 2;
  string request_id = 3;
}

message JoinResponse {
  bool success = 1;
  string message = 2;
  string user_id = 3;
  int64 joined_at = 4;
}

message ListUsersRequest {
  string request_id = 1;
}

message UserInfo {
  string user_id = 1;
  string username = 2;
  int64 connected_at = 3;
  bool is_active = 4;
}

message ListUsersResponse {
  bool success = 1;
  repeated UserInfo users = 2;
  int32 total_users = 3;
}

message SendMessageRequest {
  string request_id = 1;
  string sender_username = 2;
  string content = 3;
  int64 timestamp = 4;
}

message SendMessageResponse {
  string request_id = 1;
  bool success = 2;
  string message = 3;
  int64 delivered_at = 4;
}

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

message ChatFrame {
  FrameType type = 1;
  string request_id = 2;
  string sender = 3;
  string content = 4;
  int64 timestamp = 5;
  string user_id = 6;
}
```

### Penjelasan Setiap RPC:
1. **`Join`**: Mendaftarkan client dengan username ke server. Mencegah nama kembar aktif dan mendukung reconnect idempoten jika `client_id` sama.
2. **`ListUsers`**: Mengambil daftar entitas `UserInfo` yang sedang aktif di memori server tanpa mengganggu aliran obrolan.
3. **`SendMessage`**: Unary RPC untuk pengiriman pesan mandiri yang dilindungi deduplikasi `request_id`, menjamin semantik *at-most-once*.
4. **`Chat`**: Bidirectional stream penuh di mana client mengirimkan aliran `ChatFrame` dan server mengirimkan aliran `ChatFrame` balik secara real-time.

---

## 3. Strategi Concurrency dan Toleransi Kegagalan

### 3.1 Strategi Concurrency dan Sinkronisasi Shared State
Server menggunakan tiga struktur data di memori yang dilindungi sinkronisasi ketat:
1. **`users` (Daftar Pengguna Aktif)**:
   - Dilindungi menggunakan `threading.RLock()`.
   - Mutasi (registrasi, disconnect) dan pembacaan snapshot dilakukan di dalam *critical section* yang sangat singkat, sehingga tidak memblokir thread worker lain.
2. **`queue` (Antrean Pesan Per Client)**:
   - Setiap client streaming memiliki objek `queue.Queue(maxsize=100)`.
   - Mengatasi masalah *Slow Client*: Ketika antrean seorang client lambat penuh, server menerapkan kebijakan *drop-oldest* agar client lain dan publisher tidak terblokir (*head-of-line blocking isolation*).
3. **`PROSES` (Deduplikasi Pesan Berdasarkan `request_id`)**:
   - Memetakan `request_id -> ResponsePayload` dengan mekanisme LRU cache untuk membatasi konsumsi memori.
   - Jika client mengirim ulang permintaan yang sama karena timeout, server langsung mengembalikan hasil dari `PROSES` tanpa membroadcast ulang pesan tersebut.

### 3.2 Toleransi Kegagalan (Fault Tolerance)
1. **Timeout**:
   - Seluruh pemanggilan Unary RPC di sisi client dilengkapi batas waktu eksplisit (`timeout=5.0` detik).
2. **Retry dengan Exponential Backoff & Jitter**:
   - Hanya berlaku untuk *transient errors* (`DEADLINE_EXCEEDED`, `UNAVAILABLE`, `RESOURCE_EXHAUSTED`).
   - Jeda retry mengikuti rumus: $jeda = 0.5 \times 2^{(percobaan - 1)} + jitter$.
   - Error deterministik seperti `INVALID_ARGUMENT` atau `ALREADY_EXISTS` langsung dilaporkan ke pengguna tanpa retry.
3. **Penanganan Client Terputus (Disconnect)**:
   - Callback `context.add_callback()` pada gRPC memastikan bahwa saat koneksi client terputus (baik normal maupun crash), sesi pengguna otomatis dibersihkan dari `users` dan event leave dibroadcast ke seluruh client yang tersisa.
4. **Batasan Arsitektur In-Memory**:
   - Karena penyimpanan berada di memori RAM, saat server restart data `PROSES` dan `users` akan tereset. Ini merupakan trade-off arsitektur in-memory tanpa persistensi basis data eksternal.

---

## 4. Hasil Pengujian Kinerja dan Analisis

Pengujian beban dilakukan menggunakan skrip `benchmarks/run_benchmark.py` pada 1, 5, dan 20 client bersamaan (masing-masing mengirimkan 50 pesan gRPC).

### 4.1 Tabel Rekapitulasi Pengujian Kinerja Nyata

| Parameter Pengujian | 1 Client | 5 Client | 20 Client |
|---|:---:|:---:|:---:|
| **Total Permintaan Dicoba** | 50 | 250 | 1,000 |
| **Permintaan Sukses** | 50 (100%) | 250 (100%) | 1,000 (100%) |
| **Permintaan Gagal** | 0 (0%) | 0 (0%) | 0 (0%) |
| **Latensi Rata-rata (ms)** | **0.70 ms** | **2.35 ms** | **11.95 ms** |
| **Latensi Median (ms)** | 0.61 ms | 2.19 ms | 11.16 ms |
| **Latensi P95 (ms)** | 1.27 ms | 3.44 ms | 17.97 ms |
| **Throughput (requests/detik)** | **1,048.55 req/s** | **1,960.86 req/s** | **1,572.70 req/s** |
| **Total Waktu Pengujian (s)** | 0.05 s | 0.13 s | 0.64 s |

### 4.2 Grafik Kinerja
Grafik perbandingan latensi rata-rata dan throughput disimpan di `benchmarks/results/latency_throughput_chart.png` dan dilampirkan pada laporan PDF.

### 4.3 Analisis Kinerja
1. **Analisis Throughput**:
   - Throughput meningkat tajam dari 1 ke 5 client (naik dari 1,048 req/s ke 1,960 req/s) berkat paralelisasi multi-thread di `ThreadPoolExecutor` server.
   - Pada 20 client, throughput stabil di angka 1,572 req/s karena adanya beban pergantian context (*context switching*) antar thread dan persaingan lock sinkronisasi memori bersama (*lock contention*).
2. **Analisis Latensi**:
   - Latensi meningkat wajar seiring penambahan client konkuren (dari 0.70 ms hingga 11.95 ms).
   - Nilai P95 latensi pada 20 client tetap berada di bawah 18 ms, membuktikan performa real-time obrolan yang sangat responsif jauh di bawah batas persepsi manusia (100 ms).

---

## 5. Pembagian Tugas Anggota Kelompok

> *[MAHASISWA: Sesuaikan pembagian tugas berikut dengan kontribusi aktual masing-masing anggota]*

1. **Anggota 1 (`[NAMA ANGGOTA 1]`)**:
   - Merancang kontrak IDL `proto/chat_room.proto`.
   - Mengembangkan arsitektur server `src/chat_room/server.py` dan `src/chat_room/state.py`.
   - Mengimplementasikan isolasi antrean per client dan mekanisme lock.
2. **Anggota 2 (`[NAMA ANGGOTA 2]`)**:
   - Membangun antarmuka client CLI `src/chat_room/client.py`.
   - Mengimplementasikan logika toleransi kegagalan (timeout, retry, deduplikasi `request_id`).
   - Melakukan pengujian integrasi komunikasi multi-terminal.
3. **Anggota 3 (`[NAMA ANGGOTA 3]`)**:
   - Menyusun skenario pengujian otomatis pytest di folder `tests/`.
   - Mengonfigurasi `Dockerfile` dan `docker-compose.yml` untuk multi-container.
   - Menjalankan skrip benchmark kinerja 1, 5, dan 20 client serta menyusun laporan grafik.

---

## 6. Tautan Repositori Git dan Video Demonstrasi

- **Tautan Repositori Git**: `https://github.com/[USERNAME]/[NAMA_REPO_PROYEK_RPC]`
- **Tautan Video Demo (Durasi Maksimal 5 Menit)**: `https://youtu.be/[ID_VIDEO_DEMO]`
  - *Catatan Isi Video*: Memperlihatkan server dijalankan, Client A dan Client B saling bertukar pesan real-time, pengujian `/users`, demonstrasi penanganan disconnect, serta eksekusi benchmark.
