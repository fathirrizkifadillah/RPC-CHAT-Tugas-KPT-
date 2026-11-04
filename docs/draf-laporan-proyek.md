# LAPORAN TUGAS PROYEK MINI
## KOMPUTASI PARALEL DAN TERDISTRIBUSI
### IMPLEMENTASI SISTEM TERDISTRIBUSI BERBASIS RPC: DISTRIBUTED CHAT ROOM DENGAN gRPC DAN PYTHON

---

**Disusun Oleh: Kelompok [NOMOR_KELOMPOK]**
**Kelas**: [KELAS, misal: IF-45-01 / KPT-A]  
**Dosen Pengampu**: [NAMA DOSEN PENGAMPU]  
**Program Studi**: Informatika / Teknik Informatika / Ilmu Komputer  
**Fakultas / Universitas**: [NAMA FAKULTAS DAN UNIVERSITAS]  
**Tahun Akademik**: 2026 / 2027  

---

### IDENTITAS ANGGOTA KELOMPOK

| No | Nama Lengkap Mahasiswa | NIM | Peran Utama & Lingkup Modul | Bukti Commit Git Utama |
|:---:|---|:---:|---|---|
| 1 | Fathir *(Ketua)* | `[NIM FATHIR]` | Desain IDL `.proto`, Arsitektur Server gRPC, Concurrency State Management | `feat(proto): ...`, `feat(server): ...` |
| 2 | Ajib | `[NIM AJIB]` | Client CLI Terminal, Toleransi Kegagalan (Retry Backoff, Timeout, Deduplikasi) | `feat(client): ...`, `feat(resilience): ...` |
| 3 | Reza | `[NIM REZA]` | Otomasi Pengujian (Pytest 22 Kasus), Docker Multi-Container, Benchmark Kinerja | `test: ...`, `ci(docker): ...`, `perf: ...` |

- **Tautan Repositori Git**: `https://github.com/[ORGANISASI_ATAU_USER]/[NAMA_REPO_PROYEK_RPC]`
- **Tautan Video Demonstrasi Sistem (Durasi Maksimal 5 Menit)**: `https://youtu.be/[ID_VIDEO_YOUTUBE]`

---

## DAFTAR ISI

1. **BAB 1 — DESKRIPSI STUDI KASUS DAN DIAGRAM ARSITEKTUR**
   - 1.1 Latar Belakang dan Deskripsi Studi Kasus
   - 1.2 Diagram Arsitektur Komponen Sistem
   - 1.3 Alur Komunikasi dan Interaksi Pemanggilan RPC
2. **BAB 2 — SPESIFIKASI DAN PENJELASAN INTERFACE DEFINITION LANGUAGE (`.proto`)**
   - 2.1 Kode Sumber Lengkap `chat_room.proto`
   - 2.2 Penjelasan Rinci Setiap RPC
   - 2.3 Desain Payload Data dan Skema Frame Streaming
3. **BAB 3 — STRATEGI CONCURRENCY DAN TOLERANSI KEGAGALAN**
   - 3.1 Manajemen Concurrency dan Sinkronisasi Shared Memory (`ChatState`)
   - 3.2 Isolasi Antrean Pesan per Client dan Penanganan *Slow Client*
   - 3.3 Semantik *At-Most-Once* Melalui Deduplikasi `PROSES` Berbasis `request_id`
   - 3.4 Mekanisme Timeout dan *Exponential Backoff Retry with Jitter*
   - 3.5 Penanganan *Client Disconnection* dan *Graceful Shutdown*
4. **BAB 4 — PENGUJIAN DAN ANALISIS KINERJA SISTEM**
   - 4.1 Metodologi dan Lingkungan Pengujian Beban
   - 4.2 Tabel Rekapitulasi Data Kinerja Aktual (1, 5, dan 20 Client)
   - 4.3 Visualisasi Kinerja (Grafik Latensi dan Throughput)
   - 4.4 Analisis Kritis Kinerja Berdasarkan Teori Antrean dan Sistem Terdistribusi
   - 4.5 Hasil Verifikasi Pengujian Fungsional Otomatis (Pytest)
5. **BAB 5 — PEMBAGIAN TUGAS DAN KONTRIBUSI ANGGOTA KELOMPOK**
   - 5.1 Rincian Kontribusi Setiap Anggota
   - 5.2 Log Riwayat Commit Repositori Git
6. **BAB 6 — TAUTAN REPOSITORI GIT DAN VIDEO DEMONSTRASI**
   - 6.1 Tautan Repositori Kode Sumber
   - 6.2 Tautan dan Skenario Video Demonstrasi
7. **DAFTAR PUSTAKA & PERNYATAAN INTEGRITAS AKADEMIK**

---

# BAB 1 — DESKRIPSI STUDI KASUS DAN DIAGRAM ARSITEKTUR

## 1.1 Latar Belakang dan Deskripsi Studi Kasus
Pada sistem terdistribusi, komunikasi antar-proses yang efisien, handal, dan berlatensi rendah menjadi pilar utama pembangunan aplikasi interaktif. Studi kasus yang dipilih pada proyek mini ini adalah **Pilihan Nomor 3: Chat Room banyak pengguna yang bertukar pesan secara real-time**.

Karakteristik utama dari studi kasus ini meliputi:
1. **Pertukaran Pesan Simultan**: Banyak client terdistribusi dapat mengirimkan dan menerima pesan secara bersamaan tanpa saling memblokir (*non-blocking asynchronous exchange*).
2. **Koordinasi Pengguna Aktif**: Server harus memelihara daftar pengguna online secara dinamis, mengumumkan pengguna baru yang bergabung, serta membersihkan sesi pengguna yang terputus secara tertib.
3. **Komunikasi Full-Duplex**: Menggunakan kemampuan *bidirectional streaming* gRPC di atas protokol transport HTTP/2, di mana client dan server dapat mengalirkan pesan dua arah melalui satu koneksi TCP persisten.
4. **Arsitektur In-Memory**: Menghindari ketergantungan basis data eksternal atau message broker pihak ketiga, sehingga pengujian difokuskan murni pada konsep konkurensi thread, sinkronisasi memori bersama (*shared state*), dan protokol RPC.

## 1.2 Diagram Arsitektur Komponen Sistem
Arsitektur dirancang dengan pemisahan yang jelas antara container client dan container server, mengacu pada diagram arsitektur sistem:

```
+-------------------------------------------------------+           +-------------------------------------------------------+
|                   CONTAINER CLIENT                    |           |                   CONTAINER SERVER                    |
|                                                       |           |                                                       |
|  +-------------------------------------------------+  |           |  +-------------------------------------------------+  |
|  |                  Client CLI A                   |  |   gRPC    |  |                   gRPC Server                   |  |
|  |     (Thread Kirim UI + Thread Terima Stream)    |  |<--------->|  |           (ThreadPoolExecutor, :50051)          |  |
|  +-------------------------------------------------+  |  Port     |  +-------------------------------------------------+  |
|                                                       |  50051    |                           |                           |
|  +-------------------------------------------------+  |           |                           v                           |
|  |                  Client CLI B                   |  |  HTTP/2   |  +-------------------------------------------------+  |
|  |     (Thread Kirim UI + Thread Terima Stream)    |  |<--------->|  |                   LayananChat                   |  |
|  +-------------------------------------------------+  |           |  |      (Join, ListUsers, SendMessage, Chat)       |  |
|                                                       |           |  +-------------------------------------------------+  |
|  +-------------------------------------------------+  |           |                           |                           |
|  |                  Client CLI N                   |  |           |                           v                           |
|  |          (Simulasi Beban s.d 20 Client)         |  |<--------->|  +-------------------------------------------------+  |
|  +-------------------------------------------------+  |           |  |             State Bersama di Memori             |  |
|                                                       |           |  |  * users : Registry User Aktif (threading.RLock) |  |
|                                                       |           |  |  * queue : Antrean Pesan Terisolasi Per Client   |  |
|                                                       |           |  |  * PROSES: Deduplikasi Request ID (At-Most-Once) |  |
|                                                       |           |  +-------------------------------------------------+  |
+-------------------------------------------------------+           +-------------------------------------------------------+
```

## 1.3 Alur Komunikasi dan Interaksi Pemanggilan RPC
Interaksi sistem terbagi dalam empat tahapan logis:
1. **Fase Registrasi / Handshake (`Join`)**:
   - Client mengirimkan Unary RPC `Join(JoinRequest)` berisi nama pengguna yang diinginkan.
   - Server memvalidasi keunikan username di dalam registry memori `users`. Jika valid, server mengembalikan status sukses beserta token `user_id` unik dan mencatat waktu koneksi.
2. **Fase Inisialisasi Aliran Streaming Dua Arah (`Chat`)**:
   - Client membuka koneksi bidirectional streaming `Chat(stream ChatFrame)`.
   - Client mengirimkan frame pembuka berjenis `FRAME_TYPE_JOIN`.
   - Server membuat struktur antrean privat `queue.Queue` khusus untuk client tersebut, mengirimkan frame konfirmasi `FRAME_TYPE_ACK`, serta membroadcast frame notifikasi `FRAME_TYPE_USER_EVENT` ke seluruh client lain yang sedang aktif.
3. **Fase Pertukaran Pesan (*Messaging*)**:
   - **Jalur Streaming (Utama)**: Client mengirimkan `ChatFrame` bertipe `FRAME_TYPE_MESSAGE`. Server memvalidasi `request_id`, mencatat ke komponen `PROSES`, lalu menduplikasi pesan ke antrean seluruh client aktif.
   - **Jalur Unary (Alternatif)**: Client dapat memanggil RPC Unary `SendMessage` untuk skenario pesan terisolasi yang membutuhkan respons acknowledgment langsung.
4. **Fase Pemutusan Koneksi (*Disconnect*)**:
   - Client mengirim frame `FRAME_TYPE_LEAVE` atau koneksi terputus mendadak.
   - Server melalui callback `context.add_callback()` secara otomatis mendeteksi terputusnya stream, menghapus user dari registry `users`, membersihkan antrean terkait, dan membroadcast event keluarnya pengguna ke seluruh client yang tersisa.

---

# BAB 2 — SPESIFIKASI DAN PENJELASAN INTERFACE DEFINITION LANGUAGE (`.proto`)

## 2.1 Kode Sumber Lengkap `chat_room.proto`
Kontrak layanan didefinisikan menggunakan **Protocol Buffers versi 3 (proto3)** pada berkas `proto/chat_room.proto`:

```protobuf
syntax = "proto3";

package chat_room;

// Layanan utama Chat Room RPC terdistribusi
service LayananChat {
  // RPC 1: Join / Registrasi sesi pengguna baru (Unary)
  rpc Join (JoinRequest) returns (JoinResponse);

  // RPC 2: Mengambil daftar pengguna aktif di memori server (Unary)
  rpc ListUsers (ListUsersRequest) returns (ListUsersResponse);

  // RPC 3: Jalur Unary untuk pengiriman pesan mandiri dengan request_id
  rpc SendMessage (SendMessageRequest) returns (SendMessageResponse);

  // RPC 4: Jalur Bidirectional Streaming untuk pertukaran pesan real-time
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
}
```

## 2.2 Penjelasan Rinci Setiap RPC

### 1. `rpc Join (JoinRequest) returns (JoinResponse)`
- **Pola Komunikasi**: Unary RPC (Request-Response).
- **Semantik**: Idempoten terhadap `request_id` dan `client_id` yang sama.
- **Tujuan**: Mendaftarkan identitas pengguna sebelum bergabung ke dalam ruang obrolan.
- **Penanganan Error**: Melempar status gRPC `INVALID_ARGUMENT` jika username kosong, dan `ALREADY_EXISTS` jika username sedang digunakan oleh client aktif lain.

### 2. `rpc ListUsers (ListUsersRequest) returns (ListUsersResponse)`
- **Pola Komunikasi**: Unary RPC (Request-Response).
- **Semantik**: Idempoten murni (Read-Only).
- **Tujuan**: Mengambil snapshot instan dari seluruh pengguna yang tercatat dalam memori server.
- **Karakteristik**: Menggunakan field protobuf bertipe `repeated UserInfo` untuk serialisasi array pengguna yang efisien.

### 3. `rpc SendMessage (SendMessageRequest) returns (SendMessageResponse)`
- **Pola Komunikasi**: Unary RPC (Request-Response).
- **Semantik**: *At-most-once* dengan proteksi `request_id`.
- **Tujuan**: Menyediakan jalur pengiriman pesan alternatif yang terpisah dari streaming, ideal untuk pengujian toleransi kegagalan dan client yang membutuhkan kepastian pengiriman (*ACK*) berbasis request-response.

### 4. `rpc Chat (stream ChatFrame) returns (stream ChatFrame)`
- **Pola Komunikasi**: Bidirectional Streaming RPC (Duplex Stream).
- **Semantik**: Aliran kejadian terurut (*ordered event stream*).
- **Tujuan**: Inti sistem obrolan real-time. Client mempertahankan satu koneksi HTTP/2 terbuka di mana client secara kontinu mengirimkan frame obrolan dan menerima frame yang dibroadcast oleh server secara simultan.

---

# BAB 3 — STRATEGI CONCURRENCY DAN TOLERANSI KEGAGALAN

## 3.1 Manajemen Concurrency dan Sinkronisasi Shared Memory (`ChatState`)
Server gRPC dijalankan menggunakan `concurrent.futures.ThreadPoolExecutor(max_workers=30)` yang mampu menangani puluhan pemanggilan RPC konkuren secara paralel. Karena memori server diakses oleh banyak thread worker secara simultan, struktur `ChatState` dilindungi dengan `threading.RLock()`:

```python
# Potongan kode implementasi pada src/chat_room/state.py
class ChatState:
    def __init__(self, queue_maxsize=100, max_proses=10000):
        self._lock = threading.RLock()
        self._users = {}        # user_id -> dict(username, client_id, ...)
        self._usernames = {}    # username -> user_id
        self._queues = {}       # user_id -> queue.Queue
        self._proses = OrderedDict() # request_id -> cached_response
```

### Prinsip *Critical Section* Minimal
Untuk mencegah fenomena *lock contention* yang dapat menurunkan throughput server, lock **HANYA** dipegang ketika melakukan mutasi dictionary atau menyalin snapshot list. Lock **TIDAK PERNAH** dipegang saat melakukan operasi I/O jaringan atau menunggu antrean.

## 3.2 Isolasi Antrean Pesan per Client dan Penanganan *Slow Client*
Setiap client yang membuka stream `Chat` memiliki antrean mandiri berkapasitas terbatas (`queue.Queue(maxsize=100)`). Desain ini menjamin bahwa satu client dengan koneksi internet lambat (*slow consumer*) tidak akan memblokir pengiriman pesan ke client-client lainnya (*Head-of-Line Blocking Prevention*):

```python
def broadcast_frame(self, frame: pb.ChatFrame, exclude_user_id=None) -> int:
    with self._lock:
        # Ambil snapshot referensi antrean di bawah lock
        target_queues = [(uid, q) for uid, q in self._queues.items() if uid != exclude_user_id]

    delivered_count = 0
    for uid, q in target_queues:
        try:
            q.put_nowait(frame)  # Non-blocking enqueue
            delivered_count += 1
        except queue.Full:
            # Kebijakan Drop-Oldest untuk Slow Client
            try:
                _ = q.get_nowait()
                q.put_nowait(frame)
                delivered_count += 1
            except Exception:
                pass
    return delivered_count
```

## 3.3 Semantik *At-Most-Once* Melalui Deduplikasi `PROSES` Berbasis `request_id`
Pada jaringan terdistribusi, pengulangan (*retry*) akibat timeout dapat menyebabkan pesan yang sama dikirim dua kali. Sistem menerapkan semantik **At-Most-Once** menggunakan tabel memori `PROSES`:
1. Setiap pesan diberi identitas unik `request_id` (berbasis UUID v4).
2. Ketika server menerima pesan, server memeriksa apakah `request_id` sudah ada di `PROSES`.
3. **Cache Hit**: Server langsung mengembalikan respons yang tersimpan tanpa membroadcast ulang ke client lain.
4. **Cache Miss**: Server membroadcast pesan, menyimpan respons ke `PROSES`, lalu membalas ke pengirim.

```python
with self._lock:
    if request_id and request_id in self._proses:
        # Kembalikan cache instan (idempoten)
        return self._proses[request_id]
```

> **Catatan Batasan Arsitektur**: Karena state disimpan di RAM (in-memory), histori deduplikasi akan hilang bila server mengalami restart. Pada implementasi skala produksi industri, tabel `PROSES` dapat dipersistensikan ke Redis atau database relasional.

## 3.4 Mekanisme Timeout dan *Exponential Backoff Retry with Jitter*
Client dilengkapi mekanisme ketahanan jaringan yang tidak melakukan retry membabi buta (*blind retry*), melainkan menyaring status gRPC yang tergolong *transient*:

```python
# Formula jeda retry pada src/chat_room/client.py
can_retry = e.code() in (
    grpc.StatusCode.DEADLINE_EXCEEDED,
    grpc.StatusCode.UNAVAILABLE,
    grpc.StatusCode.RESOURCE_EXHAUSTED
)
if can_retry and attempt < self.max_retries:
    delay = self.base_retry_delay * (2 ** (attempt - 1)) + random.uniform(0.01, 0.1)
    time.sleep(delay)
```
- **Request ID Stabil**: Pada percobaan ke-1, 2, hingga ke-N, client **mempertahankan `request_id` yang sama persis** sehingga server dapat mendeteksi duplikasi saat retry berhasil mencapai server.

## 3.5 Penanganan *Client Disconnection* dan *Graceful Shutdown*
- **Sisi Server**: Menggunakan `context.add_callback(cleanup)` yang otomatis dieksekusi oleh runtime gRPC ketika koneksi stream terputus. Callback ini mencabut antrean pengguna, menghapus identitas dari `users`, dan membroadcast frame `FRAME_TYPE_USER_EVENT` (keluar) ke pengguna lain.
- **Graceful Shutdown**: Server menangani sinyal `SIGINT` / `SIGTERM` dengan memanggil `server.stop(grace=3.0)` untuk memberikan jendela waktu bagi thread yang sedang memproses frame menyelesaikan pekerjaannya sebelum socket ditutup.

---

# BAB 4 — PENGUJIAN DAN ANALISIS KINERJA SISTEM

## 4.1 Metodologi dan Lingkungan Pengujian Beban
Pengujian kinerja dilakukan secara mandiri menggunakan skrip benchmark berbasis multi-threading Python (`benchmarks/run_benchmark.py`) sesuai spesifikasi resmi pada PDF tugas halaman 12.

- **Spesifikasi Lingkungan Uji**:
  - Processor: AMD Ryzen / Intel Core Multi-Core CPU
  - Sistem Operasi: Windows 11 Home 64-bit
  - Interpreter: Python 3.11.9 (CPython) dengan optimasi Faster CPython
  - Transport gRPC: HTTP/2 over loopback socket TCP (`127.0.0.1:50051`)
  - Server Thread Pool: 50 worker threads
- **Metode Pengukuran**:
  - Dilakukan pengujian untuk **1, 5, dan 20 client bersamaan**.
  - Setiap client mengirimkan 50 pesan secara konkuren (Total: 50, 250, dan 1.000 permintaan).
  - Waktu diukur menggunakan `time.perf_counter()` dengan presisi nanodetik di sisi client mulai dari transmisi frame hingga penerimaan respons acknowledgment.

## 4.2 Tabel Rekapitulasi Data Kinerja Aktual

Berikut adalah data kuantitatif hasil pengujian aktual:

| Parameter Metrik | 1 Client Konkuren | 5 Client Konkuren | 20 Client Konkuren |
|---|:---:|:---:|:---:|
| **Jumlah Permintaan Total** | 50 | 250 | 1.000 |
| **Permintaan Berhasil (Sukses)** | 50 (100.0%) | 250 (100.0%) | 1.000 (100.0%) |
| **Permintaan Gagal (Error / Timeout)** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| **Latensi Rata-rata (*Mean*)** | **0.695 ms** | **2.349 ms** | **11.954 ms** |
| **Latensi Median (*P50*)** | 0.607 ms | 2.192 ms | 11.159 ms |
| **Latensi 95th Percentile (*P95*)** | 1.265 ms | 3.444 ms | 17.970 ms |
| **Latensi Minimum** | 0.448 ms | 1.453 ms | 1.737 ms |
| **Latensi Maksimum** | 1.351 ms | 6.064 ms | 20.260 ms |
| **Throughput Sistem** | **1.048,55 req/detik** | **1.960,86 req/detik** | **1.572,70 req/detik** |
| **Total Durasi Eksekusi** | 0,0477 detik | 0,1275 detik | 0,6358 detik |

## 4.3 Visualisasi Kinerja (Grafik Latensi dan Throughput)
Visualisasi grafis metrik kinerja digenerate secara otomatis menggunakan pustaka Matplotlib dan tersimpan pada berkas `benchmarks/results/latency_throughput_chart.png`:

*(Sertakan gambar grafik di bawah ini pada laporan cetak/PDF):*
```
+-----------------------------------------------------------------------------------------+
|                  ANALISIS KINERJA SISTEM DISTRIBUTED CHAT ROOM gRPC                     |
|                                                                                         |
|       [Grafik Batang: Latensi Rata-rata]           [Grafik Batang: Throughput Sistem]   |
|   15ms |                                       2000 |              1960.9 req/s         |
|        |                   11.95 ms                 |             +------------+        |
|   10ms |                  +--------+           1500 |             |            | 1572.7 |
|        |                  |        |                | 1048.5      |            |+------+|
|    5ms |         2.35 ms  |        |           1000 |+------+     |            ||      ||
|        | 0.70ms +------+  |        |                ||      |     |            ||      ||
|    0ms +--------+------+--+--------+              0 +-------+-----+------------++------++
|         1 Client 5 Client 20 Client                  1 Client        5 Client   20 Client
+-----------------------------------------------------------------------------------------+
```

## 4.4 Analisis Kritis Kinerja Berdasarkan Teori Sistem Terdistribusi

### A. Analisis Throughput dan *Scalability Inflection Point*
1. **Peningkatan Skala 1 ke 5 Client (+87%)**:
   Throughput melonjak drastis dari **1.048,55 req/s** menjadi **1.960,86 req/s**. Pada 1 client tunggal, pemanggilan bersifat sinkron-sekuensial (*lock-step*). Ketika 5 client bekerja bersamaan, `ThreadPoolExecutor` server memanfaatkan multi-core CPU untuk memproses thread RPC secara konkuren, meningkatkan utilisasi sumber daya komputasi secara optimal.
2. **Saturasi pada 20 Client (1.572,70 req/s)**:
   Saat client ditingkatkan menjadi 20, throughput mengalami penurunan moderat ke kisaran 1.572 req/s. Berdasarkan hukum Amdahl dan teori antrean Little's Law ($L = \lambda W$), fenomena ini disebabkan oleh dua faktor utama:
   - **Lock Contention**: Komponen `ChatState` menggunakan `threading.RLock()` bersama. Dengan 20 client aktif yang mempublikasikan pesan secara simultan, waktu tunggu antrean thread (*thread lock acquisition overhead*) meningkat.
   - **Context Switching**: Menjalankan 20 thread client dan puluhan thread worker gRPC melebihi jumlah core CPU fisik, menimbulkan beban *thread context switching* pada kernel sistem operasi.

### B. Analisis Latensi dan Stabilitas Real-Time
- **Pertumbuhan Latensi Linier**: Latensi rata-rata bergeser dari sub-milidetik (0,695 ms) pada 1 client, menjadi 2,349 ms pada 5 client, dan 11,954 ms pada 20 client.
- **Kepatuhan Terhadap Standar Interaktif**: Nilai latensi P95 pada 20 client tercatat sebesar **17,97 ms**. Angka ini jauh di bawah ambang batas persepsi latensi manusia untuk obrolan interaktif real-time (100 ms), membuktikan bahwa sistem memiliki responsivitas yang sangat baik.
- **Kerapatan Median dan Mean**: Jarak yang sempit antara median (11,16 ms) dan rata-rata (11,95 ms) pada 20 client membuktikan bahwa tidak terjadi lonjakan latensi ekstrim (*tail latency jitter*).

## 4.5 Hasil Verifikasi Pengujian Fungsional Otomatis (Pytest)
Pengujian otomatis dijalankan melalui pytest di dalam virtual environment, mencakup **22 skenario pengujian unit dan integrasi**:

```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\TUGAS\KPT\RPC_CHAT
collected 22 items

tests/test_broadcast.py::test_broadcast_between_client_a_and_client_b PASSED   [  4%]
tests/test_chat_stream.py::test_chat_bidirectional_stream_join_and_message PASSED [  9%]
tests/test_concurrency.py::test_concurrent_user_registrations_and_messages PASSED [ 13%]
tests/test_deduplication.py::test_send_message_deduplication_via_proses PASSED [ 18%]
tests/test_deduplication.py::test_send_message_different_request_ids_broadcasts_twice PASSED [ 22%]
tests/test_disconnect.py::test_disconnect_removes_user_and_broadcasts_leave_event PASSED [ 27%]
tests/test_errors.py::test_join_whitespace_only_username PASSED                [ 31%]
tests/test_errors.py::test_send_message_empty_content_and_sender PASSED        [ 36%]
tests/test_errors.py::test_stream_join_with_invalid_username_emits_error_frame PASSED [ 40%]
tests/test_join.py::test_join_success PASSED                                   [ 45%]
tests/test_join.py::test_join_empty_username_fails PASSED                      [ 50%]
tests/test_join.py::test_join_duplicate_username_fails PASSED                  [ 54%]
tests/test_join.py::test_join_idempotent_reconnect PASSED                      [ 59%]
tests/test_list_users.py::test_list_users_initially_empty PASSED               [ 63%]
tests/test_list_users.py::test_list_users_multiple_registered PASSED           [ 68%]
tests/test_queue_backpressure.py::test_slow_client_queue_drop_oldest_policy PASSED [ 72%]
tests/test_send_message.py::test_send_message_unary_success PASSED             [ 77%]
tests/test_send_message.py::test_send_message_invalid_payload_fails PASSED       [ 81%]
tests/test_server_lifecycle.py::test_server_startup_and_graceful_stop PASSED   [ 86%]
tests/test_timeout_retry.py::test_client_timeout_raises_deadline_exceeded PASSED [ 90%]
tests/test_timeout_retry.py::test_client_retry_maintains_stable_request_id PASSED [ 95%]
tests/test_timeout_retry.py::test_client_no_retry_on_invalid_argument PASSED   [100%]

============================= 22 passed in 4.10s ==============================
```
Tingkat Keberhasilan: **100% Lulus (22 passed, 0 failed)**.

---

# BAB 5 — PEMBAGIAN TUGAS DAN KONTRIBUSI ANGGOTA KELOMPOK

Sesuai dengan ketentuan pada rubrik penilaian (setiap anggota kelompok wajib memahami proyek dan memiliki riwayat commit nyata), berikut pembagian tanggung jawab teknis:

### 1. Fathir (Ketua Kelompok — NIM: [NIM FATHIR])
- **Fokus Modul**: Desain IDL `.proto`, Arsitektur Server gRPC, Concurrency State Management.
- **Rincian Kontribusi**:
  - Menyusun kontrak antarmuka `proto/chat_room.proto` dan konfigurasi kompilasi stub `scripts/generate_stubs.py`.
  - Mengimplementasikan server utama `src/chat_room/server.py` dengan konfigurasi `ThreadPoolExecutor`.
  - Merancang logika sinkronisasi thread-safe pada `src/chat_room/state.py` (`users`, `queue`, `PROSES`).
- **Commit Git Utama**: `feat(proto): ...`, `feat(server): ...`.

### 2. Ajib (Anggota — NIM: [NIM AJIB])
- **Fokus Modul**: Client CLI Terminal, Toleransi Kegagalan (Retry Backoff, Timeout, Deduplikasi).
- **Rincian Kontribusi**:
  - Mengembangkan antarmuka interaktif terminal pada `src/chat_room/client.py`.
  - Mengimplementasikan thread pembaca stream dan generator pengirim frame dua arah.
  - Menerapkan algoritma *exponential backoff retry with jitter* serta penanganan status gRPC sementara.
  - Memastikan kestabilan pengiriman `request_id` unik untuk mencegah duplikasi pesan.
- **Commit Git Utama**: `feat(client): ...`, `feat(resilience): ...`.

### 3. Reza (Anggota — NIM: [NIM REZA])
- **Fokus Modul**: Otomasi Pengujian (Pytest 22 Kasus), Containerisasi Docker, dan Pengujian Kinerja.
- **Rincian Kontribusi**:
  - Menyusun rangkaian 22 pengujian otomatis pada direktori `tests/` (`conftest.py`, `test_concurrency.py`, dll).
  - Menyusun konfigurasi `Dockerfile` multi-stage dan orkestrasi `docker-compose.yml`.
  - Membangun skrip benchmark multi-client `benchmarks/run_benchmark.py` dan mengekspor visualisasi Matplotlib.
  - Menyusun dokumentasi teknis dan draf laporan proyek.
- **Commit Git Utama**: `test: ...`, `ci(docker): ...`, `perf: ...`.

---

# BAB 6 — TAUTAN REPOSITORI GIT DAN VIDEO DEMONSTRASI

## 6.1 Tautan Repositori Kode Sumber
- **URL Repositori**: `https://github.com/[USERNAME]/[NAMA_REPO_PROYEK_RPC]`
- Repositori berisi seluruh struktur kode sumber, konfigurasi Docker, dokumen arsitektur (ADRs), dan petunjuk instalasi di `README.md`.

## 6.2 Tautan dan Skenario Video Demonstrasi
- **URL Video Demonstrasi**: `https://youtu.be/[ID_VIDEO_YOUTUBE]` *(Durasi: Maksimal 5 Menit)*
- **Struktur Skenario Demonstrasi dalam Video**:
  1. **Menit 00:00 – 00:45 (Pendahuluan)**: Perkenalan anggota kelompok dan penjelasan singkat diagram arsitektur gRPC (`arsitektur-chat-room.svg`).
  2. **Menit 00:45 – 02:00 (Demo Komunikasi Real-Time)**: Menjalankan Server gRPC, menghubungkan Client A (Alice) dan Client B (Bob), mendemonstrasikan pertukaran pesan real-time melalui *bidirectional streaming*.
  3. **Menit 02:00 – 02:45 (Fitur Unary RPC & ListUsers)**: Mendemonstrasikan pemanggilan `/users` untuk melihat daftar online dan `/unary <pesan>` dengan perlindungan request_id.
  4. **Menit 02:45 – 03:30 (Toleransi Kegagalan & Disconnect)**: Mendemonstrasikan pemutusan salah satu client (Alice keluar) dan verifikasi bahwa server membersihkan sesi serta membroadcast notifikasi leave ke Bob.
  5. **Menit 03:30 – 04:30 (Pengujian Kinerja & Pytest)**: Menjalankan `pytest -v` (22 passed) dan skrip `run_benchmark.py` untuk 1, 5, dan 20 client.
  6. **Menit 04:30 – 05:00 (Penutup)**: Kesimpulan ketercapaian tujuan proyek dan penutup.

---

# DAFTAR PUSTAKA & PERNYATAAN INTEGRITAS AKADEMIK

1. Google LLC. (2024). *gRPC Python Documentation and Tutorials*. https://grpc.io/docs/languages/python/
2. Protocol Buffers Documentation. (2024). *Language Guide (proto3)*. https://protobuf.dev/programming-guides/proto3/
3. Tanenbaum, A. S., & Van Steen, M. (2017). *Distributed Systems: Principles and Paradigms (3rd Edition)*. CreateSpace Independent Publishing Platform.
4. Tim Dosen Komputasi Paralel dan Terdistribusi. (2026). *Modul Latihan & Praktikum Remote Procedure Calls (RPC)*.

**Pernyataan Integritas Akademik**:
Kami menyatakan dengan sesungguhnya bahwa kode program, analisis, dan isi laporan proyek mini ini dikerjakan oleh kelompok kami secara mandiri sesuai dengan kaidah etika akademik. Bantuan kecerdasan buatan (*AI Assistant*) digunakan sebagai alat bantu pengembangan kode dan peninjauan dokumentasi sesuai panduan praktikum tanpa melakukan plagiasi terhadap pekerjaan kelompok lain.
