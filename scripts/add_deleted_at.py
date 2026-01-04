import asyncio
from sqlalchemy import text

from app.database import engine


async def main():
    sql = text("ALTER TABLE wallets ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;")
    async with engine.begin() as conn:
        await conn.execute(sql)


if __name__ == "__main__":
    asyncio.run(main())
