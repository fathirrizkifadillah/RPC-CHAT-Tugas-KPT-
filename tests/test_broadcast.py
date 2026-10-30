"""Tests for Multi-Client Real-Time Message Broadcast via gRPC."""

import queue
import threading
import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb
from chat_room.client import ChatClient


def test_broadcast_between_client_a_and_client_b(test_server):
    """Pesan yang dikirim oleh Client A melalui stream gRPC benar-benar diterima oleh Client B."""
    _, address, _ = test_server

    client_a = ChatClient(server_address=address, username="ClientA")
    client_b = ChatClient(server_address=address, username="ClientB")

    b_received_messages = []
    received_event = threading.Event()

    def on_client_b_message(frame: pb.ChatFrame):
        if frame.type == pb.FRAME_TYPE_MESSAGE:
            b_received_messages.append(frame)
            if frame.content == "Halo dari Client A!":
                received_event.set()

    try:
        # 1. Join kedua client
        resp_a = client_a.join_with_retry()
        resp_b = client_b.join_with_retry()
        assert resp_a.success and resp_b.success

        # 2. Buka stream untuk kedua client
        client_b.start_chat_stream(on_message_callback=on_client_b_message)
        client_a.start_chat_stream()

        time.sleep(0.3)  # Beri waktu stream terinisialisasi

        # 3. Client A mengirim pesan via stream
        client_a.send_chat_message("Halo dari Client A!")

        # 4. Verifikasi Client B menerima pesan dalam batas waktu
        success = received_event.wait(timeout=3.0)
        assert success is True, "Client B tidak menerima pesan broadcast dari Client A dalam waktu 3 detik"

        assert len(b_received_messages) >= 1
        matching_msg = [m for m in b_received_messages if m.content == "Halo dari Client A!"][0]
        assert matching_msg.sender == "ClientA"
        assert matching_msg.content == "Halo dari Client A!"

    finally:
        client_a.close()
        client_b.close()
