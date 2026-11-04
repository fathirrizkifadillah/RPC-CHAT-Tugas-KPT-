"""Script to generate a formatted Word Document for SKRIP_DEMO_VIDEO.docx."""

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_document():
    doc = docx.Document()
    
    # Page setup (A4, 0.8 inch margins)
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Normal style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("SKRIP DEMONSTRASI VIDEO TUGAS PROYEK MINI RPC\nDISTRIBUTED CHAT ROOM (gRPC & PYTHON)")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(15)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("Mata Kuliah: Komputasi Paralel dan Terdistribusi | Durasi Target: 04:30 (Maks. 5 Menit)")
    run_sub.font.size = Pt(10)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    
    # Metadata Table
    table_meta = doc.add_table(rows=4, cols=2)
    table_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Ketua & Operator Host", "Fathir (Memegang kendali laptop, ngetik perintah di 2 terminal, pembuka & penutup)"),
        ("Anggota Kelompok", "Ajib (Penjelasan arsitektur IDL .proto, 4 RPC, dan efisiensi biner HTTP/2)"),
        ("Anggota Kelompok", "Reza (Penjelasan Concurrency, 22 Pytest pass 100%, dan grafik benchmark kinerja)"),
        ("Konfigurasi Layar", "2 Jendela PowerShell Side-by-Side (Terminal Kiri & Terminal Kanan, venv aktif)")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        c0 = table_meta.cell(row_idx, 0)
        c1 = table_meta.cell(row_idx, 1)
        c0.width = Inches(2.0)
        c1.width = Inches(4.6)
        c0.text = k
        c1.text = v
        c0.paragraphs[0].runs[0].font.bold = True
        set_cell_background(c0, "F0F4F8")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        
    doc.add_paragraph()
    
    # Cheatsheet Table
    h_cs = doc.add_heading("⚡ Cheatsheet Perintah Terminal Fathir (Urutan Eksekusi)", level=1)
    h_cs.style.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    table_cs = doc.add_table(rows=12, cols=4)
    table_cs.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["No", "Waktu", "Jendela Terminal", "Perintah Persis yang Diketik Fathir"]
    for i, title in enumerate(headers):
        cell = table_cs.cell(0, i)
        cell.text = title
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 100, 100)

    cs_data = [
        ("1", "00:30", "Terminal Kiri", 'Start-Process python -ArgumentList "src/chat_room/server.py --port 50051" -WindowStyle Hidden'),
        ("2", "01:30", "Terminal Kiri", "python src/chat_room/client.py --username Alice"),
        ("3", "01:40", "Terminal Kanan", "python src/chat_room/client.py --username Bob"),
        ("4", "01:55", "Terminal Kiri (Alice)", "Halo Bob! Selamat datang di gRPC Chat Room."),
        ("5", "02:05", "Terminal Kanan (Bob)", "Halo Alice! Pesan lu langsung masuk nih secara real-time."),
        ("6", "02:20", "Terminal Kanan (Bob)", "/users"),
        ("7", "02:35", "Terminal Kanan (Bob)", "/unary Ini pesan via jalur Unary RPC dengan proteksi request ID"),
        ("8", "02:50", "Terminal Kiri (Alice)", "/exit"),
        ("9", "03:00", "Terminal Kanan (Bob)", "/users"),
        ("10", "03:08", "Terminal Kiri", "pytest -v"),
        ("11", "03:30", "Layar Utama", "Buka file gambar: benchmarks/results/latency_throughput_chart.png")
    ]
    for r_idx, row in enumerate(cs_data, start=1):
        for c_idx, val in enumerate(row):
            cell = table_cs.cell(r_idx, c_idx)
            cell.text = val
            set_cell_margins(cell, 50, 50, 80, 80)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F9FBFD")
            if c_idx == 3:
                cell.paragraphs[0].runs[0].font.name = 'Consolas'
                cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_page_break()

    # Section 1
    h_naskah = doc.add_heading("Naskah Lengkap Kata-Demi-Kata & Aksi Terminal Fathir", level=1)
    h_naskah.style.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    # Helper function for dialog block
    def add_dialog_block(title, timecode, speaker, dialog, terminal_action=None):
        p_t = doc.add_paragraph()
        r_t = p_t.add_run(f"• {title}")
        r_t.font.name = 'Arial'; r_t.font.size = Pt(12); r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        
        p_info = doc.add_paragraph()
        p_info.add_run(f"⏱️ Waktu: {timecode} | 🎙️ Pembicara: {speaker}").bold = True
        
        p_d = doc.add_paragraph()
        p_d.paragraph_format.left_indent = Inches(0.2)
        r_d = p_d.add_run(f'"{dialog}"')
        r_d.font.italic = True
        
        if terminal_action:
            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            c = tbl.cell(0, 0)
            c.width = Inches(6.6)
            c.text = f"💻 {terminal_action['label']}\n{terminal_action['cmd']}"
            c.paragraphs[0].runs[0].font.bold = True
            c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x06, 0x5F, 0x46)
            set_cell_background(c, "ECFDF5")
            set_cell_margins(c, 60, 60, 100, 100)
            doc.add_paragraph()

    # Bagian 1
    add_dialog_block(
        "BAGIAN 1: PEMBUKAAN & MENJALANKAN SERVER",
        "00:00 – 00:45",
        "Fathir (Ketua)",
        "Halo semuanya! Selamat datang di video demonstrasi Tugas Proyek Mini Komputasi Paralel dan Terdistribusi. Kami dari kelompok yang beranggotakan:\n"
        "- Saya sendiri, Fathir selaku Ketua,\n"
        "- Rekan saya Ajib, dan\n"
        "- Rekan saya Reza.\n\n"
        "Pada tugas proyek mini ini, kami mengimplementasikan Studi Kasus Nomor 3, yaitu membangun sistem Distributed Chat Room Real-Time berbasis gRPC dan Protocol Buffers menggunakan Python.\n\n"
        "Di layar ini gue udah siapin dua jendela terminal berdampingan untuk mensimulasikan dua client terdistribusi. Pertama-tama, gue bakal jalanin server gRPC-nya terlebih dahulu di background lewat terminal kiri.\n\n"
        "Oke, server udah aktif di background pada port 50051. Sekarang rekan saya Ajib bakal jelasin kontrak antarmuka dan arsitektur RPC-nya terlebih dahulu.",
        {"label": "AKSI TERMINAL KIRI FATHIR (Ketik lalu tekan Enter):",
         "cmd": 'Start-Process python -ArgumentList "src/chat_room/server.py --port 50051" -WindowStyle Hidden'}
    )

    # Bagian 2
    add_dialog_block(
        "BAGIAN 2: PENJELASAN KONTRAK IDL & ARSITEKTUR RPC",
        "00:45 – 01:25",
        "Ajib",
        "Terima kasih Fathir. Sesuai ketentuan umum di panduan praktikum, antarmuka layanan wajib didefinisikan dalam file .proto dengan minimal 4 RPC. Pada file chat_room.proto, kami merancang 4 RPC lengkap:\n"
        "1. rpc Join: Unary RPC untuk registrasi sesi pengguna baru.\n"
        "2. rpc ListUsers: Unary RPC untuk mengambil daftar pengguna yang sedang aktif di memori server.\n"
        "3. rpc SendMessage: Unary RPC untuk pengiriman pesan dengan proteksi idempotensi request_id.\n"
        "4. rpc Chat: Bidirectional Streaming RPC untuk pertukaran pesan dua arah secara real-time melalui transport HTTP/2.\n\n"
        "Dengan Protocol Buffers dan HTTP/2, pesan diserialisasi menjadi format biner yang sangat ringkas dan efisien dibandingkan XML-RPC.\n"
        "Sekarang, Fathir bakal langsung mendemokan interaksi obrolan antar-client di kedua terminal."
    )

    # Bagian 3
    doc.add_page_break()
    p_sec3 = doc.add_paragraph()
    r_sec3 = p_sec3.add_run("• BAGIAN 3: DEMO LIVE INTERAKSI CHAT DI 2 TERMINAL")
    r_sec3.font.name = 'Arial'; r_sec3.font.size = Pt(13); r_sec3.font.bold = True
    r_sec3.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
    
    p_info3 = doc.add_paragraph()
    p_info3.add_run("⏱️ Waktu: 01:25 – 03:05 | 🎙️ Pembicara & Operator Terminal: Fathir").bold = True

    demo_steps = [
        ("Langkah 1: Hubungkan Alice di Terminal Kiri",
         "Sekarang di terminal sebelah kiri, gue bakal sambungin client pertama dengan username Alice.",
         "TERMINAL KIRI (Ketik & Enter):",
         "python src/chat_room/client.py --username Alice"),

        ("Langkah 2: Hubungkan Bob di Terminal Kanan",
         "Lanjut ke terminal sebelah kanan, gue sambungin client kedua dengan username Bob.\n\n"
         "Bisa kita lihat, begitu Bob join, di terminal Alice langsung muncul notifikasi real-time bahwa Bob sudah aktif di room tanpa perlu Alice melakukan polling.",
         "TERMINAL KANAN (Ketik & Enter):",
         "python src/chat_room/client.py --username Bob"),

        ("Langkah 3: Tes Kirim Chat Real-Time Dua Arah",
         "Sekarang kita uji pertukaran pesan real-time lewat bidirectional streaming. Di terminal kiri, Alice bakal kirim pesan ke Bob.\n\n"
         "Pesan dari Alice langsung masuk ke layar Bob secara instan! Sekarang Bob bales dari terminal kanan.",
         "TERMINAL KIRI (Alice ketik): Halo Bob! Selamat datang di gRPC Chat Room.\nTERMINAL KANAN (Bob balas): Halo Alice! Pesan lu langsung masuk nih secara real-time.",
         ""),

        ("Langkah 4: Uji Fitur Unary RPC /users (List Users)",
         "Sekarang gue bakal uji fitur Unary RPC ListUsers pakai command /users di terminal Bob buat ngeliat siapa aja yang lagi online di memori server.\n\n"
         "Server langsung ngebalikin tabel daftar pengguna aktif yang tersimpan aman di shared memory server.",
         "TERMINAL KANAN (Bob ketik):",
         "/users"),

        ("Langkah 5: Uji Unary RPC /unary (SendMessage + Request ID Deduplication)",
         "Selanjutnya, kita uji pengiriman pesan lewat jalur Unary RPC SendMessage dengan command /unary. Di sini client menyertakan UUID request_id unik untuk menjamin semantik at-most-once.\n\n"
         "Dengan adanya request_id dan tabel deduplikasi PROSES di server, jika jaringan sempat putus dan client melakukan retry otomatis, pesan dipastikan tidak akan pernah terkirim ganda.",
         "TERMINAL KANAN (Bob ketik):",
         "/unary Ini pesan via jalur Unary RPC dengan proteksi request ID"),

        ("Langkah 6: Uji Disconnect Handling & Toleransi Kegagalan",
         "Sekarang kita uji penanganan client terputus atau graceful disconnect. Di terminal kiri, Alice bakal keluar pakai command /exit.\n\n"
         "Alice keluar secara tertib, dan server langsung membroadcast event keluar ke Bob. Sekarang kita cek lagi daftar user di terminal Bob pakai /users, status Alice langsung berubah Offline.\n\n"
         "Sekarang di terminal kiri yang udah kosong, gue bakal jalanin unit test otomatis yang bakal dibahas sama rekan gue Reza.",
         "TERMINAL KIRI (Alice ketik): /exit\nTERMINAL KANAN (Bob ketik): /users",
         "")
    ]

    for title, dial, cmd_lbl, cmd_str in demo_steps:
        p_st = doc.add_paragraph()
        p_st.add_run(f"👉 {title}").bold = True
        
        p_sd = doc.add_paragraph()
        p_sd.paragraph_format.left_indent = Inches(0.2)
        r_sd = p_sd.add_run(f'"{dial}"')
        r_sd.font.italic = True
        
        tbl_s = doc.add_table(rows=1, cols=1)
        tbl_s.alignment = WD_TABLE_ALIGNMENT.CENTER
        cs = tbl_s.cell(0, 0)
        cs.width = Inches(6.6)
        cs.text = f"💻 {cmd_lbl}\n{cmd_str}" if cmd_str else f"💻 {cmd_lbl}"
        cs.paragraphs[0].runs[0].font.bold = True
        cs.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x06, 0x5F, 0x46)
        set_cell_background(cs, "ECFDF5")
        set_cell_margins(cs, 50, 50, 80, 80)
        doc.add_paragraph()

    # Bagian 4
    doc.add_page_break()
    add_dialog_block(
        "BAGIAN 4: CONCURRENCY, PYTEST 22 KASUS, & ANALISIS KINERJA",
        "03:05 – 04:15",
        "Reza (Operator Terminal: Fathir)",
        "Terima kasih Fathir. Untuk menjamin kehandalan sistem dan membuktikan bahwa concurrency ditangani tanpa race condition, kami membuat 22 pengujian otomatis dengan framework Pytest.\n"
        "Pengujian ini menguji validasi registrasi thread simultan, deduplikasi request_id, retry backoff, hingga kebijakan queue drop-oldest saat client lambat.\n"
        "Seperti yang tampil di terminal kiri, seluruh 22 kasus uji otomatis lulus 100%!\n\n"
        "Sesuai ketentuan poin 5 pada panduan tugas proyek mini, kami menguji performa sistem pada skenario 1, 5, dan 20 client bersamaan dengan 50 pesan per client:\n"
        "1. Throughput (grafik kiri): Terlihat throughput melonjak dari 681 requests per detik pada 1 client, naik menjadi 909 requests per detik pada 5 client, dan mencapai puncaknya di 988 requests per detik pada 20 client. Ini menunjukkan pemrosesan multi-threading server gRPC bekerja sangat efektif.\n"
        "2. Latensi Rata-rata (grafik kanan): Pada 1 client, latensi hanya 1.09 milidetik. Pada 5 client naik ke 5.10 milidetik, dan pada 20 client berada di 19.07 milidetik. Kenaikan latensi ini wajar karena thread pool server kami atur 10 worker, sehingga pada 20 client terjadi antrean eksekusi tanpa ada data yang korup.",
        {"label": "AKSI FATHIR: Di Terminal Kiri ketik 'pytest -v', lalu buka file grafik benchmarks/results/latency_throughput_chart.png",
         "cmd": "pytest -v"}
    )

    # Bagian 5
    add_dialog_block(
        "BAGIAN 5: KESIMPULAN & PENUTUP",
        "04:15 – 04:35",
        "Fathir (Ketua)",
        "Sebagai kesimpulan, implementasi sistem Distributed Chat Room ini telah berhasil memenuhi seluruh aspek rubrik penilaian praktikum:\n"
        "1. Desain antarmuka proto 4 RPC termasuk streaming dua arah,\n"
        "2. Fungsionalitas penuh chat real-time,\n"
        "3. Concurrency bebas race condition dengan ThreadPool dan Lock,\n"
        "4. Toleransi kegagalan dengan exponential backoff dan deduplikasi at-most-once, serta\n"
        "5. Analisis kinerja empiris dengan grafik dan 22 unit test otomatis.\n\n"
        "Seluruh kode sumber dan laporan lengkap sudah kami simpan di repositori Git kelompok kami.\n"
        "Sekian demonstrasi dari kami bertiga—Fathir, Ajib, dan Reza. Terima kasih atas perhatiannya, dan wassalamu'alaikum warahmatullahi wabarakatuh!"
    )

    out_root = Path("SKRIP_DEMO_VIDEO.docx")
    try:
        doc.save(out_root)
        print(f"Saved: {out_root}")
    except Exception as e:
        alt_root = Path("SKRIP_DEMO_VIDEO_LATEST.docx")
        doc.save(alt_root)
        print(f"File locked, saved to {alt_root}: {e}")

    out_docs = Path("docs/SKRIP_DEMO_VIDEO.docx")
    try:
        doc.save(out_docs)
        print(f"Saved: {out_docs}")
    except Exception as e:
        alt_docs = Path("docs/SKRIP_DEMO_VIDEO_LATEST.docx")
        doc.save(alt_docs)
        print(f"File locked, saved to {alt_docs}: {e}")

if __name__ == "__main__":
    create_document()
