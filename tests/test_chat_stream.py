"""Tests for Bidirectional Streaming RPC Chat."""

import queue
import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb


def test_chat_bidirectional_stream_join_and_message(test_stub):
    """Client membuka stream Chat, mengirim frame JOIN, dan menerima frame ACK."""
    stub, _, state = test_stub

    outgoing_q = queue.Queue()

    def request_generator():
        while True:
            item = outgoing_q.get()
            if item is None:
                break
            yield item

    # Membuka bidirectional stream
    stream = stub.Chat(request_generator())

    # 1. Kirim frame JOIN
    join_frame = pb.ChatFrame(
        type=pb.FRAME_TYPE_JOIN,
        request_id="rid-stream-join-1",
        sender="StreamUser1",
        content="Joining room",
        timestamp=int(time.time() * 1000),
    )
    outgoing_q.put(join_frame)

    # 2. Server harus membalas dengan frame ACK
    ack_frame = next(stream)
    assert ack_frame.type == pb.FRAME_TYPE_ACK
    assert "StreamUser1" in ack_frame.content

    # 3. Kirim frame HEARTBEAT
    hb_frame = pb.ChatFrame(
        type=pb.FRAME_TYPE_HEARTBEAT,
        request_id="rid-hb-1",
        sender="StreamUser1",
        content="PING",
        timestamp=int(time.time() * 1000),
    )
    outgoing_q.put(hb_frame)

    resp_hb = next(stream)
    assert resp_hb.type == pb.FRAME_TYPE_HEARTBEAT
    assert resp_hb.content == "PONG"

    # 4. Tutup stream
    outgoing_q.put(None)
