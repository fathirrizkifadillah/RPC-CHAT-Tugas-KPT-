"""Tests for Request ID Deduplication and Semantics in PROSES."""

import queue
import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb


def test_send_message_deduplication_via_proses(test_stub):
    """Pesan dengan request_id yang sama persis hanya di-broadcast SATU kali ke target client."""
    stub, _, state = test_stub

    # Buat antrean penerima tiruan untuk menghitung jumlah broadcast aktual
    q = state.register_stream_queue("listener-uid")

    req_id = "duplicate-test-id-123"
    req = pb.SendMessageRequest(
        request_id=req_id,
        sender_username="SenderAlice",
        content="Pesan penting yang di-retry",
        timestamp=int(time.time() * 1000),
    )

    # Pemanggilan Pertama
    resp1 = stub.SendMessage(req, timeout=3.0)
    assert resp1.success is True
    assert resp1.request_id == req_id

    # Pemanggilan Kedua (simulasi retry client dengan request_id sama)
    resp2 = stub.SendMessage(req, timeout=3.0)
    assert resp2.success is True
    assert resp2.request_id == req_id
    # Respons harus berasal dari cache PROSES (delivered_at sama)
    assert resp2.delivered_at == resp1.delivered_at

    # Buktikan bahwa pesan di antrean penerima HANYA ada 1, bukan 2!
    delivered_frame = q.get(timeout=1.0)
    assert delivered_frame.request_id == req_id
    assert delivered_frame.content == "Pesan penting yang di-retry"

    # Pastikan antrean sekarang kosong (tidak ada pesan duplikat)
    assert q.empty() is True, "Terdapat pesan duplikat di antrean penerima!"


def test_send_message_different_request_ids_broadcasts_twice(test_stub):
    """Pesan dengan request_id berbeda dibroadcast dua kali sesuai jumlah permintaan."""
    stub, _, state = test_stub
    q = state.register_stream_queue("listener-uid-2")

    req1 = pb.SendMessageRequest(
        request_id="distinct-id-1",
        sender_username="SenderBob",
        content="Pesan pertama",
        timestamp=int(time.time() * 1000),
    )
    req2 = pb.SendMessageRequest(
        request_id="distinct-id-2",
        sender_username="SenderBob",
        content="Pesan kedua",
        timestamp=int(time.time() * 1000),
    )

    stub.SendMessage(req1, timeout=3.0)
    stub.SendMessage(req2, timeout=3.0)

    # Harus ada tepat 2 pesan di antrean
    f1 = q.get(timeout=1.0)
    f2 = q.get(timeout=1.0)
    assert f1.request_id == "distinct-id-1"
    assert f2.request_id == "distinct-id-2"
    assert q.empty() is True
