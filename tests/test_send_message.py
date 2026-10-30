"""Tests for Unary RPC SendMessage."""

import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb


def test_send_message_unary_success(test_stub):
    """Pengiriman pesan via jalur Unary SendMessage berhasil dan mengembalikan ACK."""
    stub, _, state = test_stub

    # Registrasi user penerima di stream queue untuk membuktikan pesan masuk ke antrean
    q = state.register_stream_queue("target-user-id")

    req = pb.SendMessageRequest(
        request_id="rid-msg-1",
        sender_username="Alice",
        content="Halo dari jalur Unary!",
        timestamp=int(time.time() * 1000),
    )
    resp = stub.SendMessage(req, timeout=3.0)

    assert resp.success is True
    assert resp.request_id == "rid-msg-1"
    assert resp.delivered_at > 0

    # Pastikan pesan ter-broadcast ke antrean penerima
    delivered_frame = q.get(timeout=1.0)
    assert delivered_frame.type == pb.FRAME_TYPE_MESSAGE
    assert delivered_frame.sender == "Alice"
    assert delivered_frame.content == "Halo dari jalur Unary!"


def test_send_message_invalid_payload_fails(test_stub):
    """Pesan dengan konten kosong atau sender kosong harus ditolak INVALID_ARGUMENT."""
    stub, _, _ = test_stub

    # Konten kosong
    req_empty_content = pb.SendMessageRequest(
        request_id="rid-err-1",
        sender_username="Alice",
        content="   ",
        timestamp=int(time.time() * 1000),
    )
    with pytest.raises(grpc.RpcError) as exc:
        stub.SendMessage(req_empty_content, timeout=3.0)
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    # Pengirim kosong
    req_empty_sender = pb.SendMessageRequest(
        request_id="rid-err-2",
        sender_username="",
        content="Halo dunia",
        timestamp=int(time.time() * 1000),
    )
    with pytest.raises(grpc.RpcError) as exc:
        stub.SendMessage(req_empty_sender, timeout=3.0)
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT
