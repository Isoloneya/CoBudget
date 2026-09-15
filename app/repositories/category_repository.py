from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.category import Category, EntryType


def create(db: Session, budget_id: str, name: str, type_: EntryType, limit_amount: Decimal | None) -> Category:
    category = Category(budget_id=budget_id, name=name, type=type_, limit_amount=limit_amount)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_by_id(db: Session, category_id: str) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def list_for_budget(db: Session, budget_id: str, include_archived: bool = False) -> list[Category]:
    query = db.query(Category).filter(Category.budget_id == budget_id)
    if not include_archived:
        query = query.filter(Category.is_archived.is_(False))
    return query.order_by(Category.name).all()


def update(db: Session, category: Category, name: str | None, limit_amount: Decimal | None) -> Category:
    if name is not None:
        category.name = name
    if limit_amount is not None:
        category.limit_amount = limit_amount
    db.commit()
    db.refresh(category)
    return category


def archive(db: Session, category: Category) -> Category:
    category.is_archived = True
    db.commit()
    db.refresh(category)
    return category