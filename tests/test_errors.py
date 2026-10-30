"""Tests for Invalid Inputs and Error Status Handling across RPCs."""

import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb


def test_join_whitespace_only_username(test_stub):
    """Username hanya spasi harus ditolak dengan INVALID_ARGUMENT."""
    stub, _, _ = test_stub
    with pytest.raises(grpc.RpcError) as exc:
        stub.Join(pb.JoinRequest(username="     ", request_id="rid-space"), timeout=2.0)
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert "tidak boleh kosong" in exc.value.details()


def test_send_message_empty_content_and_sender(test_stub):
    """SendMessage dengan pengirim dan konten kosong harus ditolak INVALID_ARGUMENT."""
    stub, _, _ = test_stub

    # Konten kosong
    with pytest.raises(grpc.RpcError) as exc1:
        stub.SendMessage(
            pb.SendMessageRequest(sender_username="ValidUser", content=""), timeout=2.0
        )
    assert exc1.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    # Pengirim kosong
    with pytest.raises(grpc.RpcError) as exc2:
        stub.SendMessage(
            pb.SendMessageRequest(sender_username="", content="Valid content"), timeout=2.0
        )
    assert exc2.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_stream_join_with_invalid_username_emits_error_frame(test_stub):
    """Stream Chat yang mencoba join dengan username kosong menerima frame ERROR."""
    stub, _, _ = test_stub

    def frame_gen():
        yield pb.ChatFrame(
            type=pb.FRAME_TYPE_JOIN,
            sender="",  # Invalid empty username
            content="Join invalid",
            timestamp=int(time.time() * 1000),
        )

    responses = stub.Chat(frame_gen())
    first_frame = next(responses)
    assert first_frame.type == pb.FRAME_TYPE_ERROR
    assert "Registrasi gagal" in first_frame.content
