from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.budget_member import BudgetMember, BudgetRole


def get_membership(db: Session, budget_id: str, user_id: str) -> BudgetMember | None:
    return (
        db.query(BudgetMember)
        .filter(BudgetMember.budget_id == budget_id, BudgetMember.user_id == user_id)
        .first()
    )


def create(db: Session, budget_id: str, user_id: str, role: BudgetRole) -> BudgetMember:
    member = BudgetMember(budget_id=budget_id, user_id=user_id, role=role)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def list_memberships_for_user(db: Session, user_id: str) -> list[BudgetMember]:
    """Повертає членства разом із уже завантаженим Budget, найновіші бюджети першими."""
    return (
        db.query(BudgetMember)
        .join(Budget)
        .filter(BudgetMember.user_id == user_id)
        .order_by(Budget.created_at.desc())
        .all()
    )

def list_members_for_budget(db: Session, budget_id: str) -> list[BudgetMember]:
    return (
        db.query(BudgetMember)
        .filter(BudgetMember.budget_id == budget_id)
        .order_by(BudgetMember.joined_at)
        .all()
    )


def count_owners(db: Session, budget_id: str) -> int:
    return (
        db.query(BudgetMember)
        .filter(BudgetMember.budget_id == budget_id, BudgetMember.role == BudgetRole.OWNER)
        .count()
    )


def update_role(db: Session, member: BudgetMember, role: BudgetRole) -> BudgetMember:
    member.role = role
    db.commit()
    db.refresh(member)
    return member


def delete(db: Session, member: BudgetMember) -> None:
    db.delete(member)
    db.commit()