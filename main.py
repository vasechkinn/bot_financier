import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage 
from handlers.register_handler import router_register
from midlewares.reg import RegMidleware
from models.database import engine, Base
from handlers.income_expense import router
from handlers.goals_handler import router_goal
from handlers.register_handler import router_register

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()

    bot = Bot(token="8926554564:AAHFoKZdA3kfrnWLMiNiREwe6hY1CRbFVgw")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(router)
    dp.include_router(router_goal)
    dp.include_router(router_register)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())