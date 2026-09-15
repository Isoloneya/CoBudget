from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCategoryLimitError
from app.models.category import Category, EntryType
from app.repositories import category_repository


def create_category(
    db: Session, budget_id: str, name: str, type_: EntryType, limit_amount: Decimal | None
) -> Category:
    if limit_amount is not None and type_ == EntryType.INCOME:
        raise InvalidCategoryLimitError()
    return category_repository.create(db, budget_id=budget_id, name=name, type_=type_, limit_amount=limit_amount)


def list_categories(db: Session, budget_id: str) -> list[Category]:
    return category_repository.list_for_budget(db, budget_id)


def update_category(
    db: Session, category: Category, name: str | None, limit_amount: Decimal | None
) -> Category:
    if limit_amount is not None and category.type == EntryType.INCOME:
        raise InvalidCategoryLimitError()
    return category_repository.update(db, category, name=name, limit_amount=limit_amount)


def archive_category(db: Session, category: Category) -> Category:
    return category_repository.archive(db, category)