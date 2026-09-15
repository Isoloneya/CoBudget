from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class BudgetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class BudgetOut(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    role: str


class CategorySummary(BaseModel):
    id: str
    name: str
    type: str
    limit_amount: Decimal | None
    spent: Decimal
    status: str | None


class BudgetSummary(BaseModel):
    budget_id: str
    income_total: Decimal
    expense_total: Decimal
    balance: Decimal
    categories: list[CategorySummary]