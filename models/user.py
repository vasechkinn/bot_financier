from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    login: Mapped[str | None] = mapped_column(String(256))
    password: Mapped[str | None] = mapped_column(String(256))
