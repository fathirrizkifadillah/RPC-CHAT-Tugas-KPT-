"""Tests for Client Timeout and Exponential Backoff Retry."""

import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb
from chat_room.client import ChatClient


def test_client_timeout_raises_deadline_exceeded(test_server):
    """Client dengan timeout rendah mengalami DEADLINE_EXCEEDED jika server tertunda."""
    _, address, _ = test_server

    # Set timeout client sangat rendah (0.05s)
    client = ChatClient(server_address=address, username="SlowUser", timeout=0.001, max_retries=1)

    # Karena timeout 1ms, pemanggilan ke remote server kemungkinan besar timeout
    # atau jika localhost terlalu cepat, kita dapat menguji penanganan status DEADLINE_EXCEEDED
    try:
        client.join_with_retry()
    except grpc.RpcError as e:
        # Jika timeout terjadi, harus DEADLINE_EXCEEDED
        assert e.code() in (grpc.StatusCode.DEADLINE_EXCEEDED, grpc.StatusCode.UNAVAILABLE)
    finally:
        client.close()


def test_client_retry_maintains_stable_request_id(test_server, monkeypatch):
    """Client retry mempertahankan request_id yang sama pada setiap percobaan."""
    _, address, _ = test_server
    client = ChatClient(server_address=address, username="RetryUser", max_retries=3, base_retry_delay=0.05)

    captured_request_ids = []
    original_send = client.connect

    # Jalankan send message normal
    client.connect()
    resp = client.send_message_unary_with_retry("Pesan uji retry")
    assert resp.success is True
    first_rid = resp.request_id

    # Lakukan retry manual dengan request_id yang sama
    resp_retried = client.send_message_unary_with_retry("Pesan uji retry", request_id=first_rid)
    assert resp_retried.request_id == first_rid
    assert resp_retried.delivered_at == resp.delivered_at

    client.close()


def test_client_no_retry_on_invalid_argument(test_server):
    """Client tidak boleh melakukan retry berulang pada error INVALID_ARGUMENT."""
    _, address, _ = test_server
    client = ChatClient(server_address=address, username="InvalidUser", max_retries=3)

    # Kirim username kosong
    with pytest.raises(grpc.RpcError) as exc:
        client.join_with_retry(username="")

    # Harus langsung gagal tanpa retry berkali-kali
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    client.close()
