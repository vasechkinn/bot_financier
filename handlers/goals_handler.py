from aiogram import Router, types, filters
from aiogram.filters import Command, CommandObject
from models.database import sessionLocal
from repo.db import (
    get_balance,
    set_goal,
    get_active_goal,
    )

router_goal = Router()

@router_goal.message(Command('set_goal'))
async def set_gosl_handler(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply('Формат: /set_goal 100000 "Скопить на отпуск"\nСумма и описание обязательны.')
        return
    
    elems = [elem.strip() for elem in args.split(' ', 1)]
    if len(elems) <2:
        await message.reply('Укажите сумму и описание цели. Пример: /set_goal 100000 Скопить на отпуск')
        return
    
    try:
        summa = float(elems[0].replace(',', '.'))
    except ValueError:
        await message.reply('Сумма должна быть числом.')
        return
    
    description = elems[1].strip()
    if not description:
        await message.reply('Описание цели не может быть пустым.')
        return
    
    async with sessionLocal() as db:
        try:
            goal = await set_goal(db, message.from_user.id, description, summa)

            await message.reply(
                f"🎯 Цель установлена!\n"
                f"Сумма: {summa:.2f}\n"
                f"Описание: {description}\n"
                f"Прогресс можно отследить через /goals"
            )
        except ValueError as e:
            await message.reply(f"Ошибка: {e}")

@router_goal.message(Command('goals'))
async def get_goals_handler(message: types.Message):
    async with sessionLocal() as db:
        balance = await get_balance(db, message.from_user.id)
        goals = await get_active_goal(db, message.from_user.id)

        if not goals:
            await message.reply("У вас нет активных целей. Установите через /set_goal")
            return
        
        arr = ["🎯 Ваши финансовые цели:\n"]
        for goal in goals:
            if goal.summa <= 0:
                progress = 100
            else:
                progress = max(0, min(100, (balance / goal.summa) * 100))
            
            status = "✅ Достигнута!" if balance >= goal.summa else f"📈 Прогресс: {progress:.1f}%"

            arr.append(f"- {goal.description}")
            arr.append(f"  Цель: {goal.summa:.2f} | Баланс: {balance:.2f} | {status}\n")

        await message.reply("\n".join(arr))