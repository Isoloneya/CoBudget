from datetime import datetime

from pydantic import BaseModel


class InviteOut(BaseModel):
    id: str
    budget_id: str
    token: str
    expires_at: datetime
    used: bool

    model_config = {"from_attributes": True}


class InvitePreview(BaseModel):
    budget_id: str
    budget_name: str
    expires_at: datetime


class InviteAcceptOut(BaseModel):
    budget_id: str
    role: str