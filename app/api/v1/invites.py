from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_budget_member, get_current_user
from app.db.session import get_db
from app.models.budget_member import BudgetMember, BudgetRole
from app.models.user import User
from app.schemas.invite import InviteAcceptOut, InviteOut, InvitePreview
from app.services import invite_service

budget_invites_router = APIRouter(prefix="/budgets/{budget_id}/invites", tags=["invites"])
invites_router = APIRouter(prefix="/invites", tags=["invites"])


@budget_invites_router.post("", response_model=InviteOut, status_code=status.HTTP_201_CREATED)
def create_invite(
    budget_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    return invite_service.create_invite(db, budget_id=budget_id, created_by=membership.user_id)


@invites_router.get("/{token}", response_model=InvitePreview)
def preview_invite(token: str, db: Session = Depends(get_db)):
    invite = invite_service.get_valid_invite(db, token)
    return InvitePreview(
        budget_id=invite.budget.id,
        budget_name=invite.budget.name,
        expires_at=invite.expires_at,
    )


@invites_router.post("/{token}/accept", response_model=InviteAcceptOut)
def accept_invite(token: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = invite_service.accept_invite(db, token, current_user.id)
    return InviteAcceptOut(budget_id=member.budget_id, role=member.role.value)