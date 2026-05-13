from datetime import datetime,  timedelta, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.transaction import Transaction
from filters.check import IncomeOp, ExpenseOp

async def get_create_if_not_exist(db: AsyncSession, tg_id: int) -> User:
    select_user = select(User).where(User.tg_id == tg_id)
    res = await db.execute(select_user)
    
    user = res.scalar_one_or_none()
    if user is None:
        user = User(tg_id = tg_id)
        db.add(user)
        await db.commit()
        await db.refresh()
    
    return user