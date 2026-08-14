from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import SessionLocal, get_db
from ..deps import get_current_user
from ..models import Block, Connection, Message, User
from ..schemas import MessageCreate, MessageOut
from ..security import decode_token
from ..services.chat_manager import chat_manager
from ..services.events import track

router = APIRouter(prefix="/chat", tags=["chat"])


def _blocked_set(db: Session, user_id: int) -> set[int]:
    rows = db.query(Block.blocked_id).filter(Block.blocker_id == user_id).all()
    rows2 = db.query(Block.blocker_id).filter(Block.blocked_id == user_id).all()
    return {r[0] for r in rows} | {r[0] for r in rows2}


@router.get("/connections/{connection_id}/messages", response_model=list[MessageOut])
def list_messages(connection_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conn = db.get(Connection, connection_id)
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    if conn.requester_id != user.id and conn.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Not part of this conversation")
    msgs = db.query(Message).filter(Message.connection_id == connection_id).order_by(Message.created_at.asc()).all()
    for m in msgs:
        if m.sender_id != user.id:
            m.is_read = True
    db.commit()
    return msgs


@router.post("/connections/{connection_id}/messages", response_model=MessageOut)
async def send_message(connection_id: int, payload: MessageCreate, user: User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    conn = db.get(Connection, connection_id)
    if not conn or conn.status != "accepted":
        raise HTTPException(status_code=400, detail="Connect with the user first")
    if conn.requester_id != user.id and conn.recipient_id != user.id:
        raise HTTPException(status_code=403, detail="Not part of this conversation")

    peer_id = conn.requester_id if conn.recipient_id == user.id else conn.recipient_id
    if peer_id in _blocked_set(db, user.id):
        raise HTTPException(status_code=403, detail="Cannot message this user")

    msg = Message(connection_id=connection_id, sender_id=user.id, content=payload.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    from fastapi.encoders import jsonable_encoder
    await chat_manager.send_to_user(peer_id, {
        "type": "message",
        "data": jsonable_encoder(MessageOut.model_validate(msg)),
    })
    track(db, user.id, "message_sent", {"connection_id": connection_id})
    return msg


@router.websocket("/ws")
async def chat_ws(ws: WebSocket, token: str = Query("")):
    payload = decode_token(token) if token else None
    if not payload:
        await ws.close(code=4401)
        return
    user_id = int(payload.get("sub"))
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user or user.is_suspended or not user.is_active:
            await ws.close(code=4403)
            return
        await chat_manager.connect(user_id, ws)
        await chat_manager.send_to_user(user_id, {"type": "presence", "data": {"online": chat_manager.online_ids()}})
        try:
            while True:
                raw = await ws.receive_json()
                msg_type = raw.get("type")
                if msg_type == "ping":
                    await ws.send_json({"type": "pong"})
        except WebSocketDisconnect:
            pass
    finally:
        chat_manager.disconnect(user_id, ws)
        db.close()
