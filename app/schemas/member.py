from datetime import datetime

from pydantic import BaseModel

from app.models.budget_member import BudgetRole


class MemberOut(BaseModel):
    user_id: str
    email: str
    role: BudgetRole
    joined_at: datetime


class MemberRoleUpdate(BaseModel):
    role: BudgetRole