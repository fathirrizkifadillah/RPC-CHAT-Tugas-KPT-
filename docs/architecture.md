# Arsitektur Sistem Distributed Chat Room gRPC

Dokumentasi rancangan arsitektur sistem chat terdistribusi mengacu pada diagram `arsitektur-chat-room.svg` dan spesifikasi akademis mata kuliah Komputasi Paralel dan Terdistribusi.

---

## 1. Diagram Komponen dan Koneksi

Merujuk pada diagram `arsitektur-chat-room.svg`:

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

---

## 2. Rincian Komponen Utama

### A. Transport dan Protokol
- **Transport**: HTTP/2 over TCP pada port default `50051`.
- **Serialisasi**: Protocol Buffers v3 (`proto/chat_room.proto`).
- **Pola Komunikasi**:
  - Unary RPC: `Join`, `ListUsers`, `SendMessage`.
  - Bidirectional Streaming RPC: `Chat` (aliran dua arah simultan).

### B. Container Server & Service (`LayananChat`)
- **Worker Concurrency**: Dikelola oleh `concurrent.futures.ThreadPoolExecutor` dengan 30–50 thread worker untuk melayani banyak panggilan RPC konkuren.
- **Service Handlers**:
  1. `Join(JoinRequest) -> JoinResponse`: Registrasi sesi pengguna baru, verifikasi nama unik, penetapan `user_id`.
  2. `ListUsers(ListUsersRequest) -> ListUsersResponse`: Pengambilan snapshot daftar pengguna online.
  3. `SendMessage(SendMessageRequest) -> SendMessageResponse`: Pengiriman pesan mandiri dengan pengecekan `request_id` di `PROSES`.
  4. `Chat(stream ChatFrame) -> stream ChatFrame`: Duplex stream di mana frame masuk diproses oleh incoming reader thread dan frame keluar diambil dari antrean pesan per client.

### C. Shared State di Memori (`ChatState`)
1. **`users` (Registry Pengguna)**:
   - Menyimpan pemetaan `user_id -> UserDict` (username, client_id, connected_at, status aktif).
   - Dilindungi oleh `threading.RLock()` untuk mencegah kondisi balapan (*race condition*) saat registrasi atau disconnect.
2. **`queue` (Antrean Pesan Per Client)**:
   - Setiap client yang membuka stream memiliki antrean `queue.Queue(maxsize=100)`.
   - Mengisolasi client cepat dari client lambat (*slow client isolation*).
   - Enqueue dilakukan secara non-blocking dengan kebijakan *drop-oldest* saat kapasitas penuh.
3. **`PROSES` (Deduplikasi At-Most-Once)**:
   - Menyimpan `request_id -> cached_response` untuk menyaring permintaan ulang akibat timeout atau retry jaringan.
   - Menjamin bahwa operasi pengiriman pesan yang diulang tidak menghasilkan publikasi ganda.

---

## 3. Keputusan Desain Terkait (ADRs)

- [ADR-001: In-Memory Concurrency and Message Queue Architecture](decisions/ADR-001.md)
- [ADR-002: Request-ID Deduplication and Semantics of Unary vs Streaming RPC](decisions/ADR-002.md)
- [ADR-003: Client Retry and Exponential Backoff Strategy](decisions/ADR-003.md)
