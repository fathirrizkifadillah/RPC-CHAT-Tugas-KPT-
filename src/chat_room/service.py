"""Implementasi gRPC Servicer untuk LayananChat.

Menyediakan 4 RPC wajib:
1. Join (Unary): Registrasi pengguna / sesi ke server.
2. ListUsers (Unary): Mengambil daftar pengguna aktif dari in-memory state.
3. SendMessage (Unary): Pengiriman pesan dengan perlindungan request_id (at-most-once).
4. Chat (Bidirectional Streaming): Komunikasi real-time dua arah untuk streaming frame pesan.
"""

import logging
from pathlib import Path
import queue
import sys
import threading
import time
from typing import Iterator, Optional

# Pastikan path aman
_pkg_dir = Path(__file__).resolve().parent
_src_dir = _pkg_dir.parent
for _p in [str(_src_dir), str(_pkg_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import grpc

try:
    from . import chat_room_pb2 as pb
    from . import chat_room_pb2_grpc as pb_grpc
    from .config import DEFAULT_STREAM_POLL_TIMEOUT
    from .state import ChatState
except (ImportError, ValueError):
    import chat_room_pb2 as pb
    import chat_room_pb2_grpc as pb_grpc
    from config import DEFAULT_STREAM_POLL_TIMEOUT
    from state import ChatState

logger = logging.getLogger("chat_room.service")


class LayananChatService(pb_grpc.LayananChatServicer):
    """Implementasi service LayananChat sesuai arsitektur diagram."""

    def __init__(self, state: Optional[ChatState] = None):
        self.state = state if state is not None else ChatState()

    def Join(self, request: pb.JoinRequest, context: grpc.ServicerContext) -> pb.JoinResponse:
        """RPC 1: Meregistrasikan pengguna baru ke dalam shared state server."""
        username = request.username.strip()
        if not username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Username tidak boleh kosong")

        success, msg, user_id, joined_at = self.state.register_user(
            username=username,
            client_id=request.client_id,
            request_id=request.request_id,
        )

        if not success:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, msg)

        # Broadcast event pengguna bergabung ke seluruh client yang sudah aktif di stream
        join_event = pb.ChatFrame(
            type=pb.FRAME_TYPE_USER_EVENT,
            request_id=f"evt-join-{user_id}",
            sender="SYSTEM",
            content=f"Pengguna '{username}' telah bergabung ke dalam room.",
            timestamp=joined_at,
            user_id=user_id,
        )
        self.state.broadcast_frame(join_event, exclude_user_id=user_id)

        return pb.JoinResponse(
            success=True,
            message=msg,
            user_id=user_id,
            joined_at=joined_at,
        )

    def ListUsers(self, request: pb.ListUsersRequest, context: grpc.ServicerContext) -> pb.ListUsersResponse:
        """RPC 2: Mengambil daftar pengguna aktif yang tercatat di memori server."""
        users = self.state.get_active_users()
        return pb.ListUsersResponse(
            success=True,
            users=users,
            total_users=len(users),
        )

    def SendMessage(self, request: pb.SendMessageRequest, context: grpc.ServicerContext) -> pb.SendMessageResponse:
        """RPC 3: Jalur Unary untuk pengiriman pesan dengan proteksi deduplikasi request_id."""
        sender = request.sender_username.strip()
        content = request.content.strip()

        if not sender:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nama pengirim tidak boleh kosong")
        if not content:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Konten pesan tidak boleh kosong")

        resp = self.state.process_send_message(
            request_id=request.request_id,
            sender_username=sender,
            content=content,
            timestamp=request.timestamp,
        )
        return resp

    def Chat(
        self, request_iterator: Iterator[pb.ChatFrame], context: grpc.ServicerContext
    ) -> Iterator[pb.ChatFrame]:
        """RPC 4: Bidirectional Streaming untuk pertukaran pesan real-time dua arah."""
        current_user_id: Optional[str] = None
        current_username: Optional[str] = None
        stop_event = threading.Event()
        client_queue: Optional[queue.Queue] = None

        def cleanup():
            if stop_event.is_set():
                return
            stop_event.set()

            if current_user_id:
                # Bersihkan queue streaming
                self.state.unregister_stream_queue(current_user_id)
                # Unregister user jika sesi stream terputus
                ok, uname = self.state.unregister_user(current_user_id)
                if ok:
                    leave_event = pb.ChatFrame(
                        type=pb.FRAME_TYPE_USER_EVENT,
                        request_id=f"evt-leave-{current_user_id}",
                        sender="SYSTEM",
                        content=f"Pengguna '{uname}' telah keluar dari room.",
                        timestamp=int(time.time() * 1000),
                        user_id=current_user_id,
                    )
                    self.state.broadcast_frame(leave_event)
                    logger.info("Stream disconnect cleanup selesai untuk '%s'", uname)

        # Daftarkan callback disconnect otomatis dari gRPC context
        context.add_callback(cleanup)

        def incoming_reader():
            nonlocal current_user_id, current_username, client_queue
            try:
                for frame in request_iterator:
                    if stop_event.is_set() or not context.is_active():
                        break

                    # 1. Frame Registrasi/Join Stream
                    if frame.type == pb.FRAME_TYPE_JOIN:
                        req_username = frame.sender.strip()
                        req_client_id = frame.user_id or ""
                        req_id = frame.request_id or ""

                        # Jika client sudah terdaftar sebelumnya melalui Unary Join
                        existing_user = self.state.get_user_by_id(frame.user_id) if frame.user_id else None
                        if existing_user:
                            current_user_id = frame.user_id
                            current_username = existing_user["username"]
                        else:
                            ok, msg, uid, joined_at = self.state.register_user(
                                username=req_username,
                                client_id=req_client_id,
                                request_id=req_id,
                            )
                            if not ok:
                                err_frame = pb.ChatFrame(
                                    type=pb.FRAME_TYPE_ERROR,
                                    sender="SYSTEM",
                                    content=f"Registrasi gagal: {msg}",
                                    timestamp=int(time.time() * 1000),
                                )
                                if client_queue is None:
                                    client_queue = queue.Queue(maxsize=10)
                                client_queue.put_nowait(err_frame)
                                time.sleep(0.1)
                                stop_event.set()
                                return

                            current_user_id = uid
                            current_username = req_username

                        # Buat dan kaitkan antrean pesan individual untuk user ini
                        client_queue = self.state.register_stream_queue(current_user_id)

                        # Kirim konfirmasi ACK Join ke client itu sendiri
                        ack_frame = pb.ChatFrame(
                            type=pb.FRAME_TYPE_ACK,
                            request_id=frame.request_id,
                            sender="SYSTEM",
                            content=f"Terhubung ke room sebagai '{current_username}'",
                            timestamp=int(time.time() * 1000),
                            user_id=current_user_id,
                        )
                        client_queue.put_nowait(ack_frame)

                        # Broadcast event kehadiran ke client lain
                        join_event = pb.ChatFrame(
                            type=pb.FRAME_TYPE_USER_EVENT,
                            request_id=f"evt-stream-join-{current_user_id}",
                            sender="SYSTEM",
                            content=f"Pengguna '{current_username}' sedang aktif di room.",
                            timestamp=int(time.time() * 1000),
                            user_id=current_user_id,
                        )
                        self.state.broadcast_frame(join_event, exclude_user_id=current_user_id)

                    # 2. Frame Pesan Chat Standar
                    elif frame.type == pb.FRAME_TYPE_MESSAGE:
                        if not current_user_id:
                            # Frame diterima sebelum registrasi
                            continue

                        # Cek deduplikasi request_id di PROSES
                        req_id = frame.request_id
                        if req_id and self.state.get_cached_proses(req_id):
                            logger.info("Deduplikasi Streaming Message: '%s' sudah diproses", req_id)
                            continue

                        if req_id:
                            self.state.save_cached_proses(req_id, True)

                        # Normalisasi sender
                        sender_name = current_username if current_username else frame.sender
                        broadcast_msg = pb.ChatFrame(
                            type=pb.FRAME_TYPE_MESSAGE,
                            request_id=frame.request_id,
                            sender=sender_name,
                            content=frame.content,
                            timestamp=frame.timestamp or int(time.time() * 1000),
                            user_id=current_user_id,
                        )
                        # Broadcast ke semua pengguna termasuk pengirim (atau semua kecuali pengirim jika diinginkan)
                        self.state.broadcast_frame(broadcast_msg)

                    # 3. Frame Heartbeat
                    elif frame.type == pb.FRAME_TYPE_HEARTBEAT:
                        if client_queue:
                            hb_ack = pb.ChatFrame(
                                type=pb.FRAME_TYPE_HEARTBEAT,
                                request_id=frame.request_id,
                                sender="SYSTEM",
                                content="PONG",
                                timestamp=int(time.time() * 1000),
                            )
                            client_queue.put_nowait(hb_ack)

                    # 4. Frame Keluar (Leave)
                    elif frame.type == pb.FRAME_TYPE_LEAVE:
                        logger.info("Menerima frame LEAVE dari user '%s'", current_username)
                        break

            except Exception as e:
                logger.error("Error pada incoming_reader stream: %s", e)
            finally:
                cleanup()

        # Jalankan reader incoming frames di thread worker terpisah
        reader_thread = threading.Thread(target=incoming_reader, daemon=True)
        reader_thread.start()

        # Generator loop untuk mengirimkan frame outgoing dari queue ke stream
        try:
            while not stop_event.is_set() and context.is_active():
                if client_queue is None:
                    # Menunggu registrasi frame pertama tiba
                    time.sleep(0.05)
                    continue

                try:
                    outgoing_frame = client_queue.get(timeout=DEFAULT_STREAM_POLL_TIMEOUT)
                    yield outgoing_frame
                    if outgoing_frame.type == pb.FRAME_TYPE_ERROR:
                        break
                except queue.Empty:
                    continue
        except Exception as e:
            logger.info("Koneksi outgoing stream terputus: %s", e)
        finally:
            cleanup()
            reader_thread.join(timeout=1.0)
