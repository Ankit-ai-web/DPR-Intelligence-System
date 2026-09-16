from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(
        name=user_data.name,
        email=user_data.email,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_users(db: Session) -> list[User]:
    result = db.execute(
        select(User).order_by(User.id)
    )

    return list(result.scalars().all())