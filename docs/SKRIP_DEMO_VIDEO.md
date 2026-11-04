# SKRIP DEMONSTRASI VIDEO TUGAS PROYEK MINI RPC (gRPC CHAT ROOM)
**Mata Kuliah**: Komputasi Paralel dan Terdistribusi  
**Topik**: Sistem Terdistribusi Berbasis RPC — Kasus 3: Distributed Chat Room  
**Target Durasi**: 4 Menit 30 Detik (Maksimal 5 Menit)  
**Anggota Kelompok**:
1. **Fathir** (Ketua / Operator 2 Terminal di Laptop / Host Demo)
2. **Ajib** (Anggota — Penjelasan Arsitektur IDL `.proto` & Protokol Transport)
3. **Reza** (Anggota — Penjelasan Concurrency, Pytest 22 Kasus, & Analisis Kinerja)

**Setup Layar**: 2 Jendela Terminal Windows PowerShell Berdampingan (Kiri & Kanan), `(venv)` sudah aktif di kedua jendela.

---

## 🛠️ PERSIAPAN CEPAT (SEBELUM TEKAN TOMBOL RECORD)

Karena kedua terminal di layar laptop kamu sudah aktif `(venv)`-nya (seperti di screenshot):
- **Terminal Kiri**: Siap menerima perintah Server & Client Alice.
- **Terminal Kanan**: Siap menerima perintah Client Bob.
- **File Gambar Grafik**: Siapkan file `benchmarks/results/latency_throughput_chart.png` agar siap dibuka dengan double-click saat giliran Reza.

---

## 🎬 NASKAH LENGKAP KATA-DEMI-KATA & AKSI TERMINAL FATHIR

---

### BAGIAN 1: PEMBUKAAN & MENJALANKAN SERVER (00:00 – 00:45)
**Pembicara**: **Fathir**  
**Aksi Fathir di Terminal**: Menjalankan server di background pada Terminal Kiri.

#### 🎙️ Dialog Fathir:
> "Halo semuanya! Selamat datang di video demonstrasi Tugas Proyek Mini Komputasi Paralel dan Terdistribusi. Kami dari kelompok yang beranggotakan:  
> - Saya sendiri, Fathir selaku Ketua,  
> - Rekan saya Ajib, dan  
> - Rekan saya Reza.  
>  
> Pada tugas proyek mini ini, kami mengimplementasikan **Studi Kasus Nomor 3**, yaitu membangun sistem **Distributed Chat Room Real-Time** berbasis **gRPC dan Protocol Buffers** menggunakan Python.  
>  
> Di layar ini gue udah siapin dua jendela terminal berdampingan untuk mensimulasikan dua client terdistribusi. Pertama-tama, gue bakal jalanin server gRPC-nya terlebih dahulu di background lewat terminal kiri."

#### 💻 AKSI TERMINAL FATHIR #1:
> **Di Terminal Kiri**, ketik perintah berikut lalu tekan **Enter**:
```powershell
Start-Process python -ArgumentList "src/chat_room/server.py --port 50051" -WindowStyle Hidden
```
*(Server langsung aktif berjalan di latar belakang pada port 50051).*

#### 🎙️ Dialog Fathir (Oper ke Ajib):
> "Oke, server udah aktif di background pada port 50051. Sekarang rekan saya Ajib bakal jelasin kontrak antarmuka dan arsitektur RPC-nya terlebih dahulu."

---

### BAGIAN 2: PENJELASAN KONTRAK IDL & ARSITEKTUR RPC (00:45 – 01:25)
**Pembicara**: **Ajib**  
**Aksi Fathir**: Tetap di layar 2 terminal, bersiap mengetik perintah client.

#### 🎙️ Dialog Ajib:
> "Terima kasih Fathir. Sesuai ketentuan umum di panduan praktikum, antarmuka layanan wajib didefinisikan dalam file `.proto` dengan minimal 4 RPC. Pada file `chat_room.proto`, kami merancang 4 RPC lengkap:  
> 1. `rpc Join`: Unary RPC untuk registrasi sesi pengguna baru.  
> 2. `rpc ListUsers`: Unary RPC untuk mengambil daftar pengguna yang sedang aktif di memori server.  
> 3. `rpc SendMessage`: Unary RPC untuk pengiriman pesan dengan proteksi idempotensi `request_id`.  
> 4. `rpc Chat`: Bidirectional Streaming RPC untuk pertukaran pesan dua arah secara real-time melalui transport HTTP/2.  
>  
> Dengan Protocol Buffers dan HTTP/2, pesan diserialisasi menjadi format biner yang sangat ringkas dan efisien dibandingkan XML-RPC.  
> Sekarang, Fathir bakal langsung mendemokan interaksi obrolan antar-client di kedua terminal."

---

### BAGIAN 3: DEMO LIVE INTERAKSI CHAT DI 2 TERMINAL (01:25 – 03:05)
**Pembicara**: **Fathir**  
**Aksi Fathir di Terminal**: Mengetik dan menjalankan semua aksi obrolan secara live!

#### 💻 LANGKAH 1 — Hubungkan Alice di Terminal Kiri:
#### 🎙️ Dialog Fathir:
> "Sekarang di terminal sebelah kiri, gue bakal sambungin client pertama dengan username **Alice**."

> **Di Terminal Kiri**, ketik perintah ini lalu tekan **Enter**:
```powershell
python src/chat_room/client.py --username Alice
```
*(Hasil: Muncul banner `[SUCCESS] Berhasil bergabung sebagai Alice`, dan streaming chat langsung terbuka).*

---

#### 💻 LANGKAH 2 — Hubungkan Bob di Terminal Kanan:
#### 🎙️ Dialog Fathir:
> "Lanjut ke terminal sebelah kanan, gue sambungin client kedua dengan username **Bob**."

> **Di Terminal Kanan**, ketik perintah ini lalu tekan **Enter**:
```powershell
python src/chat_room/client.py --username Bob
```
*(Hasil: Muncul banner sukses di layar Bob, dan di terminal kiri milik Alice langsung otomatis muncul notifikasi bel: `🔔 Pengguna 'Bob' sedang aktif di room`).*

#### 🎙️ Dialog Fathir:
> "Bisa kita lihat, begitu Bob join, di terminal Alice langsung muncul notifikasi real-time bahwa Bob sudah aktif di room tanpa perlu Alice melakukan polling."

---

#### 💻 LANGKAH 3 — Tes Kirim Chat Real-Time Dua Arah:
#### 🎙️ Dialog Fathir:
> "Sekarang kita uji pertukaran pesan real-time lewat bidirectional streaming. Di terminal kiri, Alice bakal kirim pesan ke Bob."

> **Di Terminal Kiri (Alice)**, ketik teks ini lalu tekan **Enter**:
```text
Halo Bob! Selamat datang di gRPC Chat Room.
```
*(Hasil: Seketika pesan langsung muncul di Terminal Kanan Bob: `[XX:XX:XX] <Alice>: Halo Bob! Selamat datang di gRPC Chat Room.`)*

#### 🎙️ Dialog Fathir:
> "Pesan dari Alice langsung masuk ke layar Bob secara instan! Sekarang Bob bales dari terminal kanan."

> **Di Terminal Kanan (Bob)**, ketik teks ini lalu tekan **Enter**:
```text
Halo Alice! Pesan lu langsung masuk nih secara real-time.
```
*(Hasil: Pesan Bob langsung muncul di Terminal Kiri Alice).*

---

#### 💻 LANGKAH 4 — Uji Fitur Unary RPC `/users` (List Users):
#### 🎙️ Dialog Fathir:
> "Sekarang gue bakal uji fitur Unary RPC `ListUsers` pakai command `/users` di terminal Bob buat ngeliat siapa aja yang lagi online di memori server."

> **Di Terminal Kanan (Bob)**, ketik perintah ini lalu tekan **Enter**:
```text
/users
```
*(Hasil: Muncul tabel daftar pengguna: Alice (Online) dan Bob (Online)).*

#### 🎙️ Dialog Fathir:
> "Server langsung ngebalikin tabel daftar pengguna aktif yang tersimpan aman di shared memory server."

---

#### 💻 LANGKAH 5 — Uji Fitur Unary RPC `/unary` (SendMessage + Request ID Deduplication):
#### 🎙️ Dialog Fathir:
> "Selanjutnya, kita uji pengiriman pesan lewat jalur Unary RPC `SendMessage` dengan command `/unary`. Di sini client menyertakan UUID `request_id` unik untuk menjamin semantik **at-most-once**."

> **Di Terminal Kanan (Bob)**, ketik perintah ini lalu tekan **Enter**:
```text
/unary Ini pesan via jalur Unary RPC dengan proteksi request ID
```
*(Hasil: Muncul notifikasi pengiriman pesan berhasil dan pesan terbabar ke room).*

#### 🎙️ Dialog Fathir:
> "Dengan adanya `request_id` dan tabel deduplikasi `PROSES` di server, jika jaringan sempat putus dan client melakukan retry otomatis, pesan dipastikan tidak akan pernah terkirim ganda."

---

#### 💻 LANGKAH 6 — Uji Disconnect Handling & Toleransi Kegagalan:
#### 🎙️ Dialog Fathir:
> "Sekarang kita uji penanganan client terputus atau graceful disconnect. Di terminal kiri, Alice bakal keluar pakai command `/exit`."

> **Di Terminal Kiri (Alice)**, ketik perintah ini lalu tekan **Enter**:
```text
/exit
```
*(Hasil: Terminal Alice tertutup/kembali ke prompt PowerShell. Di Terminal Kanan Bob seketika muncul notifikasi: `🔔 Pengguna 'Alice' telah keluar dari room`).*

#### 🎙️ Dialog Fathir:
> "Alice keluar secara tertib, dan server langsung membroadcast event keluar ke Bob. Sekarang kita cek lagi daftar user di terminal Bob."

> **Di Terminal Kanan (Bob)**, ketik lagi:
```text
/users
```
*(Hasil: Status Alice langsung berubah Offline / terhapus dari daftar online).*

#### 🎙️ Dialog Fathir (Oper ke Reza):
> "Daftar user langsung ter-update otomatis. Sekarang di terminal kiri yang udah kosong, gue bakal jalanin unit test otomatis yang bakal dibahas sama rekan gue Reza."

---

### BAGIAN 4: CONCURRENCY, PYTEST 22 KASUS, & ANALISIS KINERJA (03:05 – 04:15)
**Pembicara**: **Reza**  
**Aksi Fathir di Terminal**: Menjalankan Pytest di Terminal Kiri, lalu membuka gambar grafik benchmark.

#### 💻 AKSI TERMINAL FATHIR #2:
> **Di Terminal Kiri (yang tadi bekas Alice keluar)**, ketik perintah ini lalu tekan **Enter**:
```powershell
pytest -v
```
*(Proses running sekitar 4 detik, dan muncul 22 baris hijau: `22 passed in 4.xx s`).*

#### 🎙️ Dialog Reza:
> "Terima kasih Fathir. Untuk menjamin kehandalan sistem dan membuktikan bahwa concurrency ditangani tanpa race condition, kami membuat 22 pengujian otomatis dengan framework Pytest.  
> Pengujian ini menguji validasi registrasi thread simultan, deduplikasi request_id, retry backoff, hingga kebijakan queue drop-oldest saat client lambat.  
> Seperti yang tampil di terminal kiri, seluruh **22 kasus uji otomatis lulus 100%**!"

#### 💻 AKSI FATHIR #3:
> Fathir membuka gambar grafik benchmark:  
> Double click atau buka file `benchmarks/results/latency_throughput_chart.png` sehingga muncul di layar.

#### 🎙️ Dialog Reza (Analisis Grafik):
> "Sesuai ketentuan poin 5 pada panduan tugas proyek mini, kami menguji performa sistem pada skenario 1, 5, dan 20 client bersamaan dengan 50 pesan per client:  
> 1. **Throughput (grafik kiri)**: Terlihat throughput melonjak dari **681 requests per detik** pada 1 client, naik menjadi **909 requests per detik** pada 5 client, dan mencapai puncaknya di **988 requests per detik** pada 20 client. Ini menunjukkan pemrosesan multi-threading server gRPC bekerja sangat efektif.  
> 2. **Latensi Rata-rata (grafik kanan)**: Pada 1 client, latensi hanya **1.09 milidetik**. Pada 5 client naik ke **5.10 milidetik**, dan pada 20 client berada di **19.07 milidetik**. Kenaikan latensi ini wajar karena thread pool server kami atur 10 worker, sehingga pada 20 client terjadi antrean eksekusi tanpa ada data yang korup."

---

### BAGIAN 5: KESIMPULAN & PENUTUP (04:15 – 04:35)
**Pembicara**: **Fathir**  
**Aksi Fathir**: Kembali ke tampilan layar terminal atau repositori GitHub.

#### 🎙️ Dialog Fathir:
> "Sebagai kesimpulan, implementasi sistem Distributed Chat Room ini telah berhasil memenuhi seluruh aspek rubrik penilaian praktikum:  
> 1. Desain antarmuka proto 4 RPC termasuk streaming dua arah,  
> 2. Fungsionalitas penuh chat real-time,  
> 3. Concurrency bebas race condition dengan ThreadPool dan Lock,  
> 4. Toleransi kegagalan dengan exponential backoff dan deduplikasi at-most-once, serta  
> 5. Analisis kinerja empiris dengan grafik dan 22 unit test otomatis.  
>  
> Seluruh kode sumber dan laporan lengkap sudah kami simpan di repositori Git kelompok kami.  
> Sekian demonstrasi dari kami bertiga—Fathir, Ajib, dan Reza. Terima kasih atas perhatiannya, dan wassalamu'alaikum warahmatullahi wabarakatuh!"

---

## ⚡ REKAP PERINTAH TERMINAL FATHIR (CHEAT SHEET)

| No | Waktu | Jendela Terminal | Perintah Persis yang Diketik Fathir |
|:---:|:---:|---|---|
| **1** | 00:30 | **Terminal Kiri** | `Start-Process python -ArgumentList "src/chat_room/server.py --port 50051" -WindowStyle Hidden` |
| **2** | 01:30 | **Terminal Kiri** | `python src/chat_room/client.py --username Alice` |
| **3** | 01:40 | **Terminal Kanan** | `python src/chat_room/client.py --username Bob` |
| **4** | 01:55 | **Terminal Kiri (Alice)** | `Halo Bob! Selamat datang di gRPC Chat Room.` |
| **5** | 02:05 | **Terminal Kanan (Bob)** | `Halo Alice! Pesan lu langsung masuk nih secara real-time.` |
| **6** | 02:20 | **Terminal Kanan (Bob)** | `/users` |
| **7** | 02:35 | **Terminal Kanan (Bob)** | `/unary Ini pesan via jalur Unary RPC dengan proteksi request ID` |
| **8** | 02:50 | **Terminal Kiri (Alice)** | `/exit` |
| **9** | 03:00 | **Terminal Kanan (Bob)** | `/users` |
| **10** | 03:08 | **Terminal Kiri** | `pytest -v` |
| **11** | 03:30 | **Layar Utama** | Buka `benchmarks/results/latency_throughput_chart.png` |
