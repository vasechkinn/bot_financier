from datetime import datetime
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Goal(Base):
    __tablename__ = 'goals'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    summa: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    completion_status: Mapped[bool] = mapped_column(default=False)
    completion_at: Mapped[datetime | None] = mapped_column(default=None)