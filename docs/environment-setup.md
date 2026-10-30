# Dokumentasi Pengaturan Lingkungan (Environment Setup Guide)

Dokumen ini mencatat seluruh proses konfigurasi, verifikasi, dan manajemen dependensi lingkungan pengembangan proyek **Distributed Chat Room gRPC** sesuai dengan standar akademik dan pedoman modul praktikum.

---

## 1. Interpreter Python yang Dipilih

- **Versi Python**: `Python 3.11.9`
- **Executable Asal**: `C:\Users\FATHIR\AppData\Local\Programs\Python\Python311\python.exe`
- **Arsitektur**: Windows x86_64 (64-bit)

### Alasan Pemilihan Versi
1. **Kepatuhan Terhadap Modul**: Modul praktikum mensyaratkan Python versi minimal `3.10 ke atas`. Python 3.11.9 memenuhi persyaratan ini dengan kompatibilitas penuh.
2. **Performa dan Concurrency**: Python 3.11 membawa peningkatan performa runtime (Faster CPython) sekitar 10–25% lebih cepat dibandingkan Python 3.10, yang menguntungkan penanganan thread worker dan serialisasi Protobuf pada benchmark concurrency.
3. **Stabilitas Ekosistem gRPC**: Pustaka `grpcio` dan `grpcio-tools` versi 1.60+ menyediakan pre-built wheels resmi yang stabil dan teruji untuk Python 3.11 di platform Windows dan Linux x86_64.

---

## 2. Pembuatan dan Aktivasi Virtual Environment (`venv`)

Virtual environment dibuat secara lokal pada direktori root proyek untuk mengisolasi seluruh dependensi dari sistem operasi global:

```powershell
# Berada di root direktori proyek (C:\TUGAS\KPT\RPC_CHAT)
python -m venv venv
```

### Cara Aktivasi Environment

- **Windows PowerShell**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *Catatan: Jika terdapat ExecutionPolicy restriction di PowerShell, eksekusi command dapat langsung menggunakan executable interpreter di dalam venv:*
  ```powershell
  .\venv\Scripts\python.exe <perintah>
  ```

- **Windows Command Prompt (cmd.exe)**:
  ```cmd
  venv\Scripts\activate.bat
  ```

- **Linux / macOS / Container**:
  ```bash
  source venv/bin/activate
  ```

---

## 3. Bukti Verifikasi Virtual Environment

Pemeriksaan binding interpreter:
```powershell
.\venv\Scripts\python.exe -c "import sys; print('Executable:', sys.executable); print('Prefix:', sys.prefix); print('Base Prefix:', sys.base_prefix)"
```

**Hasil Verifikasi Aktual**:
- `sys.executable`: `C:\TUGAS\KPT\RPC_CHAT\venv\Scripts\python.exe`
- `sys.prefix`: `C:\TUGAS\KPT\RPC_CHAT\venv` (menunjuk tepat ke environment virtual)
- `sys.base_prefix`: `C:\Users\FATHIR\AppData\Local\Programs\Python\Python311` (interpreter sistem induk)

Status Virtual Environment: **VERIFIED**

---

## 4. Dependensi Proyek

File `requirements.txt`:
```text
grpcio>=1.60.0
grpcio-tools>=1.60.0
protobuf>=4.25.0
pytest>=8.0.0
tabulate>=0.9.0
matplotlib>=3.8.0
```

### Perintah Instalasi Dependensi:
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Verifikasi Import Dependensi Inti:
```powershell
.\venv\Scripts\python.exe -m pip check
.\venv\Scripts\python.exe -c "import grpc, google.protobuf, pytest, tabulate, matplotlib; print('Semua dependensi berhasil diimpor')"
```

---

## 5. Alur Operasional Pengembangan (Workflow)

Seluruh operasi berikut wajib dieksekusi menggunakan interpreter virtual environment:

1. **Kompilasi Protocol Buffers (Generate Stubs)**:
   ```powershell
   .\venv\Scripts\python.exe -m grpc_tools.protoc -I. --python_out=src --grpc_python_out=src proto/chat_room.proto
   ```
2. **Menjalankan Server Chat gRPC**:
   ```powershell
   .\venv\Scripts\python.exe src/chat_room/server.py --port 50051 --workers 10
   ```
3. **Menjalankan Client Terminal CLI**:
   ```powershell
   .\venv\Scripts\python.exe src/chat_room/client.py --server localhost:50051 --username Alice
   ```
4. **Menjalankan Pengujian Otomatis (Pytest)**:
   ```powershell
   .\venv\Scripts\python.exe -m pytest -v
   ```
5. **Menjalankan Benchmark Kinerja**:
   ```powershell
   .\venv\Scripts\python.exe benchmarks/run_benchmark.py --clients 1,5,20 --messages 50
   ```
