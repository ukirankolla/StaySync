"""In-memory WebSocket connection manager for real-time chat.

Each accepted connection is associated with a user id. When a message is persisted,
it is pushed to the connected peers. In production this should be swapped for a
Redis pub/sub layer so multiple workers stay in sync; the interface stays the same.
"""

from __future__ import annotations

from fastapi import WebSocket


class ChatManager:
    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, payload: dict) -> None:
        for ws in self._connections.get(user_id, []):
            try:
                await ws.send_json(payload)
            except Exception:
                pass

    def online_ids(self) -> list[int]:
        return list(self._connections.keys())


chat_manager = ChatManager()
