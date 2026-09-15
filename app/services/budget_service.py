from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.default_categories import DEFAULT_CATEGORIES
from app.models.budget import Budget
from app.models.budget_member import BudgetMember, BudgetRole
from app.models.category import EntryType
from app.models.user import User
from app.repositories import budget_member_repository, budget_repository, category_repository, transaction_repository
from app.schemas.budget import BudgetSummary, CategorySummary

WARNING_THRESHOLD = Decimal("0.9")


def create_budget(db: Session, user: User, name: str, description: str | None) -> Budget:
    budget = budget_repository.create(db, name=name, description=description)
    budget_member_repository.create(db, budget_id=budget.id, user_id=user.id, role=BudgetRole.OWNER)
    for category_name, category_type in DEFAULT_CATEGORIES:
        category_repository.create(db, budget_id=budget.id, name=category_name, type_=category_type, limit_amount=None)
    return budget


def list_user_budgets(db: Session, user: User) -> list[tuple[Budget, BudgetRole]]:
    memberships = budget_member_repository.list_memberships_for_user(db, user.id)
    return [(m.budget, m.role) for m in memberships]


def update_budget(db: Session, budget: Budget, name: str | None, description: str | None) -> Budget:
    return budget_repository.update(db, budget, name=name, description=description)


def delete_budget(db: Session, budget: Budget) -> None:
    budget_repository.delete(db, budget)


def _category_status(spent: Decimal, limit_amount: Decimal | None) -> str | None:
    if limit_amount is None:
        return None
    if spent > limit_amount:
        return "over"
    if spent >= limit_amount * WARNING_THRESHOLD:
        return "warning"
    return "ok"


def get_budget_summary(db: Session, budget_id: str) -> BudgetSummary:
    categories = category_repository.list_for_budget(db, budget_id)
    spent_by_category = transaction_repository.sum_by_category(db, budget_id)
    totals_by_type = transaction_repository.sum_by_type(db, budget_id)

    income_total = totals_by_type.get(EntryType.INCOME, Decimal("0"))
    expense_total = totals_by_type.get(EntryType.EXPENSE, Decimal("0"))

    category_summaries = [
        CategorySummary(
            id=category.id,
            name=category.name,
            type=category.type.value,
            limit_amount=category.limit_amount,
            spent=spent_by_category.get(category.id, Decimal("0")),
            status=_category_status(spent_by_category.get(category.id, Decimal("0")), category.limit_amount),
        )
        for category in categories
    ]

    return BudgetSummary(
        budget_id=budget_id,
        income_total=income_total,
        expense_total=expense_total,
        balance=income_total - expense_total,
        categories=category_summaries,
    )