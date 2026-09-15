from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.category import EntryType


class TransactionCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    category_id: str
    txn_date: date_type
    comment: str | None = Field(default=None, max_length=255)

    @field_validator("txn_date")
    @classmethod
    def not_in_future(cls, value: date_type) -> date_type:
        if value > date_type.today():
            raise ValueError("Дата транзакції не може бути в майбутньому")
        return value


class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    category_id: str | None = None
    txn_date: date_type | None = None
    comment: str | None = Field(default=None, max_length=255)

    @field_validator("txn_date")
    @classmethod
    def not_in_future(cls, value: date_type | None) -> date_type | None:
        if value is not None and value > date_type.today():
            raise ValueError("Дата транзакції не може бути в майбутньому")
        return value


class TransactionOut(BaseModel):
    id: str
    budget_id: str
    category_id: str
    user_id: str
    amount: Decimal
    type: EntryType
    txn_date: date_type
    comment: str | None

    model_config = {"from_attributes": True}


class TransactionPage(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    page_size: int