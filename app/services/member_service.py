from sqlalchemy.orm import Session

from app.core.exceptions import LastOwnerError, MemberNotFoundError
from app.models.budget_member import BudgetMember, BudgetRole
from app.repositories import budget_member_repository


def list_members(db: Session, budget_id: str) -> list[BudgetMember]:
    return budget_member_repository.list_members_for_budget(db, budget_id)


def _get_member_or_404(db: Session, budget_id: str, user_id: str) -> BudgetMember:
    member = budget_member_repository.get_membership(db, budget_id, user_id)
    if member is None:
        raise MemberNotFoundError()
    return member


def update_member_role(db: Session, budget_id: str, target_user_id: str, new_role: BudgetRole) -> BudgetMember:
    member = _get_member_or_404(db, budget_id, target_user_id)

    if member.role == BudgetRole.OWNER and new_role == BudgetRole.MEMBER:
        if budget_member_repository.count_owners(db, budget_id) <= 1:
            raise LastOwnerError()

    return budget_member_repository.update_role(db, member, new_role)


def remove_member(db: Session, budget_id: str, target_user_id: str) -> None:
    member = _get_member_or_404(db, budget_id, target_user_id)

    if member.role == BudgetRole.OWNER and budget_member_repository.count_owners(db, budget_id) <= 1:
        raise LastOwnerError()

    budget_member_repository.delete(db, member)