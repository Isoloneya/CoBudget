from datetime import date as date_type
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import EntryType
from app.models.transaction import Transaction


def create(
    db: Session,
    budget_id: str,
    category_id: str,
    user_id: str,
    amount: Decimal,
    type_: EntryType,
    txn_date: date_type,
    comment: str | None,
) -> Transaction:
    transaction = Transaction(
        budget_id=budget_id,
        category_id=category_id,
        user_id=user_id,
        amount=amount,
        type=type_,
        txn_date=txn_date,
        comment=comment,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_by_id(db: Session, transaction_id: str) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def list_for_budget(
    db: Session,
    budget_id: str,
    category_id: str | None = None,
    type_: EntryType | None = None,
    date_from: date_type | None = None,
    date_to: date_type | None = None,
    author_id: str | None = None,
    search: str | None = None,
    sort_by: str = "txn_date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Transaction], int]:
    query = db.query(Transaction).filter(Transaction.budget_id == budget_id)

    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if type_:
        query = query.filter(Transaction.type == type_)
    if date_from:
        query = query.filter(Transaction.txn_date >= date_from)
    if date_to:
        query = query.filter(Transaction.txn_date <= date_to)
    if author_id:
        query = query.filter(Transaction.user_id == author_id)
    if search:
        query = query.filter(Transaction.comment.ilike(f"%{search}%"))

    total = query.with_entities(func.count(Transaction.id)).scalar()

    sort_column = {"txn_date": Transaction.txn_date, "amount": Transaction.amount}.get(
        sort_by, Transaction.txn_date
    )
    sort_column = sort_column.desc() if order == "desc" else sort_column.asc()
    query = query.order_by(sort_column)

    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def update(db: Session, transaction: Transaction, **fields) -> Transaction:
    for key, value in fields.items():
        if value is not None:
            setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()


def sum_by_category(db: Session, budget_id: str) -> dict[str, Decimal]:
    rows = (
        db.query(Transaction.category_id, func.sum(Transaction.amount))
        .filter(Transaction.budget_id == budget_id)
        .group_by(Transaction.category_id)
        .all()
    )
    return {category_id: total for category_id, total in rows}


def sum_by_type(db: Session, budget_id: str) -> dict[EntryType, Decimal]:
    rows = (
        db.query(Transaction.type, func.sum(Transaction.amount))
        .filter(Transaction.budget_id == budget_id)
        .group_by(Transaction.type)
        .all()
    )
    return {type_: total for type_, total in rows}