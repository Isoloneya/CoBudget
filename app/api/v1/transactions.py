from datetime import date as date_type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_budget_member
from app.core.exceptions import TransactionNotFoundError
from app.db.session import get_db
from app.models.budget_member import BudgetMember
from app.models.category import EntryType
from app.repositories import transaction_repository
from app.schemas.transaction import TransactionCreate, TransactionOut, TransactionPage, TransactionUpdate
from app.services import transaction_service

router = APIRouter(prefix="/budgets/{budget_id}/transactions", tags=["transactions"])


def _get_transaction_in_budget(db: Session, budget_id: str, transaction_id: str):
    transaction = transaction_repository.get_by_id(db, transaction_id)
    if transaction is None or transaction.budget_id != budget_id:
        raise TransactionNotFoundError()
    return transaction


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    budget_id: str,
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    return transaction_service.create_transaction(
        db,
        budget_id=budget_id,
        user_id=membership.user_id,
        category_id=payload.category_id,
        amount=payload.amount,
        txn_date=payload.txn_date,
        comment=payload.comment,
    )


@router.get("", response_model=TransactionPage)
def list_transactions(
    budget_id: str,
    category_id: str | None = None,
    type: EntryType | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
    author_id: str | None = None,
    search: str | None = None,
    sort_by: str = Query(default="txn_date", pattern="^(txn_date|amount)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    items, total = transaction_service.list_transactions(
        db,
        budget_id,
        category_id=category_id,
        type_=type,
        date_from=date_from,
        date_to=date_to,
        author_id=author_id,
        search=search,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )
    return TransactionPage(items=items, total=total, page=page, page_size=page_size)


@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    budget_id: str,
    transaction_id: str,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    transaction = _get_transaction_in_budget(db, budget_id, transaction_id)
    return transaction_service.update_transaction(
        db,
        transaction,
        current_user_id=membership.user_id,
        role=membership.role,
        amount=payload.amount,
        category_id=payload.category_id,
        txn_date=payload.txn_date,
        comment=payload.comment,
    )


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    budget_id: str,
    transaction_id: str,
    db: Session = Depends(get_db),
    membership: BudgetMember = Depends(get_budget_member()),
):
    transaction = _get_transaction_in_budget(db, budget_id, transaction_id)
    transaction_service.delete_transaction(db, transaction, current_user_id=membership.user_id, role=membership.role)