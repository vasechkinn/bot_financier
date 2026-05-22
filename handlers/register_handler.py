from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from models.database import sessionLocal
from repo.db import set_log_pass, get_user_tg_id
from states.register import RegisterStates

router_register = Router()


@router_register.message(Command("register"))
async def reg_router(message: types.Message, state: FSMContext):
    async with sessionLocal() as db:
        user = await get_user_tg_id(db, message.from_user.id)

        if user and user.login:
            await message.answer(
                "✅ Вы уже зарегистрированы. Для просмотра профиля используйте /profile"
            )
            return

    await state.set_state(RegisterStates.waiting_login)
    await message.answer("Придумайте логин:")


@router_register.message(RegisterStates.waiting_login, F.text)
async def register_login(message: types.Message, state: FSMContext):
    login = message.text.strip()
    if len(login) < 3:
        await message.answer(
            "Логин должен содержать минимум 3 символа. Попробуйте ещё раз:"
        )
        return

    await state.update_data(login=login)
    await state.set_state(RegisterStates.waiting_pass)
    await message.answer("Теперь введите пароль:")


@router_register.message(RegisterStates.waiting_pass, F.text)
async def register_password(message: types.Message, state: FSMContext):
    password = message.text.strip()

    if len(password) < 4:
        await message.answer(
            "Пароль должен содержать минимум 4 символа. Попробуйте ещё раз:"
        )
        return

    user_data = await state.get_data()
    login = user_data.get("login")

    async with sessionLocal() as db:
        user = await set_log_pass(db, message.from_user.id, login, password)

    await state.clear()
    await message.answer(
        f"✅ Регистрация завершена!\n"
        f"Логин: {login}\n"
        "Теперь вы можете использовать все команды бота."
    )
