from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import BudgetNotFoundError, ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.budget_member import BudgetMember, BudgetRole
from app.models.user import User
from app.repositories import budget_member_repository, budget_repository, user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        user_id = decode_access_token(token)
    except JWTError:
        raise UnauthorizedError()

    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError()
    return user


def get_budget_member(required_role: BudgetRole | None = None):
    def dependency(
        budget_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> BudgetMember:
        budget = budget_repository.get_by_id(db, budget_id)
        if budget is None:
            raise BudgetNotFoundError()

        membership = budget_member_repository.get_membership(db, budget_id, current_user.id)
        if membership is None:
            raise ForbiddenError("Ви не є учасником цього бюджету")

        if required_role is not None and membership.role != required_role:
            raise ForbiddenError()

        return membership

    return dependency