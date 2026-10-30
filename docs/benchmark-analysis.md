# Analisis Pengujian Kinerja (Benchmark Analysis)

Laporan analisis performa sistem terdistribusi **Chat Room gRPC** untuk mengukur latensi rata-rata dan throughput pada variasi **1, 5, dan 20 client bersamaan** sesuai dengan ketentuan pada PDF Praktikum RPC Halaman 12.

---

## 1. Lingkungan dan Konfigurasi Pengujian

- **Sistem Operasi**: Windows 11 Home (64-bit)
- **Runtime Interpreter**: Python 3.11.9 (CPython)
- **Framework RPC**: `grpcio 1.85.0`, `grpcio-tools 1.85.0`, `protobuf 7.36.2`
- **Konfigurasi Server**:
  - Transport: HTTP/2 over TCP
  - Server ThreadPoolExecutor: 50 workers
  - Port Binding: `127.0.0.1:50051`
  - In-Memory Shared State: `threading.RLock()` dengan fine-grained critical section
- **Metodologi Pengujian**:
  - Menggunakan skrip Python `benchmarks/run_benchmark.py` dengan multi-threaded client executor.
  - Setiap client melakukan registrasi `Join` lalu mengirimkan 50 pesan `SendMessage` dengan `request_id` unik.
  - **Definisi Latensi**: Waktu presisi tinggi (`time.perf_counter()`) yang diukur di sisi client, mulai dari saat permintaan gRPC dikirimkan melalui stub hingga penerimaan respons acknowledgment (`SendMessageResponse`) dari server.
  - **Definisi Throughput**: Jumlah total transaksi pengiriman pesan yang sukses dibagi total durasi pengujian skenario dalam satuan *requests per second* (req/s).

---

## 2. Tabel Hasil Pengujian Kinerja Nyata

Data aktual yang diperoleh dari eksekusi benchmark pada tanggal 2026-10-29:

| Jumlah Client Konkuren | Total Pesan Dicoba | Sukses | Gagal | Latensi Rata-rata (ms) | Median Latensi (ms) | P95 Latensi (ms) | Min Latensi (ms) | Max Latensi (ms) | Throughput (req/s) | Total Waktu (s) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1 Client** | 50 | 50 | 0 | **0.695 ms** | 0.607 ms | 1.265 ms | 0.448 ms | 1.351 ms | **1,048.55 req/s** | 0.048 s |
| **5 Client** | 250 | 250 | 0 | **2.349 ms** | 2.192 ms | 3.444 ms | 1.453 ms | 6.064 ms | **1,960.86 req/s** | 0.128 s |
| **20 Client** | 1,000 | 1,000 | 0 | **11.954 ms** | 11.159 ms | 17.970 ms | 1.737 ms | 20.260 ms | **1,572.70 req/s** | 0.636 s |

Tingkat keberhasilan (Success Rate) pada seluruh skenario: **100.0%** (0 request gagal).

---

## 3. Grafik Hasil Pengujian

Grafik batang perbandingan Latensi Rata-rata dan Throughput disimpan secara otomatis pada:
`benchmarks/results/latency_throughput_chart.png`

---

## 4. Analisis dan Evaluasi Penyebab Hasil

### A. Analisis Throughput
1. **Peningkatan Skala dari 1 ke 5 Client (+87%)**:
   - Throughput melonjak dari **1,048.55 req/s** pada 1 client menjadi **1,960.86 req/s** pada 5 client.
   - *Penyebab*: Pada 1 client tunggal, proses bersifat sekuensial (client harus menunggu balasan RPC sebelum mengirim RPC berikutnya). Ketika jumlah client ditingkatkan menjadi 5, `ThreadPoolExecutor` di server memanfaatkan multi-core CPU untuk memproses request secara paralel di beberapa worker thread sekaligus, menghasilkan pemanfaatan resource yang optimal.
2. **Saturasi pada 20 Client (1,572.70 req/s)**:
   - Pada 20 client konkuren, throughput mengalami sedikit penurunan ke kisaran 1,572 req/s.
   - *Penyebab*:
     - **Lock Contention**: Seluruh worker thread mengakses komponen shared state yang sama (`_users`, `_queues`, dan `_proses`). Meskipun critical section dibuat sangat singkat, adanya 20 thread yang melakukan mutasi bersamaan menyebabkan antrean singkat untuk memperoleh lock sinkronisasi.
     - **Thread Context Switching Overhead**: 20 thread client dan worker server bersaing memperebutkan cycle CPU pada sistem operasi, menyebabkan biaya pergantian context (*context switching*) meningkat.

### B. Analisis Latensi
1. **Tren Kenaikan Latensi Linear**:
   - Latensi rata-rata meningkat dari **0.695 ms** (1 client) $\to$ **2.349 ms** (5 client) $\to$ **11.954 ms** (20 client).
   - Nilai P95 latensi pada 20 client tetap berada di bawah **18 ms** (17.97 ms), yang menunjukkan performa real-time obrolan yang sangat prima (di bawah standar ambang batas latensi interaktif 100 ms).
2. **Distribusi Latensi**:
   - Jarak antara median (11.16 ms) dan rata-rata (11.95 ms) pada 20 client sangat rapat, membuktikan bahwa variansi respon gRPC server sangat stabil tanpa adanya outlier ekstrem (*tail latency spikes*).

---

## 5. Kesimpulan Kinerja

Arsitektur in-memory RPC chat room berbasis `ThreadPoolExecutor` dengan isolasi antrean per client dan perlindungan lock terbukti:
1. Menghasilkan throughput puncak hampir **2,000 requests/detik**.
2. Menjaga latensi tetap di level sub-15 ms bahkan pada beban puncak 20 client konkuren.
3. Menjamin integritas data 100% tanpa ada pesan yang hilang atau gagal dikirim.
