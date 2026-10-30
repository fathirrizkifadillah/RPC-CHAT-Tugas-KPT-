"""Tests for Concurrency and Shared State Thread-Safety under Multi-Client Load."""

from concurrent import futures
import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb
from chat_room.client import ChatClient


def test_concurrent_user_registrations_and_messages(test_server):
    """20 client secara bersamaan melakukan Join, ListUsers, dan SendMessage tanpa race condition."""
    _, address, state = test_server
    num_clients = 20

    def worker_task(index: int):
        username = f"ConcurrentUser_{index:02d}"
        client = ChatClient(server_address=address, username=username)
        try:
            # 1. Join
            join_resp = client.join_with_retry()
            assert join_resp.success is True

            # 2. List Users
            users = client.list_users_with_retry()
            assert len(users) >= 1

            # 3. Send Unary Message
            msg_resp = client.send_message_unary_with_retry(f"Pesan konkuren dari {username}")
            assert msg_resp.success is True

            return True
        finally:
            client.close()

    # Jalankan 20 thread secara bersamaan
    with futures.ThreadPoolExecutor(max_workers=num_clients) as executor:
        results = list(executor.map(worker_task, range(num_clients)))

    assert all(results)
    assert len(results) == num_clients

    # Verifikasi konsistensi shared state server
    active_users = state.get_active_users()
    # Semua 20 user harus terdaftar dengan benar
    assert len(active_users) == num_clients
    usernames = {u.username for u in active_users}
    for i in range(num_clients):
        assert f"ConcurrentUser_{i:02d}" in usernames
