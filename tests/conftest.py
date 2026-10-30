"""Pytest fixtures and configuration for gRPC Chat Room test suite."""

from concurrent import futures
import socket
import sys
from pathlib import Path
import threading
import time
from typing import Generator, Tuple

import grpc
import pytest

# Ensure src is in python path
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from chat_room import chat_room_pb2 as pb
from chat_room import chat_room_pb2_grpc as pb_grpc
from chat_room.service import LayananChatService
from chat_room.state import ChatState


def get_free_port() -> int:
    """Mendapatkan port TCP bebas di sistem host lokal."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture
def clean_state() -> ChatState:
    """Fixture menyediakan instance ChatState baru dan bersih."""
    state = ChatState()
    yield state
    state.reset_state()


@pytest.fixture
def test_server(clean_state: ChatState) -> Generator[Tuple[grpc.Server, str, ChatState], None, None]:
    """Fixture yang menjalankan ephemeral test gRPC server di port lokal acak."""
    port = get_free_port()
    address = f"127.0.0.1:{port}"

    executor = futures.ThreadPoolExecutor(max_workers=15, thread_name_prefix="TestWorker")
    server = grpc.server(executor)
    service = LayananChatService(state=clean_state)
    pb_grpc.add_LayananChatServicer_to_server(service, server)
    server.add_insecure_port(address)
    server.start()

    yield server, address, clean_state

    # Teardown
    server.stop(grace=0.5).wait()


@pytest.fixture
def test_stub(test_server) -> Generator[Tuple[pb_grpc.LayananChatStub, str, ChatState], None, None]:
    """Fixture menyediakan gRPC stub dan channel client yang siap pakai."""
    server, address, state = test_server
    channel = grpc.insecure_channel(address)
    stub = pb_grpc.LayananChatStub(channel)

    yield stub, address, state

    channel.close()
