from aiogram import Router, types, filters
from aiogram.filters import Command, CommandObject
from models.database import sessionLocal
from repo.db import (
    add_income,
    add_expense,
    get_transactions,
    get_create_if_not_exist,
    goal_progress,
    get_balance,
)
from filters.check import (
    IncomeOp,
    ExpenseOp,
    check_message,
)
from pydantic import ValidationError

router = Router()


@router.message(Command("start"))
async def start(message: types.Message):
    async with sessionLocal() as bd:
        user = await get_create_if_not_exist(bd, message.from_user.id)

        if not user.login:
            await message.reply(
                f"Привет, {message.from_user.full_name}!\n\n"
                "Для использования бота необходимо зарегистрироваться.\n"
                "Используйте команду /register, чтобы создать логин и пароль.\n\n"
                "После регистрации вам станут доступны:\n"
                "➕ Доход: /add_income сумма, категория, цель\n"
                "➖ Расход: /add_expense сумма, категория, цель\n"
                "📊 История: /view_transactions период [категория]\n"
                "🎯 Цели: /set_goal сумма описание\n"
                "📈 Прогресс: /goals"
            )
            return

        await message.reply(
            f"С возвращением, {user.login}!\n"
            "➕ Доход: /add_income сумма, категория, цель\n"
            "➖ Расход: /add_expense сумма, категория, цель\n"
            "📊 История: /view_transactions период [категория]\n"
            "Периоды: день, неделя, месяц, год\n"
            "🎯 Цели: /set_goal сумма описание\n"
            "📈 Прогресс: /goals"
        )


@router.message(Command("add_income"))
async def add_income_handler(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply(
            "Формат: /add_income 1000, еда, обед (категория и цель опциональны)"
        )
        return

    args_message = [elem.strip() for elem in args.split(",")]
    dict_checking = check_message(args_message)

    try:
        summa = float(dict_checking["summa"].replace(",", "."))
    except ValueError:
        await message.reply("сумма должна быть числом.")
        return

    ALLOWED_INCOME = ("еда", "развлечения", "отдых", "зарплата", "другое")

    category_ = dict_checking["category"] if dict_checking["category"] else ""
    if category_ not in ALLOWED_INCOME:
        category_ = "другое"

    try:
        income_op = IncomeOp(
            summa=summa,
            category=category_,
            purpose=dict_checking["purpose"]
            if dict_checking["purpose"]
            else "на мечту",
        )
    except ValidationError as e:
        await message.reply(f"ошибка в данных: {e}")
        return

    async with sessionLocal() as db:
        try:
            await add_income(db, message.from_user.id, income_op)
            balance = await get_balance(db, message.from_user.id)
            await message.reply(f"✅ Доход добавлен. Текущий баланс: {balance:.2f}")

            can_close = await goal_progress(db, message.from_user.id)
            for goal in can_close:
                balance = await get_balance(db, message.from_user.id)

                await message.reply(
                    f"🎉 Поздравляем! Вы достигли цели «{goal.description}»!\n"
                    f"Цель: {goal.summa:.2f} | Текущий баланс: {balance:.2f}"
                )

        except ValueError as e:
            await message.reply(f"Ошибка: {e}")


@router.message(Command("add_expense"))
async def add_expense_handler(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply(
            "Формат: /add_expense 1000, еда, обед (категория и цель опциональны)"
        )
        return

    args_message = [elem.strip() for elem in args.split(",")]
    dict_checking = check_message(args_message)

    try:
        summa = float(dict_checking["summa"].replace(",", "."))
    except ValueError:
        await message.reply("сумма должна быть числом.")
        return

    ALLOWED_EXPENSE = ("еда", "развлечения", "отдых", "подарок", "другое")

    category_ = dict_checking["category"] if dict_checking["category"] else ""
    if category_ not in ALLOWED_EXPENSE:
        category_ = "другое"

    try:
        expense_op = ExpenseOp(
            summa=summa,
            category=category_,
            purpose=dict_checking["purpose"]
            if dict_checking["purpose"]
            else "на мечту",
        )
    except ValidationError as e:
        await message.reply(f"ошибка в данных: {e}")
        return

    async with sessionLocal() as db:
        try:
            await add_expense(db, message.from_user.id, expense_op)
            balance = await get_balance(db, message.from_user.id)
            await message.reply(f"✅ Рфсход добавлен. Текущий баланс: {balance:.2f}")
        except ValueError as e:
            await message.reply(f"Ошибка: {e}")


@router.message(Command("view_transactions"))
async def view_transactions(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply(
            "Формат: /view_transactions период [категория]\n"
            "Периоды: день, неделя, месяц, год\n"
            "Пример: /view_transactions неделя еда"
        )
        return

    elems = [elem.strip() for elem in args.split()]
    period = elems[0].lower()
    category = elems[1] if len(elems) > 1 else None

    allowed_periods = ("день", "неделя", "месяц", "год")
    if period not in allowed_periods:
        await message.reply(f"Неверный период. Доступные: {', '.join(allowed_periods)}")
        return

    async with sessionLocal() as db:
        transactions, income_sum, expense_sum = await get_transactions(
            db, message.from_user.id, period, category
        )

    if not transactions:
        await message.reply("за указанный период трфнзакций нет")
        return

    lines = []
    lines.append(f"📊 История за {period}")
    if category:
        lines.append(f"Категория: {category}")
    lines.append(f"💰 Доходы: {income_sum:.2f}")
    lines.append(f"💸 Расходы: {expense_sum:.2f}")
    lines.append(f"📈 Баланс: {(income_sum - expense_sum):.2f}")
    lines.append("\n📝 Последние операции:")

    for t in transactions[:10]:
        emoji = "➕" if t.operation_type.value == "пополнение" else "➖"
        date_str = t.date.strftime("%d.%m %H:%M")
        lines.append(f"{emoji} {date_str} | {t.category} | {t.summa:.2f} | {t.purpose}")

    if len(transactions) > 10:
        lines.append(f"\n... и ещё {len(transactions) - 10} операций")

    await message.reply("\n".join(lines))
