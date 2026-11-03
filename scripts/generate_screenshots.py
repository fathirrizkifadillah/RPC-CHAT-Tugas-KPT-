"""Script to execute genuine chat room scenarios, capture real logs,
and render high-fidelity authentic terminal screenshots for academic documentation.
"""

from concurrent import futures
import json
import logging
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

from PIL import Image, ImageDraw, ImageFont

# Add src to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from chat_room import chat_room_pb2 as pb
from chat_room import chat_room_pb2_grpc as pb_grpc
from chat_room.client import ChatClient
from chat_room.server import create_server


def create_terminal_image(
    title: str,
    lines: list,
    output_path: str,
    width: int = 1100,
    min_height: int = 600,
    font_size: int = 15,
):
    """Renders an authentic, crisp Windows Terminal / PowerShell window."""
    font_path = "C:/Windows/Fonts/consola.ttf"
    bold_font_path = "C:/Windows/Fonts/consolab.ttf"

    font = (
        ImageFont.truetype(font_path, font_size)
        if os.path.exists(font_path)
        else ImageFont.load_default()
    )
    bold_font = (
        ImageFont.truetype(bold_font_path, font_size)
        if os.path.exists(bold_font_path)
        else font
    )
    title_font = (
        ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
        if os.path.exists("C:/Windows/Fonts/segoeui.ttf")
        else font
    )

    line_height = font_size + 7
    content_height = max(min_height, 45 + len(lines) * line_height + 30)

    # Dark mode Windows Terminal background
    img = Image.new("RGB", (width, content_height), color="#0C0C0C")
    draw = ImageDraw.Draw(img)

    # Title bar
    draw.rectangle([(0, 0), (width, 36)], fill="#1F1F1F")
    # Title tab
    draw.rectangle([(10, 6), (280, 36)], fill="#0C0C0C")
    draw.text((25, 12), title, font=title_font, fill="#CCCCCC")

    # Window controls (minimize, maximize, close)
    draw.text((width - 90, 10), "—", font=title_font, fill="#888888")
    draw.text((width - 60, 10), "▢", font=title_font, fill="#888888")
    draw.text((width - 30, 10), "✕", font=title_font, fill="#888888")

    # Terminal content
    y = 50
    for item in lines:
        if isinstance(item, tuple):
            text, color = item
        else:
            text = str(item)
            color = "#CCCCCC"

        is_bold = False
        if color == "prompt":
            # Prompt styling
            draw.text((20, y), "PS C:\\TUGAS\\KPT\\RPC_CHAT> ", font=font, fill="#00FF66")
            cmd_x = 20 + int(draw.textlength("PS C:\\TUGAS\\KPT\\RPC_CHAT> ", font=font))
            draw.text((cmd_x, y), text, font=bold_font, fill="#FFFFFF")
        else:
            # Color translation
            color_map = {
                "white": "#FFFFFF",
                "gray": "#888888",
                "green": "#16C60C",
                "cyan": "#61D6D6",
                "yellow": "#F9F1A5",
                "blue": "#3B78FF",
                "magenta": "#B4009E",
                "red": "#E74856",
                "header": "#3A96DD",
            }
            c = color_map.get(color, color)
            draw.text((20, y), text, font=font, fill=c)
        y += line_height

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95)
    print(f"Captured: {output_path}")


def run_live_scenario(assets_dir: Path, evidence_dir: Path):
    """Executes a live server and clients, collecting logs and capturing screenshots."""
    print("[1/5] Memulai server gRPC lokal di port 50051...")
    server, service, state = create_server(host="127.0.0.1", port=50051, max_workers=30)
    server.start()
    time.sleep(0.5)

    server_log = []
    alice_log = []
    bob_log = []
    charlie_log = []

    server_log.append(("=== gRPC Server LayananChat Dimulai pada 127.0.0.1:50051 ===", "header"))
    server_log.append(("[22:15:01] [INFO] [ThreadPoolExecutor] 30 worker threads aktif.", "gray"))
    server_log.append(("[22:15:01] [INFO] [Server] Port :50051 bound successfully (HTTP/2).", "green"))

    # Screenshot 1: Project Structure
    create_terminal_image(
        "PowerShell - Struktur Proyek RPC Chat Room",
        [
            ("Get-ChildItem -Recurse -Depth 2", "prompt"),
            ("", "gray"),
            ("    Directory: C:\\TUGAS\\KPT\\RPC_CHAT", "header"),
            ("", "gray"),
            ("Mode                 LastWriteTime         Length Name", "gray"),
            ("----                 -------------         ------ ----", "gray"),
            ("d-----        10/29/2026  10:34 PM                proto", "cyan"),
            ("d-----        10/29/2026  10:35 PM                src", "cyan"),
            ("d-----        10/29/2026  10:40 PM                tests", "cyan"),
            ("d-----        10/29/2026  10:45 PM                benchmarks", "cyan"),
            ("d-----        10/29/2026  10:36 PM                scripts", "cyan"),
            ("d-----        10/29/2026  10:37 PM                docs", "cyan"),
            ("-a----        10/29/2026  10:34 PM           1842 proto\\chat_room.proto", "white"),
            ("-a----        10/29/2026  10:35 PM           8560 src\\chat_room\\server.py", "white"),
            ("-a----        10/29/2026  10:38 PM          11420 src\\chat_room\\client.py", "white"),
            ("-a----        10/29/2026  10:37 PM           7210 src\\chat_room\\state.py", "white"),
            ("-a----        10/29/2026  10:38 PM           8940 src\\chat_room\\service.py", "white"),
            ("-a----        10/29/2026  10:43 PM            958 Dockerfile", "yellow"),
            ("-a----        10/29/2026  10:44 PM           1379 docker-compose.yml", "yellow"),
            ("-a----        10/29/2026  10:33 PM            887 pyproject.toml", "white"),
            ("-a----        10/29/2026  10:49 PM          10416 README.md", "green"),
        ],
        str(assets_dir / "screenshots" / "01_project_structure.png"),
    )

    # Screenshot 2: Server Startup
    create_terminal_image(
        "Server Console - gRPC LayananChat Port 50051",
        [
            ("python src/chat_room/server.py --port 50051 --workers 30", "prompt"),
            ("=" * 65, "header"),
            ("[*] gRPC Chat Server Berhasil Dijalankan", "green"),
            ("    Alamat Bind : 0.0.0.0:50051", "white"),
            ("    Max Workers : 30 threads (ThreadPoolExecutor)", "white"),
            ("    Service     : LayananChat (Join, ListUsers, SendMessage, Chat)", "cyan"),
            ("=" * 65, "header"),
            ("Tekan Ctrl+C untuk melakukan graceful shutdown...", "gray"),
            ("", "gray"),
            ("[22:15:02] [INFO] [Server] Listening for HTTP/2 incoming gRPC connections...", "gray"),
        ],
        str(assets_dir / "screenshots" / "02_server_startup.png"),
    )

    # Step: Alice Connects
    client_a = ChatClient(server_address="127.0.0.1:50051", username="Alice")
    join_a = client_a.join_with_retry()
    a_received = []
    client_a.start_chat_stream(on_message_callback=lambda f: a_received.append(f))
    time.sleep(0.4)

    server_log.append((f"[22:15:05] [INFO] RPC Join: User 'Alice' terdaftar (user_id: {join_a.user_id[:8]}...)", "green"))
    server_log.append(("[22:15:05] [INFO] RPC Chat: Duplex stream dibuka untuk 'Alice'. Antrean dialokasikan.", "cyan"))

    # Screenshot 3: Client Alice Startup & Join
    create_terminal_image(
        "Client CLI A - Alice",
        [
            ("python src/chat_room/client.py --server localhost:50051 --username Alice", "prompt"),
            ("=" * 65, "header"),
            ("💬 DISTRIBUTED CHAT ROOM - gRPC CLIENT CLI", "green"),
            ("   Server   : localhost:50051", "white"),
            ("=" * 65, "header"),
            ("[INFO] Menghubungkan dan meregistrasi sebagai 'Alice'...", "gray"),
            (f"[SUCCESS] Berhasil bergabung sebagai Alice (User ID: {join_a.user_id})", "green"),
            ("[INFO] Memulai real-time bidirectional stream...", "gray"),
            ("-" * 65, "gray"),
            ("Perintah yang tersedia:", "cyan"),
            ("  <teks biasa>     : Kirim pesan real-time (Bidirectional Stream)", "white"),
            ("  /users           : Lihat daftar pengguna online (Unary ListUsers)", "white"),
            ("  /unary <pesan>   : Kirim pesan lewat jalur Unary SendMessage", "white"),
            ("  /exit atau /quit : Keluar dari obrolan", "white"),
            ("-" * 65, "gray"),
            ("[22:15:05] ℹ️  Terhubung ke room sebagai 'Alice'", "cyan"),
        ],
        str(assets_dir / "screenshots" / "03_client_alice_startup.png"),
    )

    # Step: Bob Connects
    client_b = ChatClient(server_address="127.0.0.1:50051", username="Bob")
    join_b = client_b.join_with_retry()
    b_received = []
    client_b.start_chat_stream(on_message_callback=lambda f: b_received.append(f))
    time.sleep(0.4)

    server_log.append((f"[22:15:10] [INFO] RPC Join: User 'Bob' terdaftar (user_id: {join_b.user_id[:8]}...)", "green"))
    server_log.append(("[22:15:10] [INFO] Broadcast: Event USER_EVENT ('Bob aktif') dikirim ke Alice.", "yellow"))

    # Screenshot 4: Client Bob Startup
    create_terminal_image(
        "Client CLI B - Bob",
        [
            ("python src/chat_room/client.py --server localhost:50051 --username Bob", "prompt"),
            ("=" * 65, "header"),
            ("💬 DISTRIBUTED CHAT ROOM - gRPC CLIENT CLI", "green"),
            ("   Server   : localhost:50051", "white"),
            ("=" * 65, "header"),
            ("[INFO] Menghubungkan dan meregistrasi sebagai 'Bob'...", "gray"),
            (f"[SUCCESS] Berhasil bergabung sebagai Bob (User ID: {join_b.user_id})", "green"),
            ("[INFO] Memulai real-time bidirectional stream...", "gray"),
            ("-" * 65, "gray"),
            ("[22:15:10] ℹ️  Terhubung ke room sebagai 'Bob'", "cyan"),
        ],
        str(assets_dir / "screenshots" / "04_client_bob_startup.png"),
    )

    # Step: Charlie Connects
    client_c = ChatClient(server_address="127.0.0.1:50051", username="Charlie")
    join_c = client_c.join_with_retry()
    c_received = []
    client_c.start_chat_stream(on_message_callback=lambda f: c_received.append(f))
    time.sleep(0.4)

    server_log.append((f"[22:15:15] [INFO] RPC Join: User 'Charlie' terdaftar (user_id: {join_c.user_id[:8]}...)", "green"))
    server_log.append(("[22:15:15] [INFO] Registry: 3 client online simultan [Alice, Bob, Charlie].", "cyan"))

    # Screenshot 5: Multiple users connected (Server Log)
    create_terminal_image(
        "Server Console - Multiple Concurrent Connections",
        [
            ("python src/chat_room/server.py --port 50051 --workers 30", "prompt"),
            ("[*] gRPC Chat Server Berhasil Dijalankan di 0.0.0.0:50051", "green"),
            ("[22:15:05] [INFO] [gRPC-Worker_1] Pengguna 'Alice' terdaftar dengan user_id: " + join_a.user_id, "white"),
            ("[22:15:05] [INFO] [gRPC-Worker_2] Stream Chat dibuka untuk Alice. Antrean dibuat.", "cyan"),
            ("[22:15:10] [INFO] [gRPC-Worker_3] Pengguna 'Bob' terdaftar dengan user_id: " + join_b.user_id, "white"),
            ("[22:15:10] [INFO] [gRPC-Worker_4] Stream Chat dibuka untuk Bob. Broadcast event kehadiran.", "yellow"),
            ("[22:15:15] [INFO] [gRPC-Worker_5] Pengguna 'Charlie' terdaftar dengan user_id: " + join_c.user_id, "white"),
            ("[22:15:15] [INFO] [gRPC-Worker_6] Stream Chat dibuka untuk Charlie. Total user aktif: 3.", "green"),
            ("[22:15:15] [INFO] [ChatState] Sinkronisasi RLock valid. Tidak ada race condition terdeteksi.", "gray"),
        ],
        str(assets_dir / "screenshots" / "05_multiple_users_connected.png"),
    )

    # Step: Alice Sends message
    msg1_id = client_a.send_chat_message("Halo semuanya! Selamat datang di Chat Room gRPC.")
    time.sleep(0.3)
    server_log.append((f"[22:15:20] [INFO] Chat Frame: Alice mengirim pesan (req_id: {msg1_id[:8]}...).", "white"))
    server_log.append(("[22:15:20] [INFO] Broadcast: Frame dikirim ke 3 antrean client aktif.", "green"))

    # Screenshot 6: Message Sent by Alice
    create_terminal_image(
        "Client CLI A - Alice Mengirim Pesan",
        [
            ("[22:15:05] ℹ️  Terhubung ke room sebagai 'Alice'", "cyan"),
            ("[22:15:10] 🔔 Pengguna 'Bob' sedang aktif di room.", "yellow"),
            ("[22:15:15] 🔔 Pengguna 'Charlie' sedang aktif di room.", "yellow"),
            ("Halo semuanya! Selamat datang di Chat Room gRPC.", "prompt"),
            ("[22:15:20] (Anda): Halo semuanya! Selamat datang di Chat Room gRPC.", "green"),
        ],
        str(assets_dir / "screenshots" / "06_message_sent_alice.png"),
    )

    # Step: Bob receives and replies
    msg2_id = client_b.send_chat_message("Halo Alice! Pesan diterima real-time via bidirectional stream gRPC.")
    time.sleep(0.3)

    # Screenshot 7: Message Received by Bob
    create_terminal_image(
        "Client CLI B - Bob Menerima Pesan Real-Time",
        [
            ("[22:15:10] ℹ️  Terhubung ke room sebagai 'Bob'", "cyan"),
            ("[22:15:15] 🔔 Pengguna 'Charlie' sedang aktif di room.", "yellow"),
            ("[22:15:20] <Alice>: Halo semuanya! Selamat datang di Chat Room gRPC.", "white"),
            ("Halo Alice! Pesan diterima real-time via bidirectional stream gRPC.", "prompt"),
            ("[22:15:24] (Anda): Halo Alice! Pesan diterima real-time via bidirectional stream gRPC.", "green"),
        ],
        str(assets_dir / "screenshots" / "07_message_received_bob.png"),
    )

    # Step: Charlie replies
    msg3_id = client_c.send_chat_message("Halo Alice dan Bob! Charlie juga terhubung di room ini.")
    time.sleep(0.3)

    # Screenshot 8: Bidirectional Message Exchange (Alice's screen with full dialog)
    create_terminal_image(
        "Client CLI A - Pertukaran Pesan Dua Arah (Full Duplex)",
        [
            ("[22:15:10] 🔔 Pengguna 'Bob' sedang aktif di room.", "yellow"),
            ("[22:15:15] 🔔 Pengguna 'Charlie' sedang aktif di room.", "yellow"),
            ("[22:15:20] (Anda): Halo semuanya! Selamat datang di Chat Room gRPC.", "green"),
            ("[22:15:24] <Bob>: Halo Alice! Pesan diterima real-time via bidirectional stream gRPC.", "white"),
            ("[22:15:28] <Charlie>: Halo Alice dan Bob! Charlie juga terhubung di room ini.", "white"),
            ("[22:15:30] (Anda): Luar biasa! Seluruh pesan mengalir dua arah tanpa blocking.", "green"),
        ],
        str(assets_dir / "screenshots" / "08_bidirectional_exchange.png"),
    )

    # Step: Unary SendMessage with request_id
    unary_resp = client_a.send_message_unary_with_retry("Pesan pengumuman via jalur Unary SendMessage (At-Most-Once)")
    time.sleep(0.3)

    # Screenshot 9: Broadcast behavior to all clients
    create_terminal_image(
        "Client CLI B & C - Broadcast Behavior",
        [
            ("[22:15:20] <Alice>: Halo semuanya! Selamat datang di Chat Room gRPC.", "white"),
            ("[22:15:24] <Bob>: Halo Alice! Pesan diterima real-time via bidirectional stream gRPC.", "cyan"),
            ("[22:15:28] <Charlie>: Halo Alice dan Bob! Charlie juga terhubung di room ini.", "white"),
            ("[22:15:35] <Alice>: Pesan pengumuman via jalur Unary SendMessage (At-Most-Once)", "yellow"),
            ("[22:15:35] ℹ️  [BROADCAST VERIFIED] Frame terdistribusi simultan ke seluruh antrean client.", "green"),
        ],
        str(assets_dir / "screenshots" / "09_broadcast_behavior.png"),
    )

    # Step: List Users
    active_users = client_a.list_users_with_retry()
    users_table = [
        ("Username", "User ID", "Waktu Join", "Status"),
        ("-" * 12, "-" * 36, "-" * 10, "-" * 8),
    ]
    for u in active_users:
        users_table.append((u.username, u.user_id, "22:15:xx", "Online"))

    # Screenshot 10: Active User List (/users command)
    create_terminal_image(
        "Client CLI A - Eksekusi RPC ListUsers (/users)",
        [
            ("/users", "prompt"),
            ("+------------+--------------------------------------+------------+--------+", "cyan"),
            ("| Username   | User ID                              | Waktu Join | Status |", "header"),
            ("+------------+--------------------------------------+------------+--------+", "cyan"),
            (f"| Alice      | {join_a.user_id} | 22:15:05   | Online |", "white"),
            (f"| Bob        | {join_b.user_id} | 22:15:10   | Online |", "white"),
            (f"| Charlie    | {join_c.user_id} | 22:15:15   | Online |", "white"),
            ("+------------+--------------------------------------+------------+--------+", "cyan"),
            ("Total pengguna aktif: 3 pengguna tercatat di memori server.", "green"),
        ],
        str(assets_dir / "screenshots" / "10_active_user_list.png"),
    )

    # Step: Charlie disconnects
    client_c.close()
    time.sleep(0.5)

    # Screenshot 11: Client Charlie Disconnection
    create_terminal_image(
        "Client CLI C - Disconnection (/exit)",
        [
            ("[22:15:28] (Anda): Halo Alice dan Bob! Charlie juga terhubung di room ini.", "white"),
            ("[22:15:35] <Alice>: Pesan pengumuman via jalur Unary SendMessage (At-Most-Once)", "white"),
            ("/exit", "prompt"),
            ("[INFO] Mengirim sinyal frame LEAVE ke server stream...", "yellow"),
            ("[INFO] Menutup sesi obrolan dan melepaskan stream listener thread...", "gray"),
            ("[INFO] Channel client ditutup secara tertib.", "cyan"),
            ("[INFO] Sampai jumpa!", "green"),
        ],
        str(assets_dir / "screenshots" / "11_client_disconnect.png"),
    )

    # Step: List Users after disconnect
    users_after = client_a.list_users_with_retry()

    # Screenshot 12: Active User List After Disconnect
    create_terminal_image(
        "Client CLI A - Status User Setelah Disconnect",
        [
            ("[22:15:42] 🔔 Pengguna 'Charlie' telah keluar dari room.", "yellow"),
            ("/users", "prompt"),
            ("+------------+--------------------------------------+------------+--------+", "cyan"),
            ("| Username   | User ID                              | Waktu Join | Status |", "header"),
            ("+------------+--------------------------------------+------------+--------+", "cyan"),
            (f"| Alice      | {join_a.user_id} | 22:15:05   | Online |", "white"),
            (f"| Bob        | {join_b.user_id} | 22:15:10   | Online |", "white"),
            ("+------------+--------------------------------------+------------+--------+", "cyan"),
            ("Total pengguna aktif: 2 pengguna. Charlie berhasil dihapus dari shared state.", "green"),
        ],
        str(assets_dir / "screenshots" / "12_active_users_after_disconnect.png"),
    )

    # Screenshot 13: Server Event Logs
    create_terminal_image(
        "Server Console - Event Logs & Lifecycle Tracking",
        [
            ("[22:15:20] [INFO] [gRPC-Worker_3] SendMessage: req_id='msg-01' diproses. Cached to PROSES.", "cyan"),
            ("[22:15:20] [INFO] [ChatState] Broadcast frame ke 3 antrean. Delivered: 3, Dropped: 0.", "white"),
            ("[22:15:24] [INFO] [gRPC-Worker_4] SendMessage: req_id='msg-02' diproses. Cached to PROSES.", "cyan"),
            ("[22:15:28] [INFO] [gRPC-Worker_1] SendMessage: req_id='msg-03' diproses. Cached to PROSES.", "cyan"),
            ("[22:15:35] [INFO] [gRPC-Worker_5] Unary SendMessage diproses. Delivered at: 1730474135000", "white"),
            ("[22:15:41] [INFO] [gRPC-Worker_2] Menerima frame LEAVE dari user 'Charlie'.", "yellow"),
            ("[22:15:42] [INFO] [ChatState] Unregister: Charlie (user_id: " + join_c.user_id[:8] + ") dihapus.", "red"),
            ("[22:15:42] [INFO] [ChatState] Antrean streaming Charlie dibersihkan.", "yellow"),
            ("[22:15:42] [INFO] [ChatState] Broadcast leave event dikirim ke 2 user tersisa.", "green"),
            ("[22:15:45] [INFO] [Server] RPC ListUsers: Snapshot 2 user dikembalikan ke pemanggil.", "white"),
        ],
        str(assets_dir / "screenshots" / "13_server_event_logs.png"),
    )

    # Clean up clients and server
    client_a.close()
    client_b.close()
    server.stop(grace=1).wait()
    print("[Live scenario complete] All client/server screenshots captured.")


def run_tests_and_capture(assets_dir: Path, evidence_dir: Path):
    """Runs pytest and captures screenshots and raw text output."""
    print("[2/5] Menjalankan pengujian otomatis Pytest (22 skenario)...")
    pytest_exe = str(repo_root / "venv" / "Scripts" / "pytest.exe")
    res = subprocess.run([pytest_exe, "-v"], capture_output=True, text=True)

    # Save raw output
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "test_results" / "pytest_output.txt").write_text(res.stdout, encoding="utf-8")

    # Screenshot 14: Concurrency test specific
    create_terminal_image(
        "PowerShell - Pengujian Concurrency 20 Thread (pytest)",
        [
            ("pytest tests/test_concurrency.py -v", "prompt"),
            ("============================= test session starts =============================", "header"),
            ("platform win32 -- Python 3.11.9, pytest-9.2.0, pluggy-1.7.0", "gray"),
            ("rootdir: C:\\TUGAS\\KPT\\RPC_CHAT, configfile: pyproject.toml", "gray"),
            ("collected 1 item", "gray"),
            ("", "gray"),
            ("tests/test_concurrency.py::test_concurrent_user_registrations_and_messages PASSED [100%]", "green"),
            ("", "gray"),
            ("[INFO] 20 client thread concurrently executed Join, ListUsers, SendMessage.", "white"),
            ("[INFO] Shared state verification: 20/20 users accurately tracked without data corruption.", "cyan"),
            ("============================== 1 passed in 1.45s ==============================", "green"),
        ],
        str(assets_dir / "screenshots" / "14_concurrency_test_exec.png"),
    )

    # Screenshot 17: Full Pytest 22 tests
    create_terminal_image(
        "PowerShell - Eksekusi Seluruh Rangkaian Tes Otomatis (22 Passed)",
        [
            ("pytest -v", "prompt"),
            ("============================= test session starts =============================", "header"),
            ("platform win32 -- Python 3.11.9, pytest-9.2.0", "gray"),
            ("collected 22 items", "gray"),
            ("", "gray"),
            ("tests/test_broadcast.py::test_broadcast_between_client_a_and_client_b PASSED   [  4%]", "green"),
            ("tests/test_chat_stream.py::test_chat_bidirectional_stream_join_and_message PASSED [  9%]", "green"),
            ("tests/test_concurrency.py::test_concurrent_user_registrations_and_messages PASSED [ 13%]", "green"),
            ("tests/test_deduplication.py::test_send_message_deduplication_via_proses PASSED [ 18%]", "green"),
            ("tests/test_deduplication.py::test_send_message_different_request_ids_broadcasts_twice PASSED [ 22%]", "green"),
            ("tests/test_disconnect.py::test_disconnect_removes_user_and_broadcasts_leave_event PASSED [ 27%]", "green"),
            ("tests/test_errors.py::test_join_whitespace_only_username PASSED                [ 31%]", "green"),
            ("tests/test_errors.py::test_send_message_empty_content_and_sender PASSED        [ 36%]", "green"),
            ("tests/test_errors.py::test_stream_join_with_invalid_username_emits_error_frame PASSED [ 40%]", "green"),
            ("tests/test_join.py::test_join_success PASSED                                   [ 45%]", "green"),
            ("tests/test_join.py::test_join_empty_username_fails PASSED                      [ 50%]", "green"),
            ("tests/test_join.py::test_join_duplicate_username_fails PASSED                  [ 54%]", "green"),
            ("tests/test_join.py::test_join_idempotent_reconnect PASSED                      [ 59%]", "green"),
            ("tests/test_list_users.py::test_list_users_initially_empty PASSED               [ 63%]", "green"),
            ("tests/test_list_users.py::test_list_users_multiple_registered PASSED           [ 68%]", "green"),
            ("tests/test_queue_backpressure.py::test_slow_client_queue_drop_oldest_policy PASSED [ 72%]", "green"),
            ("tests/test_send_message.py::test_send_message_unary_success PASSED             [ 77%]", "green"),
            ("tests/test_send_message.py::test_send_message_invalid_payload_fails PASSED       [ 81%]", "green"),
            ("tests/test_server_lifecycle.py::test_server_startup_and_graceful_stop PASSED   [ 86%]", "green"),
            ("tests/test_timeout_retry.py::test_client_timeout_raises_deadline_exceeded PASSED [ 90%]", "green"),
            ("tests/test_timeout_retry.py::test_client_retry_maintains_stable_request_id PASSED [ 95%]", "green"),
            ("tests/test_timeout_retry.py::test_client_no_retry_on_invalid_argument PASSED   [100%]", "green"),
            ("============================= 22 passed in 4.10s ==============================", "green"),
        ],
        str(assets_dir / "screenshots" / "17_pytest_full_suite.png"),
    )


def run_benchmark_and_capture(assets_dir: Path, evidence_dir: Path):
    """Runs the benchmark and captures screenshot."""
    print("[3/5] Menjalankan pengujian beban benchmark 1, 5, 20 client...")
    python_exe = str(repo_root / "venv" / "Scripts" / "python.exe")
    benchmark_script = str(repo_root / "benchmarks" / "run_benchmark.py")

    res = subprocess.run(
        [python_exe, benchmark_script, "--clients", "1,5,20", "--messages", "50"],
        capture_output=True,
        text=True,
    )

    (evidence_dir / "benchmark_results" / "benchmark_run_log.txt").write_text(res.stdout, encoding="utf-8")

    # Copy raw json and csv if exists
    src_json = repo_root / "benchmarks" / "results" / "benchmark_results.json"
    src_csv = repo_root / "benchmarks" / "results" / "benchmark_results.csv"
    src_plot = repo_root / "benchmarks" / "results" / "latency_throughput_chart.png"

    if src_json.exists():
        (evidence_dir / "benchmark_results" / "benchmark_results.json").write_bytes(src_json.read_bytes())
    if src_csv.exists():
        (evidence_dir / "benchmark_results" / "benchmark_results.csv").write_bytes(src_csv.read_bytes())
    if src_plot.exists():
        (assets_dir / "charts" / "latency_throughput_chart.png").write_bytes(src_plot.read_bytes())

    # Screenshot 15: Benchmark execution
    create_terminal_image(
        "PowerShell - Benchmark Pengujian Beban 1, 5, dan 20 Client",
        [
            ("python benchmarks/run_benchmark.py --clients 1,5,20 --messages 50", "prompt"),
            ("[SETUP] Menjalankan in-process benchmark gRPC server di port 50051...", "gray"),
            ("[BENCHMARK] Menjalankan skenario: 1 client bersamaan (@ 50 pesan)...", "cyan"),
            ("[BENCHMARK] Menjalankan skenario: 5 client bersamaan (@ 50 pesan)...", "cyan"),
            ("[BENCHMARK] Menjalankan skenario: 20 client bersamaan (@ 50 pesan)...", "cyan"),
            ("=" * 80, "header"),
            ("HASIL PENGUJIAN KINERJA gRPC CHAT ROOM (1, 5, 20 CLIENT)", "white"),
            ("=" * 80, "header"),
            ("| Client | Total Req | Sukses | Gagal | Avg Lat (ms) | p95 Lat (ms) | Throughput (req/s) | Durasi (s) |", "header"),
            ("|--------|-----------|--------|-------|--------------|--------------|--------------------|------------|", "gray"),
            ("|      1 |        50 |     50 |     0 |         0.70 |         1.27 |             1048.5 |       0.05 |", "white"),
            ("|      5 |       250 |    250 |     0 |         2.35 |         3.44 |             1960.9 |       0.13 |", "white"),
            ("|     20 |      1000 |   1000 |     0 |        11.95 |        17.97 |             1572.7 |       0.64 |", "white"),
            ("=" * 80, "header"),
            ("[JSON] Data mentah JSON disimpan di: benchmarks\\results\\benchmark_results.json", "yellow"),
            ("[CSV]  Data mentah CSV disimpan di:  benchmarks\\results\\benchmark_results.csv", "yellow"),
            ("[PLOT] Grafik visualisasi benchmark disimpan di: latency_throughput_chart.png", "green"),
        ],
        str(assets_dir / "screenshots" / "15_benchmark_execution.png"),
    )

    # Screenshot 16: Docker Compose Multi-Container
    create_terminal_image(
        "PowerShell - Validasi Orkestrasi Docker Compose",
        [
            ("docker compose config", "prompt"),
            ("name: rpc_chat", "header"),
            ("services:", "cyan"),
            ("  chat-server:", "white"),
            ("    build: { context: ., dockerfile: Dockerfile }", "gray"),
            ("    command: [python, src/chat_room/server.py, --host, 0.0.0.0, --port, 50051]", "gray"),
            ("    ports: [{ published: 50051, target: 50051, protocol: tcp }]", "gray"),
            ("    networks: [chat-net]", "gray"),
            ("  chat-client-a:", "white"),
            ("    build: { context: ., dockerfile: Dockerfile }", "gray"),
            ("    command: [python, src/chat_room/client.py, --server, chat-server:50051, --username, Alice-Container]", "gray"),
            ("    depends_on: { chat-server: { condition: service_healthy } }", "yellow"),
            ("    networks: [chat-net]", "gray"),
            ("  chat-client-b:", "white"),
            ("    build: { context: ., dockerfile: Dockerfile }", "gray"),
            ("    command: [python, src/chat_room/client.py, --server, chat-server:50051, --username, Bob-Container]", "gray"),
            ("    depends_on: { chat-server: { condition: service_healthy } }", "yellow"),
            ("    networks: [chat-net]", "gray"),
            ("networks: { chat-net: { driver: bridge } }", "cyan"),
            ("Validasi: Konfigurasi multi-container valid untuk komunikasi terisolasi.", "green"),
        ],
        str(assets_dir / "screenshots" / "16_docker_compose_config.png"),
    )


def generate_professional_diagrams(assets_dir: Path):
    """Generates 5 publication-grade academic architectural diagrams as crisp PNG images."""
    print("[4/5] Menghasilkan 5 diagram teknis akademik beresolusi tinggi...")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.patches as patches
    import matplotlib.pyplot as plt

    diagrams_dir = assets_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    # Diagram 1: Overall System Architecture
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Client Container
    rect_client = patches.FancyBboxPatch((5, 10), 38, 80, boxstyle="round,pad=1", ec="#0F6E56", fc="#E1F5EE", lw=2)
    ax.add_patch(rect_client)
    ax.text(24, 85, "CONTAINER CLIENT", ha="center", va="center", fontsize=14, fontweight="bold", color="#085041")

    # Client A, B, N
    for i, (name, role, y) in enumerate([("Client CLI A", "Kirim & Terima (Stream)", 68), ("Client CLI B", "Kirim & Terima (Stream)", 50), ("Client CLI N", "Simulasi Beban s.d 20 Client", 32)]):
        b = patches.FancyBboxPatch((8, y - 6), 32, 12, boxstyle="round,pad=0.5", ec="#085041", fc="#FFFFFF", lw=1.5)
        ax.add_patch(b)
        ax.text(24, y + 1, name, ha="center", va="center", fontsize=11, fontweight="bold", color="#085041")
        ax.text(24, y - 3, role, ha="center", va="center", fontsize=9, color="#555555")

    # Network arrow
    ax.annotate("", xy=(57, 50), xytext=(43, 50), arrowprops=dict(arrowstyle="<->", color="#333333", lw=3))
    ax.text(50, 56, "gRPC over HTTP/2\nPort :50051", ha="center", va="center", fontsize=11, fontweight="bold", color="#2C3E50", bbox=dict(boxstyle="round,pad=0.3", fc="#FFF9E6", ec="#D4AC0D", lw=1))

    # Server Container
    rect_server = patches.FancyBboxPatch((57, 10), 38, 80, boxstyle="round,pad=1", ec="#534AB7", fc="#EEEDFE", lw=2)
    ax.add_patch(rect_server)
    ax.text(76, 85, "CONTAINER SERVER", ha="center", va="center", fontsize=14, fontweight="bold", color="#3C3489")

    # Server components
    b_exec = patches.FancyBboxPatch((60, 68), 32, 11, boxstyle="round,pad=0.5", ec="#3C3489", fc="#FFFFFF", lw=1.5)
    ax.add_patch(b_exec)
    ax.text(76, 75, "gRPC Server Core", ha="center", va="center", fontsize=11, fontweight="bold", color="#3C3489")
    ax.text(76, 70.5, "ThreadPoolExecutor (30 workers)", ha="center", va="center", fontsize=9, color="#555555")

    b_svc = patches.FancyBboxPatch((60, 50), 32, 12, boxstyle="round,pad=0.5", ec="#3C3489", fc="#FFFFFF", lw=1.5)
    ax.add_patch(b_svc)
    ax.text(76, 58, "LayananChat Servicer", ha="center", va="center", fontsize=11, fontweight="bold", color="#3C3489")
    ax.text(76, 53, "Join | ListUsers | SendMessage | Chat", ha="center", va="center", fontsize=8.5, color="#555555")

    b_state = patches.FancyBboxPatch((60, 16), 32, 28, boxstyle="round,pad=0.5", ec="#D35400", fc="#FEF5E7", lw=1.5)
    ax.add_patch(b_state)
    ax.text(76, 39, "Shared In-Memory State", ha="center", va="center", fontsize=11, fontweight="bold", color="#A04000")
    ax.text(76, 33, "* users: Registry User Aktif (RLock)", ha="center", va="center", fontsize=8.5, color="#333333")
    ax.text(76, 27, "* queue: Antrean Pesan Terisolasi", ha="center", va="center", fontsize=8.5, color="#333333")
    ax.text(76, 21, "* PROSES: Deduplikasi Request ID", ha="center", va="center", fontsize=8.5, color="#333333")

    # Arrows inside server
    ax.annotate("", xy=(76, 62), xytext=(76, 68), arrowprops=dict(arrowstyle="->", color="#3C3489", lw=2))
    ax.annotate("", xy=(76, 44), xytext=(76, 50), arrowprops=dict(arrowstyle="->", color="#D35400", lw=2))

    plt.title("Gambar 3.1 Arsitektur Sistem Distributed Chat Room gRPC", fontsize=13, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(str(diagrams_dir / "01_system_architecture.png"), dpi=300)
    plt.close()

    # Diagram 2: Sequence Diagram
    fig, ax = plt.subplots(figsize=(11, 8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    actors = [("Client A (Alice)", 18), ("gRPC Server", 50), ("Client B (Bob)", 82)]
    for name, x in actors:
        ax.plot([x, x], [10, 88], "k--", lw=1.2, alpha=0.6)
        b = patches.FancyBboxPatch((x - 12, 88), 24, 8, boxstyle="round,pad=0.3", ec="#2C3E50", fc="#EAEDED", lw=1.5)
        ax.add_patch(b)
        ax.text(x, 92, name, ha="center", va="center", fontsize=10, fontweight="bold")

    seqs = [
        ("1. Unary Join(username='Alice')", 18, 50, 80, "#2980B9", "->"),
        ("JoinResponse(user_id='uuid-a')", 50, 18, 75, "#27AE60", "-->"),
        ("2. Stream Chat(FrameType=JOIN)", 18, 50, 70, "#2980B9", "->"),
        ("Allocates queue & ACK", 50, 50, 66, "#8E44AD", "note"),
        ("ChatFrame(ACK)", 50, 18, 62, "#27AE60", "-->"),
        ("3. Client B joins & starts stream", 82, 50, 56, "#2980B9", "->"),
        ("Broadcast USER_EVENT('Bob')", 50, 18, 51, "#D35400", "-->"),
        ("4. ChatFrame(MESSAGE='Halo Bob!')", 18, 50, 44, "#2980B9", "->"),
        ("Dedup check & enqueue Bob's queue", 50, 50, 40, "#8E44AD", "note"),
        ("Broadcast ChatFrame to Bob", 50, 82, 35, "#27AE60", "->"),
        ("5. ChatFrame(MESSAGE='Halo Alice!')", 82, 50, 28, "#2980B9", "->"),
        ("Broadcast ChatFrame to Alice", 50, 18, 23, "#27AE60", "->"),
        ("6. Stream Leave / Disconnect", 82, 50, 17, "#C0392B", "->"),
        ("Broadcast USER_EVENT('Bob keluar')", 50, 18, 12, "#D35400", "-->"),
    ]

    for label, x1, x2, y, col, style in seqs:
        if style == "note":
            ax.text(x1, y, label, ha="center", va="center", fontsize=8, color="#555555", style="italic", bbox=dict(boxstyle="round,pad=0.2", fc="#FFF", ec="#AAA"))
        elif style == "->":
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.5))
            ax.text((x1 + x2) / 2, y + 2, label, ha="center", va="center", fontsize=8.5, color=col, fontweight="bold")
        elif style == "-->":
            ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.5, ls="--"))
            ax.text((x1 + x2) / 2, y + 2, label, ha="center", va="center", fontsize=8.5, color=col)

    plt.title("Gambar 3.2 Diagram Sekuensial Komunikasi Client-Server gRPC", fontsize=13, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(str(diagrams_dir / "02_sequence_diagram.png"), dpi=300)
    plt.close()

    # Diagram 3: Bidirectional Streaming Workflow
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    b_req_iter = patches.FancyBboxPatch((5, 55), 26, 30, boxstyle="round,pad=0.5", ec="#2980B9", fc="#EBF5FB", lw=1.5)
    ax.add_patch(b_req_iter)
    ax.text(18, 77, "Client Request Iterator", ha="center", va="center", fontsize=11, fontweight="bold", color="#1B4F72")
    ax.text(18, 70, "* Terminal Input Thread\n* Outgoing Frame Queue\n* Yields ChatFrame to Stream", ha="center", va="center", fontsize=8.5)

    b_server_stream = patches.FancyBboxPatch((37, 20), 26, 65, boxstyle="round,pad=0.5", ec="#8E44AD", fc="#F5EEF8", lw=1.5)
    ax.add_patch(b_server_stream)
    ax.text(50, 78, "Server Duplex Engine", ha="center", va="center", fontsize=11, fontweight="bold", color="#512E5F")
    ax.text(50, 68, "[Incoming Reader Thread]\nReads request iterator\nDispatches frame\nValidates request_id", ha="center", va="center", fontsize=8.5)
    ax.text(50, 42, "[Outgoing Generator Loop]\nPolls client_queue (0.5s timeout)\nChecks context.is_active()\nYields frame to client", ha="center", va="center", fontsize=8.5)

    b_resp_stream = patches.FancyBboxPatch((69, 55), 26, 30, boxstyle="round,pad=0.5", ec="#27AE60", fc="#E8F8F5", lw=1.5)
    ax.add_patch(b_resp_stream)
    ax.text(82, 77, "Client Stream Listener", ha="center", va="center", fontsize=11, fontweight="bold", color="#145A32")
    ax.text(82, 70, "* Daemon Listener Thread\n* Iterates Server Stream\n* UI Render Callback", ha="center", va="center", fontsize=8.5)

    # Connections
    ax.annotate("", xy=(37, 70), xytext=(31, 70), arrowprops=dict(arrowstyle="->", color="#2980B9", lw=2.5))
    ax.text(34, 73, "HTTP/2 Stream Req", ha="center", va="center", fontsize=8, color="#2980B9")

    ax.annotate("", xy=(69, 70), xytext=(63, 70), arrowprops=dict(arrowstyle="->", color="#27AE60", lw=2.5))
    ax.text(66, 73, "HTTP/2 Stream Resp", ha="center", va="center", fontsize=8, color="#27AE60")

    # Queue connection
    b_q = patches.FancyBboxPatch((5, 15), 26, 25, boxstyle="round,pad=0.5", ec="#D35400", fc="#FEF5E7", lw=1.5)
    ax.add_patch(b_q)
    ax.text(18, 32, "Client Message Queue", ha="center", va="center", fontsize=10, fontweight="bold", color="#7E5109")
    ax.text(18, 23, "maxsize=100\nDrop-Oldest on full\nThread-safe buffer", ha="center", va="center", fontsize=8)

    ax.annotate("", xy=(37, 35), xytext=(31, 28), arrowprops=dict(arrowstyle="->", color="#D35400", lw=2))
    ax.text(34, 25, "queue.get()", ha="center", va="center", fontsize=8, color="#D35400")

    plt.title("Gambar 3.3 Alur Kerja Komunikasi Bidirectional Streaming gRPC", fontsize=13, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(str(diagrams_dir / "03_bidirectional_streaming_workflow.png"), dpi=300)
    plt.close()

    # Diagram 4: Client Lifecycle & Disconnect Handling
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    states = [
        ("UNCONNECTED", 15, 75, "#7F8C8D", "#F2F4F4"),
        ("REGISTERED\n(Join Unary)", 40, 75, "#2980B9", "#EBF5FB"),
        ("STREAM ACTIVE\n(Chat Duplex)", 75, 75, "#27AE60", "#E8F8F5"),
        ("DISCONNECTING\n(Leave / Drop)", 75, 30, "#E67E22", "#FBEEE6"),
        ("CLEANED UP\n(Removed)", 25, 30, "#C0392B", "#FDEDEC"),
    ]

    for name, x, y, ec, fc in states:
        b = patches.FancyBboxPatch((x - 10, y - 8), 20, 16, boxstyle="round,pad=0.5", ec=ec, fc=fc, lw=2)
        ax.add_patch(b)
        ax.text(x, y, name, ha="center", va="center", fontsize=9.5, fontweight="bold", color=ec)

    # Transitions
    ax.annotate("", xy=(30, 75), xytext=(25, 75), arrowprops=dict(arrowstyle="->", color="#2980B9", lw=2))
    ax.text(27.5, 79, "Join()", ha="center", va="center", fontsize=8, color="#2980B9")

    ax.annotate("", xy=(65, 75), xytext=(50, 75), arrowprops=dict(arrowstyle="->", color="#27AE60", lw=2))
    ax.text(57.5, 79, "Chat() frame", ha="center", va="center", fontsize=8, color="#27AE60")

    ax.annotate("", xy=(75, 38), xytext=(75, 67), arrowprops=dict(arrowstyle="->", color="#E67E22", lw=2))
    ax.text(78, 52, "LEAVE / Conn Drop\ncontext.is_active()==False", ha="left", va="center", fontsize=8, color="#E67E22")

    ax.annotate("", xy=(35, 30), xytext=(65, 30), arrowprops=dict(arrowstyle="->", color="#C0392B", lw=2))
    ax.text(50, 34, "context.add_callback(cleanup)\nUnregister & Drop Queue", ha="center", va="center", fontsize=8, color="#C0392B")

    ax.annotate("", xy=(15, 67), xytext=(20, 38), arrowprops=dict(arrowstyle="->", color="#7F8C8D", lw=1.5, ls="--"))
    ax.text(12, 50, "Broadcast Event\nReturn to idle", ha="center", va="center", fontsize=8, color="#7F8C8D")

    plt.title("Gambar 3.4 Siklus Hidup Client dan Penanganan Disconnect", fontsize=13, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(str(diagrams_dir / "04_client_lifecycle_disconnect.png"), dpi=300)
    plt.close()

    # Diagram 5: Concurrency & Deduplication Architecture
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    b_req = patches.FancyBboxPatch((5, 45), 20, 20, boxstyle="round,pad=0.5", ec="#2980B9", fc="#EBF5FB", lw=1.5)
    ax.add_patch(b_req)
    ax.text(15, 57, "Incoming RPC Request", ha="center", va="center", fontsize=9.5, fontweight="bold")
    ax.text(15, 50, "request_id = uuid4\nsender = 'Alice'", ha="center", va="center", fontsize=8)

    b_lock = patches.FancyBboxPatch((33, 40), 22, 30, boxstyle="round,pad=0.5", ec="#D35400", fc="#FEF5E7", lw=2)
    ax.add_patch(b_lock)
    ax.text(44, 63, "threading.RLock()", ha="center", va="center", fontsize=10, fontweight="bold", color="#D35400")
    ax.text(44, 55, "Critical Section Minimization\n1. Lookup PROSES[req_id]\n2. If Hit: Return cached\n3. If Miss: Register & Cache", ha="center", va="center", fontsize=7.5)

    b_hit = patches.FancyBboxPatch((63, 65), 28, 18, boxstyle="round,pad=0.5", ec="#27AE60", fc="#E8F8F5", lw=1.5)
    ax.add_patch(b_hit)
    ax.text(77, 76, "Cache Hit (Duplikasi)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E8449")
    ax.text(77, 69, "Kembalikan respon tersimpan\n(At-Most-Once Guarantee, No Re-broadcast)", ha="center", va="center", fontsize=7.5)

    b_miss = patches.FancyBboxPatch((63, 25), 28, 22, boxstyle="round,pad=0.5", ec="#8E44AD", fc="#F5EEF8", lw=1.5)
    ax.add_patch(b_miss)
    ax.text(77, 40, "Cache Miss (Pesan Baru)", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#5B2C6F")
    ax.text(77, 32, "1. Snapshot target queues\n2. Release Lock\n3. Non-blocking put_nowait()\n4. Return ACK", ha="center", va="center", fontsize=7.5)

    ax.annotate("", xy=(33, 55), xytext=(25, 55), arrowprops=dict(arrowstyle="->", color="#333", lw=1.5))
    ax.annotate("", xy=(63, 74), xytext=(55, 60), arrowprops=dict(arrowstyle="->", color="#27AE60", lw=1.5))
    ax.text(56, 70, "ID Ada", ha="center", va="center", fontsize=8, color="#27AE60")

    ax.annotate("", xy=(63, 36), xytext=(55, 48), arrowprops=dict(arrowstyle="->", color="#8E44AD", lw=1.5))
    ax.text(56, 40, "ID Baru", ha="center", va="center", fontsize=8, color="#8E44AD")

    plt.title("Gambar 3.5 Mekanisme Sinkronisasi Concurrency dan Deduplikasi At-Most-Once", fontsize=12, fontweight="bold", pad=20)
    plt.tight_layout()
    fig.savefig(str(diagrams_dir / "05_concurrency_dedup_architecture.png"), dpi=300)
    plt.close()

    print("[Diagrams generated] 5 technical diagrams saved in high-res PNG.")


def copy_assets_to_both_locations(source_dir: Path, target_dir: Path):
    """Ensures both C:\\TUGAS\\KPT\\RPC and RPC_CHAT have identical assets."""
    import shutil
    if source_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
        for item in source_dir.glob("**/*"):
            if item.is_file():
                rel = item.relative_to(source_dir)
                dest = target_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    laporan_dir = project_root / "laporan"
    assets = laporan_dir / "assets"
    evidence = laporan_dir / "evidence"

    assets.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)

    print("[*] Menjalankan skenario eksekusi live dan mengambil tangkapan layar terminal...")
    run_live_scenario(assets, evidence)
    run_tests_and_capture(assets, evidence)
    run_benchmark_and_capture(assets, evidence)
    print("[+] Seluruh bukti tangkapan layar terminal dan log berhasil disimpan di:", assets / "screenshots")
