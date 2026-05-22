from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from models.database import sessionLocal
from repo.db import set_user_credentials, get_user_by_tg_id
from states.register import RegisterStates

router_register = Router()

@router_register.message(Command('register'))
async def reg_router(message: types.Message, state: FSMContext):
    async with sessionLocal() as db:
        user = await get_user_by_tg_id(db, message.from_user.id)

        if user and user.login:
            await message.answer("✅ Вы уже зарегистрированы. Для просмотра профиля используйте /profile")
            return
    
    await state.set_state(RegisterStates.waiting_login)
    await message.answer("Придумайте логин:")