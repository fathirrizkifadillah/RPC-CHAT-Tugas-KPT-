"""Tests for Server Startup, Port Binding, and Graceful Shutdown."""

import socket
import time
import grpc
import pytest

from chat_room.server import create_server
from tests.conftest import get_free_port


def test_server_startup_and_graceful_stop():
    """Server dapat dimulai dan dimatikan secara tertib tanpa hanging."""
    port = get_free_port()
    server, service, state = create_server(host="127.0.0.1", port=port, max_workers=5)
    server.start()

    # Pastikan port aktif dan listening
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        conn_res = s.connect_ex(("127.0.0.1", port))
        assert conn_res == 0, f"Port {port} harus listening setelah server.start()"

    # Hentikan server dengan grace period
    stop_event = server.stop(grace=1.0)
    stop_event.wait(timeout=2.0)

    # Pastikan port dilepaskan
    time.sleep(0.3)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        conn_after = s.connect_ex(("127.0.0.1", port))
        assert conn_after != 0, f"Port {port} harus tertutup setelah server.stop()"
