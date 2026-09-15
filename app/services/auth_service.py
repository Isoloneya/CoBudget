from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository


def register_user(db: Session, email: str, password: str) -> User:
    if user_repository.get_by_email(db, email):
        raise EmailAlreadyExistsError()
    return user_repository.create(db, email=email, password_hash=hash_password(password))


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repository.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError()
    return user


def issue_token_for(user: User) -> str:
    return create_access_token(subject=user.id)