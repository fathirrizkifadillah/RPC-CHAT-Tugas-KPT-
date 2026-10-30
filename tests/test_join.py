"""Tests for RPC Join."""

import grpc
import pytest

from chat_room import chat_room_pb2 as pb


def test_join_success(test_stub):
    """Pengguna baru berhasil bergabung dan menerima user_id."""
    stub, _, state = test_stub
    req = pb.JoinRequest(username="Alice", client_id="c-alice-1", request_id="rid-1")
    resp = stub.Join(req, timeout=3.0)

    assert resp.success is True
    assert "Alice" in resp.message
    assert len(resp.user_id) > 0
    assert resp.joined_at > 0

    # Pastikan user terdaftar di shared state
    users = state.get_active_users()
    assert len(users) == 1
    assert users[0].username == "Alice"


def test_join_empty_username_fails(test_stub):
    """Join dengan username kosong harus melempar status INVALID_ARGUMENT."""
    stub, _, _ = test_stub
    req = pb.JoinRequest(username="   ", client_id="c-invalid", request_id="rid-empty")

    with pytest.raises(grpc.RpcError) as exc_info:
        stub.Join(req, timeout=3.0)

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT


def test_join_duplicate_username_fails(test_stub):
    """Username yang sama jika didaftarkan oleh client_id berbeda harus ditolak ALREADY_EXISTS."""
    stub, _, _ = test_stub
    req1 = pb.JoinRequest(username="Bob", client_id="client-bob-1", request_id="rid-bob-1")
    resp1 = stub.Join(req1, timeout=3.0)
    assert resp1.success is True

    req2 = pb.JoinRequest(username="Bob", client_id="client-bob-2", request_id="rid-bob-2")
    with pytest.raises(grpc.RpcError) as exc_info:
        stub.Join(req2, timeout=3.0)

    assert exc_info.value.code() == grpc.StatusCode.ALREADY_EXISTS


def test_join_idempotent_reconnect(test_stub):
    """Client_id yang sama dengan username sama diperlakukan idempoten / reconnect."""
    stub, _, _ = test_stub
    req = pb.JoinRequest(username="Charlie", client_id="c-charlie", request_id="rid-c1")
    resp1 = stub.Join(req, timeout=3.0)
    assert resp1.success is True

    # Reconnect dengan client_id sama
    req_reconnect = pb.JoinRequest(username="Charlie", client_id="c-charlie", request_id="rid-c2")
    resp2 = stub.Join(req_reconnect, timeout=3.0)
    assert resp2.success is True
    assert resp2.user_id == resp1.user_id
