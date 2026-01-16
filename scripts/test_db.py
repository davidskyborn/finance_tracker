import asyncio
import asyncpg


async def main() -> None:
    conn = await asyncpg.connect(
        user="finance_user",
        password="finance_pass",
        database="finance_tracker",
        host="localhost",
        port=5432,
    )

    result = await conn.fetch("SELECT 1;")
    print(result)

    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
