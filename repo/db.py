from datetime import datetime,  timedelta, date
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.transaction import Transaction, OperationType
from models.goal import Goal
from models.database import Base
from filters.check import IncomeOp, ExpenseOp
from sqlalchemy.exc import IntegrityError

async def get_create_if_not_exist(db: AsyncSession, tg_id: int) -> User:
    """
    функция возвращает пользователя по его tg id
    если такого нет, то создает его запись
    """
    select_user = select(User).where(User.tg_id == tg_id)
    res = await db.execute(select_user)
    
    user = res.scalar_one_or_none()
    if user is None:
        user = User(tg_id = tg_id)
        db.add(user)

        try:
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            res2 =  await db.execute(select(User).where(User.tg_id == tg_id))
            user = res2.scalar_one()
    
    return user

async def get_user_id(db: AsyncSession, tg_id: int) -> int | None:
    select_id = select(User.id).where(User.tg_id == tg_id)
    res = await db.execute(select_id)
    return res.scalar_one_or_none()

async def add_income(
        db: AsyncSession,
        tg_id: int,
        data: IncomeOp
) -> Transaction:
    
    user_id_db = await get_user_id(db, tg_id)

    if user_id_db is None:
        raise ValueError('пользователь не найден')
    
    transaction = Transaction(
        summa = data.summa,
        operation_type = OperationType.INCOME,
        category = data.category,
        user_id = user_id_db,
        purpose = data.purpose
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

async def add_expense(
        db: AsyncSession,
        tg_id: int,
        data: ExpenseOp
) -> Transaction:
    
    user_id_db = await get_user_id(db, tg_id)

    if user_id_db is None:
        raise ValueError('пользователь не найден')
    
    transaction = Transaction(
        summa = data.summa,
        operation_type = OperationType.EXPENSE,
        category = data.category,
        user_id = user_id_db,
        purpose = data.purpose
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

async def get_transactions(
    db: AsyncSession,
    tg_id: int,
    period: str,
    category: str | None = None
):
    user_id_db = await get_user_id(db, tg_id)

    if user_id_db is None:
        return [], 0.0, 0.0
    
    today = date.today()

    if period == 'день':
        start = today
    elif period == 'неделя':
        start = today - timedelta(days=7)
    elif period == 'месяц':
        start = date(today.year, today.month, 1)
    elif period == 'год':
        start = date(today.year, 1, 1)
    else:
        return [], 0.0, 0.0
    
    date_start = datetime.combine(start, datetime.min.time())
    time_select = select(Transaction).where(
        Transaction.user_id == user_id_db,
        Transaction.date >= date_start
    ).order_by(Transaction.date.desc())

    if category:
        time_select = time_select.where(Transaction.category == category)

    res = await db.execute(time_select)
    transactions = res.scalars().all()

    all_incomes = sum(
        transaction.summa for transaction in transactions if transaction.operation_type == OperationType.INCOME
    )
    all_expenses = sum(
        transaction.summa for transaction in transactions if transaction.operation_type == OperationType.EXPENSE
    )

    return transactions, all_incomes, all_expenses

async def get_balance(
    db: AsyncSession,
    tg_id: int
):
    user_id_db = await get_user_id(db, tg_id)

    if user_id_db is None:
        return 0.0
    
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user_id_db)
    )

    transactions = result.scalars().all()
    income_sum = sum(t.summa for t in transactions if t.operation_type == OperationType.INCOME)
    expense_sum = sum(t.summa for t in transactions if t.operation_type == OperationType.EXPENSE)

    return income_sum - expense_sum

async def set_goal(
    db: AsyncSession,
    tg_id: int,
    description: str,
    summa: float
):
    user_id_db = await get_user_id(db, tg_id)

    if user_id_db is None:
        raise ValueError('не найден пользователь')
    
    goal = Goal(
        user_id=user_id_db,
        summa = summa,
        description=description,
        completion_status=False
    )

    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal

async def get_active_goal(
    db: AsyncSession,
    tg_id: int,
):
    user_id_db = await get_user_id(db, tg_id)

    if user_id_db is None:
        return []
    
    select_transactions = select(Goal).where(Goal.user_id == user_id_db, Goal.completion_status == False)
    res = await db.execute(select_transactions)

    return res.scalars().all()

async def goal_progress(
    db: AsyncSession,
    tg_id: int,
):
    goals = await get_active_goal(db, tg_id)
    if not goals:
        return []
    
    balance = await get_balance(db, tg_id)

    can_close = []
    for goal in goals:
        if balance >= goal.summa and not goal.completion_status:
            goal.completion_status = True
            goal.completion_at = datetime.now()
            can_close.append(goal)
    
    if can_close:
        await db.commit()
        for goal in can_close:
            await db.refresh(goal)
    
    return can_close

async def get_user_tg_id(db: AsyncSession, tg_id: int) -> User | None:
    select_user = select(User).where(User.id == tg_id)
    res = await db.execute(select_user)

    return res.scalar_one_or_none()

async def is_register(db: AsyncSession, tg_id: int):
    user = await get_user_tg_id(db, tg_id)
    if user is None:
        return False
    
    return user.login is not None and user.login != ""