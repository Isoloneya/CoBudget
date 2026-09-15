from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models. Alembic uses Base.metadata for migrations."""
    pass

# Models are imported here so that Alembic's autogenerate can discover them
# through Base.metadata once each model module is created.
# from app.models.user import User
# from app.models.budget import Budget
# from app.models.budget_member import BudgetMember
# from app.models.category import Category
# from app.models.transaction import Transaction
# from app.models.invite import Invite
