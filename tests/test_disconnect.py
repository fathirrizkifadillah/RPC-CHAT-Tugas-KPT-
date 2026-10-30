"""Tests for Client Disconnection and Session Cleanup."""

import threading
import time
import grpc
import pytest

from chat_room import chat_room_pb2 as pb
from chat_room.client import ChatClient


def test_disconnect_removes_user_and_broadcasts_leave_event(test_server):
    """Saat client terputus atau keluar, user dihapus dari daftar aktif dan event leave dibroadcast."""
    _, address, state = test_server

    client_watcher = ChatClient(server_address=address, username="Watcher")
    client_leaver = ChatClient(server_address=address, username="Leaver")

    leave_event_received = threading.Event()

    def on_watcher_message(frame: pb.ChatFrame):
        if frame.type == pb.FRAME_TYPE_USER_EVENT and "Leaver" in frame.content and "keluar" in frame.content:
            leave_event_received.set()

    try:
        client_watcher.join_with_retry()
        client_watcher.start_chat_stream(on_message_callback=on_watcher_message)

        client_leaver.join_with_retry()
        client_leaver.start_chat_stream()

        time.sleep(0.3)

        # Pastikan kedua user terdaftar
        users_before = client_watcher.list_users_with_retry()
        names_before = [u.username for u in users_before]
        assert "Watcher" in names_before
        assert "Leaver" in names_before

        # Leaver memutuskan koneksi (close)
        client_leaver.close()

        # Watcher harus menerima notifikasi leave event
        event_ok = leave_event_received.wait(timeout=3.0)
        assert event_ok is True, "Watcher tidak menerima event bahwa Leaver telah keluar"

        # Pastikan Leaver tidak lagi ada di ListUsers
        time.sleep(0.3)
        users_after = client_watcher.list_users_with_retry()
        names_after = [u.username for u in users_after]
        assert "Leaver" not in names_after
        assert "Watcher" in names_after

    finally:
        client_watcher.close()
        client_leaver.close()
