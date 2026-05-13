import enum
from datetime import datetime
from sqlalchemy import (
    String,
    func,
    ForeignKey
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from database import Base

class OperationType(enum.Enum):
    INCOME = 'пополнение'
    EXPENSE = 'снятие'

class Transaction(Base):
    __tablename__='transactions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    summa: Mapped[float]
    operation_type: Mapped[OperationType]
    date: Mapped[datetime] = mapped_column(server_default=func.now())
    category: Mapped[str] = mapped_column(default='другое')
    purpose: Mapped[str] = mapped_column(default='на мечту')
    limits: Mapped[float] = mapped_column(default=0.0)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'))