from sqlalchemy.orm import Session

from ..models import Event


def track(db: Session, user_id: int | None, event_type: str, payload: dict | None = None) -> None:
    db.add(Event(user_id=user_id, event_type=event_type, payload=payload or {}))
    db.commit()
