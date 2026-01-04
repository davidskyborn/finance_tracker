# репозиторий кода для БД
from __future__ import annotations
from typing import Any
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import select, insert, update, delete, and_, or_, func
from app.database import wallets

select(wallets).where(wallets.c.id == 1)

# функция проверки существования кошелька
async def wallet_exists(engine: AsyncEngine, wallet_id: int) -> bool:
    stmt = select(wallets.c.id).where(wallets.c.id == wallet_id)

    async with engine.connect() as conn:
        result = await conn.execute(stmt)
        row = result.first()

    return row is not None

# функция вызова кошелька
async def get_wallet_by_id(engine: AsyncEngine, wallet_id: int) -> dict[str, Any] | None:
    stmt = select(wallets).where(wallets.c.id == wallet_id)

    async with engine.connect() as conn:
        result = await conn.execute(stmt)
        row = result.mappings().one_or_none()

    return dict(row) if row else None

# функция получения всех кошельков
async def get_all_wallets(engine: AsyncEngine) -> list[dict[str, Any]]:
    stmt = select(wallets).order_by(wallets.c.id)

    async with engine.connect() as conn:
        result = await conn.execute(stmt)
        rows = result.mappings().all()

    return [dict(r) for r in rows]

# функция создания нового кошелька
async def create_wallet(engine: AsyncEngine, name: str) -> dict[str, Any]:
    stmt = (
        insert(wallets)
        .values(name=name)
        .returning(wallets.c.id, wallets.c.name, wallets.c.balance, wallets.c.created_at)
    )

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        row = result.mappings().one()

    return dict(row)

# функция обновление кошелька: вернуть количество затронутых строк (0 или 1)
async def update_wallet(engine: AsyncEngine, wallet_id: int, name: str) -> int:
    stmt = (
        update(wallets)
        .where(wallets.c.id == wallet_id)
        .values(name=name)
    )

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        return result.rowcount or 0

# функция удаление кошелька: вернуть количество затронутых строк (0 или 1)
async def delete_wallet(engine: AsyncEngine, wallet_id: int) -> int:
    if not await wallet_exists(engine, wallet_id):
        return 0

    stmt = delete(wallets).where(wallets.c.id == wallet_id)

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        return result.rowcount or 0


# Подзадача 1: поиск/фильтрация/сортировка
async def search_wallets(engine: AsyncEngine, name_part: str | None = None, min_balance: float | None = None,
    order_by: str = "id", desc: bool = False,) -> list[dict[str, Any]]:
    stmt = select(wallets)

    conditions = [wallets.c.deleted_at.is_(None)]

    if name_part:
        conditions.append(wallets.c.name.ilike(f"%{name_part}%"))

    if min_balance is not None:
        conditions.append(wallets.c.balance >= min_balance)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # сортировка
    column = getattr(wallets.c, order_by, wallets.c.id)
    stmt = stmt.order_by(column.desc() if desc else column.asc())

    async with engine.connect() as conn:
        result = await conn.execute(stmt)
        rows = result.mappings().all()

    return [dict(r) for r in rows]



# Подзадача 2: агрегации
async def count_wallets(engine: AsyncEngine) -> int:
    # stmt = select(func.count()).select_from(wallets)
    stmt = select(func.count()).select_from(wallets).where(wallets.c.deleted_at.is_(None))

    async with engine.connect() as conn:
        result = await conn.execute(stmt)
        value = result.scalar_one()

    return int(value)


async def avg_balance(engine: AsyncEngine) -> float | None:
    # stmt = select(func.avg(wallets.c.balance))
    stmt = select(func.avg(wallets.c.balance)).where(wallets.c.deleted_at.is_(None))

    async with engine.connect() as conn:
        result = await conn.execute(stmt)
        value = result.scalar_one()

    return float(value) if value is not None else None


async def max_balance_wallet(engine: AsyncEngine) -> dict[str, Any] | None:
    # max_stmt = select(func.max(wallets.c.balance))
    max_stmt = select(func.max(wallets.c.balance)).where(wallets.c.deleted_at.is_(None))

    async with engine.connect() as conn:
        max_value = (await conn.execute(max_stmt)).scalar_one()

        if max_value is None:
            return None

        # stmt = select(wallets).where(wallets.c.balance == max_value)
        stmt = select(wallets).where(
            and_(wallets.c.balance == max_value, wallets.c.deleted_at.is_(None))
        )

        row = (await conn.execute(stmt)).mappings().first()

    return dict(row) if row else None


# Подзадача 3: сложные условия/пакетные/soft delete
async def update_balance_if_enough(
    engine: AsyncEngine,
    wallet_id: int,
    delta: float,
) -> int:
    stmt = (
        update(wallets)
        .where(
            and_(
                wallets.c.id == wallet_id,
                wallets.c.balance + delta >= 0,
            )
        )
        .values(balance=wallets.c.balance + delta)
    )

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        return result.rowcount or 0

async def create_wallets_batch(engine: AsyncEngine, names: list[str]) -> int:
    if not names:
        return 0

    payload = [{"name": n} for n in names]

    stmt = insert(wallets).values(payload)

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        return result.rowcount or 0



async def soft_delete_wallet(
    engine: AsyncEngine,
    wallet_id: int,
) -> int:
    stmt = (
        update(wallets)
        .where(
            and_(
                wallets.c.id == wallet_id,
                wallets.c.deleted_at.is_(None),
            )
        )
        .values(deleted_at=func.now())
    )

    async with engine.begin() as conn:
        result = await conn.execute(stmt)
        return result.rowcount or 0
