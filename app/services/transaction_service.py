from datetime import date as date_type
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import CategoryArchivedError, CategoryNotInBudgetError, TransactionForbiddenError
from app.models.budget_member import BudgetRole
from app.models.category import EntryType
from app.models.transaction import Transaction
from app.repositories import category_repository, transaction_repository


def _resolve_category(db: Session, budget_id: str, category_id: str):
    category = category_repository.get_by_id(db, category_id)
    if category is None or category.budget_id != budget_id:
        raise CategoryNotInBudgetError()
    if category.is_archived:
        raise CategoryArchivedError()
    return category


def create_transaction(
    db: Session,
    budget_id: str,
    user_id: str,
    category_id: str,
    amount: Decimal,
    txn_date: date_type,
    comment: str | None,
) -> Transaction:
    category = _resolve_category(db, budget_id, category_id)
    return transaction_repository.create(
        db,
        budget_id=budget_id,
        category_id=category_id,
        user_id=user_id,
        amount=amount,
        type_=category.type,
        txn_date=txn_date,
        comment=comment,
    )


def list_transactions(db: Session, budget_id: str, **filters):
    return transaction_repository.list_for_budget(db, budget_id, **filters)


def _can_modify(transaction: Transaction, current_user_id: str, role: BudgetRole) -> bool:
    return transaction.user_id == current_user_id or role == BudgetRole.OWNER


def update_transaction(
    db: Session,
    transaction: Transaction,
    current_user_id: str,
    role: BudgetRole,
    amount: Decimal | None,
    category_id: str | None,
    txn_date: date_type | None,
    comment: str | None,
) -> Transaction:
    if not _can_modify(transaction, current_user_id, role):
        raise TransactionForbiddenError("У вас немає прав редагувати цю транзакцію")

    type_: EntryType | None = None
    if category_id is not None:
        category = _resolve_category(db, transaction.budget_id, category_id)
        type_ = category.type

    return transaction_repository.update(
        db,
        transaction,
        amount=amount,
        category_id=category_id,
        type=type_,
        txn_date=txn_date,
        comment=comment,
    )


def delete_transaction(db: Session, transaction: Transaction, current_user_id: str, role: BudgetRole) -> None:
    if not _can_modify(transaction, current_user_id, role):
        raise TransactionForbiddenError("У вас немає прав видаляти цю транзакцію")
    transaction_repository.delete(db, transaction)