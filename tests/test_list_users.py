"""Tests for RPC ListUsers."""

import grpc
import pytest

from chat_room import chat_room_pb2 as pb


def test_list_users_initially_empty(test_stub):
    """Saat server baru mulai, ListUsers harus mengembalikan daftar kosong."""
    stub, _, _ = test_stub
    req = pb.ListUsersRequest(request_id="rid-list-0")
    resp = stub.ListUsers(req, timeout=3.0)

    assert resp.success is True
    assert resp.total_users == 0
    assert len(resp.users) == 0


def test_list_users_multiple_registered(test_stub):
    """Daftar pengguna aktif mencerminkan seluruh pengguna yang berhasil bergabung."""
    stub, _, _ = test_stub

    # Tambahkan 3 pengguna
    usernames = ["UserA", "UserB", "UserC"]
    for u in usernames:
        stub.Join(pb.JoinRequest(username=u, client_id=f"c-{u}", request_id=f"rid-{u}"), timeout=3.0)

    resp = stub.ListUsers(pb.ListUsersRequest(request_id="rid-list-all"), timeout=3.0)
    assert resp.success is True
    assert resp.total_users == 3
    retrieved_names = [user.username for user in resp.users]
    for u in usernames:
        assert u in retrieved_names
