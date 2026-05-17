import asyncio
import logging
from aiogram import Bot, Dispatcher
from models.database import engine, Base
from handlers.income_expense import router

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()

    bot = Bot(token="8926554564:AAHFoKZdA3kfrnWLMiNiREwe6hY1CRbFVgw")
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())