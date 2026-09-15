from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.category import EntryType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: EntryType
    limit_amount: Decimal | None = Field(default=None, gt=0)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    limit_amount: Decimal | None = Field(default=None, gt=0)


class CategoryOut(BaseModel):
    id: str
    budget_id: str
    name: str
    type: EntryType
    limit_amount: Decimal | None
    is_archived: bool