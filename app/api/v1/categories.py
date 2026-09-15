from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_budget_member
from app.core.exceptions import CategoryNotFoundError
from app.db.session import get_db
from app.models.budget_member import BudgetMember, BudgetRole
from app.repositories import category_repository
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/budgets/{budget_id}/categories", tags=["categories"])


def _get_category_in_budget(db: Session, budget_id: str, category_id: str):
    category = category_repository.get_by_id(db, category_id)
    if category is None or category.budget_id != budget_id:
        raise CategoryNotFoundError()
    return category


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    budget_id: str,
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    return category_service.create_category(
        db, budget_id=budget_id, name=payload.name, type_=payload.type, limit_amount=payload.limit_amount
    )


@router.get("", response_model=list[CategoryOut])
def list_categories(
    budget_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    return category_service.list_categories(db, budget_id)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    budget_id: str,
    category_id: str,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    category = _get_category_in_budget(db, budget_id, category_id)
    return category_service.update_category(db, category, name=payload.name, limit_amount=payload.limit_amount)


@router.delete("/{category_id}", response_model=CategoryOut)
def archive_category(
    budget_id: str,
    category_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member(required_role=BudgetRole.OWNER)),
):
    category = _get_category_in_budget(db, budget_id, category_id)
    return category_service.archive_category(db, category)