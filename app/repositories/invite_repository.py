from datetime import datetime

from sqlalchemy.orm import Session

from app.models.invite import Invite


def create(db: Session, budget_id: str, token: str, created_by: str, expires_at: datetime) -> Invite:
    invite = Invite(budget_id=budget_id, token=token, created_by=created_by, expires_at=expires_at)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


def get_by_token(db: Session, token: str) -> Invite | None:
    return db.query(Invite).filter(Invite.token == token).first()


def mark_used(db: Session, invite: Invite) -> Invite:
    invite.used = True
    db.commit()
    db.refresh(invite)
    return invite