import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BudgetRole(str, enum.Enum):
    OWNER = "owner"
    MEMBER = "member"


class BudgetMember(Base):
    __tablename__ = "budget_members"
    __table_args__ = (
        UniqueConstraint("budget_id", "user_id", name="uq_budget_member_budget_user"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id: Mapped[str] = mapped_column(ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[BudgetRole] = mapped_column(
        Enum(BudgetRole, native_enum=False, length=20), default=BudgetRole.MEMBER, nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    budget: Mapped["Budget"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")