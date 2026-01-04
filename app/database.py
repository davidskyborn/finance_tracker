# здесь мы конвертируем нашу schema.sql в бд построенную через alchemy

from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    func,
)

# "Папка", в которой хранятся описания всех таблиц
metadata = MetaData()

# CREATE TABLE wallets (...)
wallets = Table(
    "wallets",
    metadata,
    Column("id", Integer, primary_key=True),  # SERIAL PRIMARY KEY
    Column("name", String(255), nullable=False),  # VARCHAR(255) NOT NULL
    Column("balance", Numeric(12, 2), nullable=False, server_default="0"),  # NUMERIC(12,2) NOT NULL DEFAULT 0
    Column("created_at", DateTime, nullable=False, server_default=func.now()),  # TIMESTAMP NOT NULL DEFAULT NOW()
    Column("deleted_at", DateTime, nullable=True),

)

# CREATE TABLE transactions (...)
transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),  # SERIAL PRIMARY KEY
    Column("wallet_id", Integer, ForeignKey("wallets.id"), nullable=False),  # INTEGER NOT NULL REFERENCES wallets(id)
    Column("amount", Numeric(12, 2), nullable=False),  # NUMERIC(12,2) NOT NULL
    Column("description", String(255), nullable=True),  # VARCHAR(255)
    Column("created_at", DateTime, nullable=False, server_default=func.now()),  # TIMESTAMP NOT NULL DEFAULT NOW()
    Column("deleted_at", DateTime, nullable=True),

)

# Дальше добавляем в этот же файл подключение к БД и создание таблиц
import os
from sqlalchemy.ext.asyncio import create_async_engine

def _get_database_url() -> str:
    # ожидается строка вида:
    # postgresql+asyncpg://user:password@localhost:5432/dbname
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url

engine = create_async_engine(_get_database_url(), echo=True)

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

# Что делает metadata.create_all в этой строке:
# - берёт wallets и transactions, которые лежат в metadata
# - генерирует SQL CREATE TABLE ...
# - выполняет его в Postgres
