from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_budget_member, get_current_user
from app.db.session import get_db
from app.models.budget_member import BudgetMember, BudgetRole
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetOut, BudgetSummary, BudgetUpdate
from app.services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = budget_service.create_budget(db, current_user, payload.name, payload.description)
    return BudgetOut(
        id=budget.id,
        name=budget.name,
        description=budget.description,
        created_at=budget.created_at,
        role=BudgetRole.OWNER.value,
    )


@router.get("", response_model=list[BudgetOut])
def list_budgets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    pairs = budget_service.list_user_budgets(db, current_user)
    return [
        BudgetOut(
            id=budget.id,
            name=budget.name,
            description=budget.description,
            created_at=budget.created_at,
            role=role.value,
        )
        for budget, role in pairs
    ]


@router.get("/{budget_id}", response_model=BudgetOut)
def get_budget(membership: BudgetMember = Depends(get_budget_member())):
    budget = membership.budget
    return BudgetOut(
        id=budget.id,
        name=budget.name,
        description=budget.description,
        created_at=budget.created_at,
        role=membership.role.value,
    )


@router.get("/{budget_id}/summary", response_model=BudgetSummary)
def get_budget_summary(
    budget_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    return budget_service.get_budget_summary(db, budget_id)


@router.patch("/{budget_id}", response_model=BudgetOut)
def update_budget(
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    budget = budget_service.update_budget(db, membership.budget, payload.name, payload.description)
    return BudgetOut(
        id=budget.id,
        name=budget.name,
        description=budget.description,
        created_at=budget.created_at,
        role=membership.role.value,
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    budget_service.delete_budget(db, membership.budget)