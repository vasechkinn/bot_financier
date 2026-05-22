from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.fsm.context import FSMContext
from models.database import sessionLocal
from repo.db import is_register
from states.register import RegisterStates


class RegMidleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        message: Message = event
        tg_id = message.from_user.id
        text = message.text | ""

        if text.startswith("/start") or text.startswith("/register"):
            return await handler(event, data)

        state: FSMContext | None = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state and current_state.startswith("RegisterStates:"):
                return await handler(event, data)

        async with sessionLocal() as db:
            registered = await is_register(db, tg_id)

        if not registered:
            await message.answer(
                "❌ Вы не зарегистрированы.\n"
                "Пожалуйста, используйте команду /register для создания аккаунта."
            )
            return

        return await handler(event, data)
