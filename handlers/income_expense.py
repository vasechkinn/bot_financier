from aiogram import Router, types, filters
from aiogram.filters import Command, CommandObject
from models.database import sessionLocal
from repo.db import (
    add_income,
    add_expense,
    get_transactions,
    get_create_if_not_exist,
    )
from filters.check import (
    IncomeOp,
    ExpenseOp,
    check_message,
    )
from pydantic import ValidationError
router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    async with sessionLocal() as bd:
        user = await get_create_if_not_exist(bd, message.from_user.id)

        await message.reply(
            f"привет, {message.from_user.full_name}!\n"
            "➕ Доход: /add_income сумма, категория, цель\n"
            "➖ Расход: /add_expense сумма, категория, цель\n"
            "📊 История: /view_transactions период [категория]\n"
            "Периоды: день, неделя, месяц, год"
        )

@router.message(Command('add_income'))
async def add_income_handler(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply('Формат: /add_income 1000, еда, обед (категория и цель опциональны)')
        return
    
    args_message = [elem.strip() for elem in args.split(',')]
    dict_checking = check_message(args_message)

    try:
        summa = float(dict_checking['summa'].replace(',', '.'))
    except ValueError:
        await message.reply("сумма должна быть числом.")
        return
    
    try:
        income_op = IncomeOp(
            summa = summa,
            category = dict_checking["category"] if dict_checking["category"] else "другое",
            purpose = dict_checking["purpose"] if dict_checking["purpose"] else "на мечту"
        )
    except ValidationError as e:
        await message.reply(f"ошибка в данных: {e}")
        return

    async with sessionLocal() as db:
        try:
            await add_income(db, message.from_user.id, income_op)
            await message.reply("✅ Доход добавлен")
        except ValueError as e:
            await message.reply(f"Ошибка: {e}")