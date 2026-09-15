class AppError(Exception):
    status_code: int = 400
    code: str = "BAD_REQUEST"
    message: str = "Помилка запиту"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        if message:
            self.message = message


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"
    message = "Недійсний або протермінований токен"


class InvalidCredentialsError(AppError):
    status_code = 401
    code = "INVALID_CREDENTIALS"
    message = "Невірна пошта або пароль"


class EmailAlreadyExistsError(AppError):
    status_code = 409
    code = "EMAIL_ALREADY_EXISTS"
    message = "Цей email вже зареєстровано"


class BudgetNotFoundError(AppError):
    status_code = 404
    code = "BUDGET_NOT_FOUND"
    message = "Бюджет не знайдено"


class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    message = "Недостатньо прав для цієї дії"


class CategoryNotFoundError(AppError):
    status_code = 404
    code = "CATEGORY_NOT_FOUND"
    message = "Категорію не знайдено"


class CategoryNotInBudgetError(AppError):
    status_code = 400
    code = "CATEGORY_NOT_FOUND"
    message = "Категорія не належить цьому бюджету"


class InvalidCategoryLimitError(AppError):
    status_code = 400
    code = "INVALID_CATEGORY_LIMIT"
    message = "Ліміт не застосовується до категорій доходу"


class CategoryArchivedError(AppError):
    status_code = 400
    code = "CATEGORY_ARCHIVED"
    message = "Категорію архівовано"


class TransactionNotFoundError(AppError):
    status_code = 404
    code = "TRANSACTION_NOT_FOUND"
    message = "Транзакцію не знайдено"


class TransactionForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"
    message = "У вас немає прав для цієї дії з транзакцією"


class InvalidInviteTokenError(AppError):
    status_code = 400
    code = "INVALID_INVITE_TOKEN"
    message = "Посилання-запрошення недійсне або протерміноване"


class AlreadyMemberError(AppError):
    status_code = 409
    code = "ALREADY_MEMBER"
    message = "Ви вже є учасником цього бюджету"

class MemberNotFoundError(AppError):
    status_code = 404
    code = "MEMBER_NOT_FOUND"
    message = "Учасника не знайдено"


class LastOwnerError(AppError):
    status_code = 400
    code = "CANNOT_REMOVE_LAST_OWNER"
    message = "У бюджеті має залишитись хоча б один власник"