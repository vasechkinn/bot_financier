from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession)
from sqlalchemy.orm import declarative_base

DB_URL = 'sqlire+aiosqlite:///database.sqlite3'

engine = create_async_engine(DB_URL, echo=False)
sessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(declarative_base):
    pass

async def get_db():
    async with sessionLocal() as session:
        yield session