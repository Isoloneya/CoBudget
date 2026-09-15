from app.models.category import EntryType

DEFAULT_CATEGORIES: list[tuple[str, EntryType]] = [
    ("Продукти", EntryType.EXPENSE),
    ("Комунальні", EntryType.EXPENSE),
    ("Транспорт", EntryType.EXPENSE),
    ("Розваги", EntryType.EXPENSE),
    ("Здоров'я", EntryType.EXPENSE),
    ("Одяг", EntryType.EXPENSE),
    ("Освіта", EntryType.EXPENSE),
    ("Інше", EntryType.EXPENSE),
    ("Зарплата", EntryType.INCOME),
    ("Інший дохід", EntryType.INCOME),
]