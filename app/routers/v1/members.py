from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.routers.deps import get_budget_member
from app.db.session import get_db
from app.models.budget_member import BudgetMember, BudgetRole
from app.schemas.member import MemberOut, MemberRoleUpdate
from app.services import member_service

router = APIRouter(prefix="/budgets/{budget_id}/members", tags=["members"])


def _to_out(member: BudgetMember) -> MemberOut:
    return MemberOut(user_id=member.user_id, email=member.user.email, role=member.role, joined_at=member.joined_at)


@router.get("", response_model=list[MemberOut])
def list_members(
    budget_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    members = member_service.list_members(db, budget_id)
    return [_to_out(m) for m in members]


@router.patch("/{user_id}", response_model=MemberOut)
def update_member_role(
    budget_id: str,
    user_id: str,
    payload: MemberRoleUpdate,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    member = member_service.update_member_role(db, budget_id, user_id, payload.role)
    return _to_out(member)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    budget_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    member_service.remove_member(db, budget_id, user_id)