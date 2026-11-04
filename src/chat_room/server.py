"""Modul eksekusi gRPC Server untuk Distributed Chat Room.

Sesuai dengan diagram arsitektur:
- Menjalankan ThreadPoolExecutor dengan worker terkonfigurasi
- Bind ke port 50051 (atau port kustom) dengan dukungan IPv4/IPv6 ([::]:50051)
- Mendukung graceful shutdown saat menerima sinyal SIGINT/SIGTERM
"""

import argparse
from concurrent import futures
import logging
from pathlib import Path
import signal
import sys
import threading
import time
from typing import Optional, Tuple

# Pastikan direktori root, src, dan chat_room masuk sys.path agar aman dijalankan langsung
_pkg_dir = Path(__file__).resolve().parent
_src_dir = _pkg_dir.parent
for _p in [str(_src_dir), str(_pkg_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import grpc

try:
    from . import chat_room_pb2_grpc as pb_grpc
    from .config import DEFAULT_HOST, DEFAULT_MAX_WORKERS, DEFAULT_PORT
    from .service import LayananChatService
    from .state import ChatState
except (ImportError, ValueError):
    import chat_room_pb2_grpc as pb_grpc
    from config import DEFAULT_HOST, DEFAULT_MAX_WORKERS, DEFAULT_PORT
    from service import LayananChatService
    from state import ChatState

# Reconfigure stdout for utf-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("chat_room.server")


def create_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    max_workers: int = DEFAULT_MAX_WORKERS,
    state: Optional[ChatState] = None,
) -> Tuple[grpc.Server, LayananChatService, ChatState]:
    """Factory helper untuk membuat instance gRPC server beserta servicernya."""
    shared_state = state if state is not None else ChatState()
    service = LayananChatService(state=shared_state)

    executor = futures.ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="gRPC-Worker"
    )
    server = grpc.server(executor)

    pb_grpc.add_LayananChatServicer_to_server(service, server)

    # Bind ke port yang diminta, dukung 0.0.0.0 atau [::] untuk akses container/jaringan luar
    bind_address = f"{host}:{port}"
    server.add_insecure_port(bind_address)

    return server, service, shared_state


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, max_workers: int = DEFAULT_MAX_WORKERS) -> None:
    """Menjalankan gRPC server dan menunggu hingga proses dihentikan."""
    server, _, _ = create_server(host=host, port=port, max_workers=max_workers)
    server.start()

    bind_address = f"{host}:{port}"
    print("=" * 60)
    print(f"[*] gRPC Chat Server Berhasil Dijalankan")
    print(f"   Alamat Bind : {bind_address}")
    print(f"   Max Workers : {max_workers} threads (ThreadPoolExecutor)")
    print(f"   Service     : LayananChat (Join, ListUsers, SendMessage, Chat)")
    print("=" * 60)
    print("Tekan Ctrl+C untuk melakukan graceful shutdown...")

    stop_event = threading.Event()

    def signal_handler(signum, frame):
        print("\n[INFO] Sinyal penghentian diterima. Melakukan graceful shutdown...")
        stop_event.set()

    # Daftarkan handler sinyal sistem
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (ValueError, AttributeError):
        # Beberapa thread context pada Windows mungkin membatasi signal registration
        pass

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt terdeteksi.")
    finally:
        print("[INFO] Menghentikan gRPC server (grace period 3 detik)...")
        server.stop(grace=3).wait()
        print("[INFO] Server telah dimatikan secara tertib.")


def main() -> None:
    """CLI entry point untuk menjalankan server."""
    parser = argparse.ArgumentParser(description="Distributed Chat Room gRPC Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on (default: 50051)")
    parser.add_argument(
        "--workers", type=int, default=DEFAULT_MAX_WORKERS, help="ThreadPoolExecutor max workers (default: 30)"
    )
    args = parser.parse_args()

    serve(host=args.host, port=args.port, max_workers=args.workers)


if __name__ == "__main__":
    main()
