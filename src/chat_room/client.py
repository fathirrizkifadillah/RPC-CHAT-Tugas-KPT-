"""Modul Client Terminal CLI untuk Distributed Chat Room.

Mendukung:
1. Bidirectional streaming real-time chat (RPC Chat).
2. Unary RPC (SendMessage, ListUsers, Join) dengan Timeout dan Retry (Exponential Backoff).
3. Penanganan Request ID yang stabil saat retry (mencegah duplikasi pesan).
4. Penanganan disconnect yang tertib (graceful shutdown).
"""

import argparse
import logging
import queue
import random
import sys
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional
import uuid

# Pastikan path aman
_pkg_dir = Path(__file__).resolve().parent
_src_dir = _pkg_dir.parent
for _p in [str(_src_dir), str(_pkg_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import grpc
from tabulate import tabulate

try:
    from . import chat_room_pb2 as pb
    from . import chat_room_pb2_grpc as pb_grpc
    from .config import (
        DEFAULT_BASE_RETRY_DELAY,
        DEFAULT_MAX_RETRIES,
        DEFAULT_SERVER_ADDRESS,
        DEFAULT_UNARY_TIMEOUT,
    )
except (ImportError, ValueError):
    import chat_room_pb2 as pb
    import chat_room_pb2_grpc as pb_grpc
    from config import (
        DEFAULT_BASE_RETRY_DELAY,
        DEFAULT_MAX_RETRIES,
        DEFAULT_SERVER_ADDRESS,
        DEFAULT_UNARY_TIMEOUT,
    )

logger = logging.getLogger("chat_room.client")


class ChatClient:
    """Client gRPC untuk LayananChat dengan ketahanan jaringan dan bidirectional streaming."""

    def __init__(
        self,
        server_address: str = DEFAULT_SERVER_ADDRESS,
        username: str = "",
        timeout: float = DEFAULT_UNARY_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_retry_delay: float = DEFAULT_BASE_RETRY_DELAY,
    ):
        self.server_address = server_address
        self.username = username
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_retry_delay = base_retry_delay

        self.client_id = f"client-{uuid.uuid4().hex[:8]}"
        self.user_id: Optional[str] = None
        self.channel: Optional[grpc.Channel] = None
        self.stub: Optional[pb_grpc.LayananChatStub] = None

        # Queue untuk mengalirkan frame outgoing ke bidirectional stream
        self._outgoing_queue: queue.Queue = queue.Queue()
        self._is_running = threading.Event()
        self._stream_listener_thread: Optional[threading.Thread] = None

    def connect(self) -> None:
        """Membuka channel koneksi gRPC ke server."""
        if not self.channel:
            # Menggunakan HTTP/2 channel insecure
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = pb_grpc.LayananChatStub(self.channel)
            logger.info("Terhubung ke server gRPC di %s", self.server_address)

    def close(self) -> None:
        """Menutup koneksi client dan unregister dari server secara tertib."""
        if not self._is_running.is_set():
            return
        self._is_running.clear()

        # Kirim frame LEAVE ke server stream jika aktif
        try:
            leave_frame = pb.ChatFrame(
                type=pb.FRAME_TYPE_LEAVE,
                sender=self.username,
                content="Leaving",
                timestamp=int(time.time() * 1000),
                user_id=self.user_id or "",
            )
            self._outgoing_queue.put_nowait(leave_frame)
        except Exception:
            pass

        # Tunggu stream listener thread selesai
        if self._stream_listener_thread and self._stream_listener_thread.is_alive():
            self._stream_listener_thread.join(timeout=1.5)

        if self.channel:
            self.channel.close()
            self.channel = None
            self.stub = None
            logger.info("Channel client ditutup.")

    # =========================================================================
    # RPC Unary dengan Timeout, Retry, dan Request ID Konsisten
    # =========================================================================

    def join_with_retry(self, username: Optional[str] = None) -> pb.JoinResponse:
        """Memanggil RPC Join dengan retry dan request_id yang stabil."""
        self.connect()
        target_username = self.username if username is None else username
        rid = str(uuid.uuid4())  # Request ID stabil untuk seluruh percobaan retry

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                req = pb.JoinRequest(
                    username=target_username,
                    client_id=self.client_id,
                    request_id=rid,
                )
                resp = self.stub.Join(req, timeout=self.timeout)
                if resp.success:
                    self.username = target_username
                    self.user_id = resp.user_id
                    return resp
                raise RuntimeError(resp.message)

            except grpc.RpcError as e:
                last_error = e
                # Hanya retry error sementara (transient error)
                can_retry = e.code() in (
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                )
                if not can_retry or attempt == self.max_retries:
                    logger.error("Join gagal permanen atau batas retry tercapai: %s", e)
                    raise

                # Hitung jeda exponential backoff dengan sedikit jitter
                delay = self.base_retry_delay * (2 ** (attempt - 1)) + random.uniform(0.01, 0.1)
                logger.warning(
                    "Join percobaan %d/%d gagal (%s). Retry dalam %.2f detik...",
                    attempt,
                    self.max_retries,
                    e.code().name,
                    delay,
                )
                time.sleep(delay)

        raise last_error or RuntimeError("Join gagal setelah retry")

    def list_users_with_retry(self) -> List[pb.UserInfo]:
        """Mengambil daftar pengguna aktif via RPC ListUsers dengan timeout dan retry."""
        self.connect()
        rid = str(uuid.uuid4())

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                req = pb.ListUsersRequest(request_id=rid)
                resp = self.stub.ListUsers(req, timeout=self.timeout)
                return list(resp.users)

            except grpc.RpcError as e:
                last_error = e
                can_retry = e.code() in (
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.UNAVAILABLE,
                )
                if not can_retry or attempt == self.max_retries:
                    raise

                delay = self.base_retry_delay * (2 ** (attempt - 1))
                time.sleep(delay)

        raise last_error or RuntimeError("ListUsers gagal setelah retry")

    def send_message_unary_with_retry(
        self, content: str, request_id: Optional[str] = None
    ) -> pb.SendMessageResponse:
        """Mengirim pesan via RPC Unary SendMessage dengan perlindungan request_id stabil."""
        self.connect()
        rid = request_id or str(uuid.uuid4())  # Request ID SAMA untuk seluruh siklus retry

        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                req = pb.SendMessageRequest(
                    request_id=rid,
                    sender_username=self.username,
                    content=content,
                    timestamp=int(time.time() * 1000),
                )
                resp = self.stub.SendMessage(req, timeout=self.timeout)
                return resp

            except grpc.RpcError as e:
                last_error = e
                can_retry = e.code() in (
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                    grpc.StatusCode.UNAVAILABLE,
                )
                if not can_retry or attempt == self.max_retries:
                    logger.error("SendMessage gagal permanen (%s): %s", e.code(), e.details())
                    raise

                delay = self.base_retry_delay * (2 ** (attempt - 1)) + random.uniform(0.01, 0.1)
                logger.warning(
                    "SendMessage percobaan %d gagal (%s). Retry dengan request_id sama dalam %.2f s...",
                    attempt,
                    e.code().name,
                    delay,
                )
                time.sleep(delay)

        raise last_error or RuntimeError("SendMessage gagal setelah retry")

    # =========================================================================
    # Bidirectional Streaming Real-Time (RPC Chat)
    # =========================================================================

    def _generate_outgoing_frames(self):
        """Generator yang menghasilkan ChatFrame ke server stream."""
        # Kirim frame pembuka Join Stream
        join_frame = pb.ChatFrame(
            type=pb.FRAME_TYPE_JOIN,
            request_id=str(uuid.uuid4()),
            sender=self.username,
            content="Entering chat room",
            timestamp=int(time.time() * 1000),
            user_id=self.user_id or "",
        )
        yield join_frame

        # Loop membaca antrean pesan yang ingin dikirim pengguna
        while self._is_running.is_set():
            try:
                frame = self._outgoing_queue.get(timeout=0.5)
                yield frame
                if frame.type == pb.FRAME_TYPE_LEAVE:
                    break
            except queue.Empty:
                continue

    def start_chat_stream(self, on_message_callback: Optional[Callable[[pb.ChatFrame], None]] = None) -> None:
        """Memulai sesi bidirectional streaming Chat."""
        self.connect()
        self._is_running.set()

        def stream_listener():
            try:
                # Buka duplex stream ke server
                responses = self.stub.Chat(self._generate_outgoing_frames())
                for frame in responses:
                    if not self._is_running.is_set():
                        break
                    if on_message_callback:
                        on_message_callback(frame)
                    else:
                        self._default_render_frame(frame)

            except grpc.RpcError as e:
                if self._is_running.is_set():
                    print(f"\n[DISCONNECT] Koneksi chat stream terputus: {e.code().name} - {e.details()}")
            except Exception as ex:
                if self._is_running.is_set():
                    print(f"\n[ERROR] Kesalahan stream: {ex}")
            finally:
                self._is_running.clear()

        self._stream_listener_thread = threading.Thread(
            target=stream_listener, daemon=True, name="StreamListener"
        )
        self._stream_listener_thread.start()

    def send_chat_message(self, content: str) -> str:
        """Mengirim pesan chat teks ke dalam bidirectional stream."""
        rid = str(uuid.uuid4())
        frame = pb.ChatFrame(
            type=pb.FRAME_TYPE_MESSAGE,
            request_id=rid,
            sender=self.username,
            content=content,
            timestamp=int(time.time() * 1000),
            user_id=self.user_id or "",
        )
        self._outgoing_queue.put(frame)
        return rid

    def _default_render_frame(self, frame: pb.ChatFrame) -> None:
        """Format tampilan pesan terminal bawaan."""
        t_str = time.strftime("%H:%M:%S", time.localtime(frame.timestamp / 1000)) if frame.timestamp else ""

        if frame.type == pb.FRAME_TYPE_MESSAGE:
            if frame.sender == self.username:
                print(f"[{t_str}] (Anda): {frame.content}")
            else:
                print(f"[{t_str}] <{frame.sender}>: {frame.content}")

        elif frame.type == pb.FRAME_TYPE_USER_EVENT:
            print(f"[{t_str}] 🔔 {frame.content}")

        elif frame.type == pb.FRAME_TYPE_ACK:
            print(f"[{t_str}] ℹ️  {frame.content}")

        elif frame.type == pb.FRAME_TYPE_ERROR:
            print(f"[{t_str}] ⚠️  {frame.content}")


def run_interactive_cli(server_address: str, username: str) -> None:
    """Menjalankan terminal interaktif untuk pengguna obrolan."""
    print("=" * 60)
    print("💬 DISTRIBUTED CHAT ROOM - gRPC CLIENT CLI")
    print(f"   Server   : {server_address}")
    print("=" * 60)

    while not username.strip():
        username = input("Masukkan username Anda: ").strip()

    client = ChatClient(server_address=server_address, username=username)

    try:
        print(f"\n[INFO] Menghubungkan dan meregistrasi sebagai '{username}'...")
        join_resp = client.join_with_retry()
        print(f"[SUCCESS] {join_resp.message} (User ID: {join_resp.user_id})")

        print("[INFO] Memulai real-time bidirectional stream...")
        client.start_chat_stream()

        print("\n" + "-" * 60)
        print("Perintah yang tersedia:")
        print("  <teks biasa>     : Kirim pesan real-time (Bidirectional Stream)")
        print("  /users           : Lihat daftar pengguna online (Unary ListUsers)")
        print("  /unary <pesan>   : Kirim pesan lewat jalur Unary SendMessage")
        print("  /help            : Tampilkan bantuan ini")
        print("  /exit atau /quit : Keluar dari obrolan")
        print("-" * 60 + "\n")

        while client._is_running.is_set():
            try:
                line = input().strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not line:
                continue

            if line in ("/exit", "/quit"):
                print("[INFO] Mengirim sinyal keluar...")
                break

            elif line == "/help":
                print("Perintah: /users (lihat user), /unary <pesan> (kirim unary), /exit (keluar)")

            elif line == "/users":
                try:
                    users = client.list_users_with_retry()
                    table_data = [
                        [
                            u.username,
                            u.user_id,
                            time.strftime("%H:%M:%S", time.localtime(u.connected_at / 1000)),
                            "Online" if u.is_active else "Offline",
                        ]
                        for u in users
                    ]
                    print("\n" + tabulate(table_data, headers=["Username", "User ID", "Waktu Join", "Status"]) + "\n")
                except Exception as ex:
                    print(f"[ERROR] Gagal mengambil daftar pengguna: {ex}")

            elif line.startswith("/unary "):
                content = line[7:].strip()
                if content:
                    try:
                        resp = client.send_message_unary_with_retry(content)
                        print(f"✅ [UNARY ACK] Pesan terkirim (req_id: {resp.request_id[:8]}...)")
                    except Exception as ex:
                        print(f"❌ [UNARY FAIL] Gagal mengirim pesan unary: {ex}")

            else:
                client.send_chat_message(line)

    except Exception as e:
        print(f"[FATAL] Gagal memulai client: {e}")
    finally:
        print("\n[INFO] Menutup sesi obrolan...")
        client.close()
        print("[INFO] Sampai jumpa!")


def main() -> None:
    """CLI entry point untuk Client."""
    parser = argparse.ArgumentParser(description="Distributed Chat Room gRPC Client CLI")
    parser.add_argument("--server", default=DEFAULT_SERVER_ADDRESS, help="gRPC Server address (default: localhost:50051)")
    parser.add_argument("--username", default="", help="Username to join with")
    parser.add_argument("--timeout", type=float, default=DEFAULT_UNARY_TIMEOUT, help="Unary RPC timeout in seconds")
    parser.add_argument("--retries", type=int, default=DEFAULT_MAX_RETRIES, help="Maximum retry attempts")
    args = parser.parse_args()

    run_interactive_cli(server_address=args.server, username=args.username)


if __name__ == "__main__":
    main()
