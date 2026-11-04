"""Modul pengelola state bersama (shared in-memory state) server chat.

Mengimplementasikan tiga komponen arsitektur utama:
1. `users` : Registry pengguna aktif yang dilindungi mekanisme sinkronisasi Lock.
2. `queue` : Antrean pesan terisolasi per client (mencegah head-of-line blocking).
3. `PROSES`: Penyimpanan hasil eksekusi untuk deduplikasi at-most-once berdasarkan request_id.
"""

from collections import OrderedDict
import logging
from pathlib import Path
import queue
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

# Pastikan path aman
_pkg_dir = Path(__file__).resolve().parent
_src_dir = _pkg_dir.parent
for _p in [str(_src_dir), str(_pkg_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from . import chat_room_pb2 as pb
    from .config import DEFAULT_CLIENT_QUEUE_MAXSIZE, DEFAULT_MAX_PROSES_CACHE
except (ImportError, ValueError):
    import chat_room_pb2 as pb
    from config import DEFAULT_CLIENT_QUEUE_MAXSIZE, DEFAULT_MAX_PROSES_CACHE

logger = logging.getLogger("chat_room.state")


class ChatState:
    """Komponen Shared State di Memori dengan proteksi Lock thread-safe."""

    def __init__(self, queue_maxsize: int = DEFAULT_CLIENT_QUEUE_MAXSIZE, max_proses: int = DEFAULT_MAX_PROSES_CACHE):
        self._lock = threading.RLock()
        self._queue_maxsize = queue_maxsize
        self._max_proses = max_proses

        # Shared component 1: users (daftar user aktif)
        # user_id -> dict(username, client_id, connected_at, is_active)
        self._users: Dict[str, Dict[str, Any]] = {}
        # username -> user_id (pencarian cepat untuk mencegah username duplikat aktif)
        self._usernames: Dict[str, str] = {}

        # Shared component 2: queue (antrean pesan per client aktif)
        # user_id -> queue.Queue[pb.ChatFrame]
        self._queues: Dict[str, queue.Queue] = {}

        # Shared component 3: PROSES (deduplikasi request_id)
        # request_id -> cached response protobuf message
        self._proses: OrderedDict[str, Any] = OrderedDict()

    def register_user(
        self, username: str, client_id: str = "", request_id: str = ""
    ) -> Tuple[bool, str, str, int]:
        """Meregistrasikan user baru atau mengembalikan sesi jika request_id sama.

        Returns: (success, message, user_id, joined_at)
        """
        username = username.strip()
        if not username:
            return False, "Username tidak boleh kosong", "", 0

        with self._lock:
            # 1. Cek deduplikasi request_id di PROSES
            if request_id and request_id in self._proses:
                cached = self._proses[request_id]
                logger.info("Deduplikasi Join: request_id '%s' ditemukan di PROSES", request_id)
                return cached.success, cached.message, cached.user_id, cached.joined_at

            # 2. Cek apakah username sudah aktif digunakan oleh client lain
            if username in self._usernames:
                existing_user_id = self._usernames[username]
                existing_user = self._users.get(existing_user_id)
                # Jika client_id sama, izinkan reconnect/idempoten
                if client_id and existing_user and existing_user.get("client_id") == client_id:
                    user_id = existing_user_id
                    joined_at = existing_user["connected_at"]
                    resp = pb.JoinResponse(
                        success=True,
                        message=f"Selamat datang kembali, {username} (reconnected)",
                        user_id=user_id,
                        joined_at=joined_at,
                    )
                    if request_id:
                        self._save_proses_locked(request_id, resp)
                    return True, resp.message, user_id, joined_at

                return False, f"Username '{username}' sedang aktif digunakan", "", 0

            # 3. Registrasi pengguna baru
            user_id = str(uuid.uuid4())
            now_ms = int(time.time() * 1000)
            self._users[user_id] = {
                "user_id": user_id,
                "username": username,
                "client_id": client_id,
                "connected_at": now_ms,
                "is_active": True,
            }
            self._usernames[username] = user_id

            resp = pb.JoinResponse(
                success=True,
                message=f"Berhasil bergabung sebagai {username}",
                user_id=user_id,
                joined_at=now_ms,
            )
            if request_id:
                self._save_proses_locked(request_id, resp)

            logger.info("Pengguna '%s' berhasil terdaftar dengan user_id: %s", username, user_id)
            return True, resp.message, user_id, now_ms

    def unregister_user(self, user_id: str) -> Tuple[bool, str]:
        """Menghapus pengguna dari daftar users aktif dan membersihkan queue.

        Returns: (success, username_yang_keluar)
        """
        with self._lock:
            user = self._users.pop(user_id, None)
            if not user:
                return False, ""

            username = user.get("username", "")
            if username in self._usernames:
                del self._usernames[username]

            # Hapus queue client dari map
            self._queues.pop(user_id, None)
            logger.info("Pengguna '%s' (user_id: %s) dikeluarkan dari server", username, user_id)
            return True, username

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Mendapatkan snapshot info user berdasarkan user_id."""
        with self._lock:
            user = self._users.get(user_id)
            return dict(user) if user else None

    def get_active_users(self) -> List[pb.UserInfo]:
        """Mengambil snapshot daftar pengguna aktif secara konsisten."""
        with self._lock:
            user_list: List[pb.UserInfo] = []
            for u in self._users.values():
                user_list.append(
                    pb.UserInfo(
                        user_id=u["user_id"],
                        username=u["username"],
                        connected_at=u["connected_at"],
                        is_active=u["is_active"],
                    )
                )
            return user_list

    def register_stream_queue(self, user_id: str) -> queue.Queue:
        """Membuat dan mengaitkan antrean pesan individual untuk client stream."""
        with self._lock:
            q: queue.Queue = queue.Queue(maxsize=self._queue_maxsize)
            self._queues[user_id] = q
            logger.debug("Antrean pesan dibuat untuk user_id: %s", user_id)
            return q

    def unregister_stream_queue(self, user_id: str) -> Optional[queue.Queue]:
        """Menghapus antrean pesan client stream."""
        with self._lock:
            return self._queues.pop(user_id, None)

    def broadcast_frame(self, frame: pb.ChatFrame, exclude_user_id: Optional[str] = None) -> int:
        """Membroadcast ChatFrame ke seluruh antrean client aktif.

        Menggunakan mekanisme isolasi: mengambil snapshot daftar queue di bawah lock,
        lalu melakukan enqueue non-blocking di luar lock agar tidak memblokir publisher.
        """
        with self._lock:
            # Ambil shallow copy dari antrean yang aktif
            target_queues = [
                (uid, q) for uid, q in self._queues.items() if uid != exclude_user_id
            ]

        delivered_count = 0
        for uid, q in target_queues:
            try:
                # Coba enqueue secara non-blocking
                q.put_nowait(frame)
                delivered_count += 1
            except queue.Full:
                # Isolasi slow client: drop frame tertua agar antrean tidak macet
                logger.warning("Antrean user '%s' penuh! Menerapkan drop-oldest policy.", uid)
                try:
                    _ = q.get_nowait()
                    q.put_nowait(frame)
                    delivered_count += 1
                except Exception:
                    pass

        return delivered_count

    def process_send_message(
        self, request_id: str, sender_username: str, content: str, timestamp: int
    ) -> pb.SendMessageResponse:
        """Memproses pengiriman pesan unary dengan perlindungan deduplikasi request_id."""
        with self._lock:
            # 1. Cek deduplikasi di PROSES
            if request_id and request_id in self._proses:
                logger.info("Deduplikasi SendMessage: request_id '%s' ditemukan di PROSES", request_id)
                return self._proses[request_id]

            # 2. Buat respons baru
            delivered_at = int(time.time() * 1000)
            resp = pb.SendMessageResponse(
                request_id=request_id,
                success=True,
                message="Pesan berhasil dikirim dan dibroadcast",
                delivered_at=delivered_at,
            )

            # 3. Simpan ke PROSES sebelum broadcast
            if request_id:
                self._save_proses_locked(request_id, resp)

        # 4. Broadcast ChatFrame ke seluruh client aktif
        frame = pb.ChatFrame(
            type=pb.FRAME_TYPE_MESSAGE,
            request_id=request_id,
            sender=sender_username,
            content=content,
            timestamp=timestamp or int(time.time() * 1000),
            user_id="",
        )
        self.broadcast_frame(frame)
        return resp

    def get_cached_proses(self, request_id: str) -> Optional[Any]:
        """Mendapatkan hasil eksekusi dari komponen PROSES jika ada."""
        with self._lock:
            return self._proses.get(request_id)

    def save_cached_proses(self, request_id: str, response_obj: Any) -> None:
        """Menyimpan hasil eksekusi ke komponen PROSES secara thread-safe."""
        with self._lock:
            self._save_proses_locked(request_id, response_obj)

    def _save_proses_locked(self, request_id: str, response_obj: Any) -> None:
        """Penyimpanan internal ke PROSES dengan batas LRU (harus dipanggil di bawah lock)."""
        if not request_id:
            return
        if len(self._proses) >= self._max_proses:
            # Buang entri tertua (LRU eviction)
            self._proses.popitem(last=False)
        self._proses[request_id] = response_obj

    def reset_state(self) -> None:
        """Mengosongkan seluruh state (khusus untuk isolasi pengujian / teardown)."""
        with self._lock:
            self._users.clear()
            self._usernames.clear()
            self._queues.clear()
            self._proses.clear()
            logger.debug("ChatState berhasil direset")
