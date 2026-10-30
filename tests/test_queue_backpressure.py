"""Tests for Client Message Queue Isolation and Slow Client Backpressure."""

import queue
import time
import pytest

from chat_room import chat_room_pb2 as pb
from chat_room.state import ChatState


def test_slow_client_queue_drop_oldest_policy():
    """Client lambat dengan antrean penuh tidak membuat crash server atau memblokir broadcast."""
    # Buat state dengan kapasitas antrean sangat kecil (maxsize=3)
    state = ChatState(queue_maxsize=3)

    # Daftarkan dua client: slow_client dan fast_client
    slow_q = state.register_stream_queue("slow-uid")
    fast_q = state.register_stream_queue("fast-uid")

    # Broadcast 5 pesan berturut-turut tanpa slow_client membaca antreannya
    for i in range(1, 6):
        frame = pb.ChatFrame(
            type=pb.FRAME_TYPE_MESSAGE,
            request_id=f"msg-{i}",
            sender="Publisher",
            content=f"Message {i}",
            timestamp=int(time.time() * 1000),
        )
        delivered = state.broadcast_frame(frame)
        assert delivered == 2  # Tetap terkirim ke kedua antrean

    # Antrean slow_client harus tetap berada pada batas kapasitasnya (3)
    assert slow_q.qsize() == 3

    # Pesan yang tersisa di antrean slow_client harus pesan terbaru (3, 4, 5) karena pesan 1 & 2 di-drop
    remaining_slow = []
    while not slow_q.empty():
        remaining_slow.append(slow_q.get_nowait().content)

    assert remaining_slow == ["Message 3", "Message 4", "Message 5"]
