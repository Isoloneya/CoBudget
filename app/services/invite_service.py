import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AlreadyMemberError, InvalidInviteTokenError
from app.models.budget_member import BudgetMember, BudgetRole
from app.models.invite import Invite
from app.repositories import budget_member_repository, invite_repository


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def create_invite(db: Session, budget_id: str, created_by: str) -> Invite:
    token = secrets.token_urlsafe(24)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.INVITE_TOKEN_EXPIRE_DAYS)
    return invite_repository.create(db, budget_id=budget_id, token=token, created_by=created_by, expires_at=expires_at)


def get_valid_invite(db: Session, token: str) -> Invite:
    invite = invite_repository.get_by_token(db, token)
    if invite is None or invite.used:
        raise InvalidInviteTokenError()
    if _as_utc(invite.expires_at) < datetime.now(timezone.utc):
        raise InvalidInviteTokenError()
    return invite


def accept_invite(db: Session, token: str, user_id: str) -> BudgetMember:
    invite = get_valid_invite(db, token)

    if budget_member_repository.get_membership(db, invite.budget_id, user_id):
        raise AlreadyMemberError()

    member = budget_member_repository.create(db, budget_id=invite.budget_id, user_id=user_id, role=BudgetRole.MEMBER)
    invite_repository.mark_used(db, invite)
    return member