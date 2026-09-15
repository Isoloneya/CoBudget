from sqlalchemy.orm import Session

from app.models.budget import Budget


def create(db: Session, name: str, description: str | None) -> Budget:
    budget = Budget(name=name, description=description)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def get_by_id(db: Session, budget_id: str) -> Budget | None:
    return db.query(Budget).filter(Budget.id == budget_id).first()


def update(db: Session, budget: Budget, name: str | None, description: str | None) -> Budget:
    if name is not None:
        budget.name = name
    if description is not None:
        budget.description = description
    db.commit()
    db.refresh(budget)
    return budget


def delete(db: Session, budget: Budget) -> None:
    db.delete(budget)
    db.commit()