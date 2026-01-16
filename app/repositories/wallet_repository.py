# репозиторий кода для БД
from __future__ import annotations
from typing import Any, Optional, Iterable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection
from sqlalchemy.sql import Executable
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.engine import Result
from sqlalchemy import select, insert, update, delete, and_, func
from database.database import wallets
select(wallets).where(wallets.c.id == 1)

class WalletRepo:
    _engine: AsyncEngine

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @staticmethod
    def _row_to_dict(row: Any) -> dict[str, Any]:
        return dict(row)

    @staticmethod
    def _not_deleted() -> ColumnElement[bool]:
        return wallets.c.deleted_at.is_(None)

    async def _fetch_one(self, stmt: Executable) -> Optional[dict[str, Any]]:
        async with self._engine.connect() as conn:  # type: AsyncConnection
            res: Result = await conn.execute(stmt)
            row = res.mappings().one_or_none()
            return self._row_to_dict(row) if row else None

    async def _fetch_all(self, stmt: Executable) -> list[dict[str, Any]]:
        async with self._engine.connect() as conn:
            res: Result = await conn.execute(stmt)
            rows = res.mappings().all()
            return [self._row_to_dict(r) for r in rows]

    async def _exec_rowcount(self, stmt: Executable) -> int:
        async with self._engine.begin() as conn:
            res: Result = await conn.execute(stmt)
            return int(res.rowcount or 0)

    async def _exec_one(self, stmt: Executable) -> dict[str, Any]:
        async with self._engine.begin() as conn:
            res: Result = await conn.execute(stmt)
            row = res.mappings().one()
            return self._row_to_dict(row)

    async def exists(self, wallet_id: int, include_deleted: bool = False) -> bool:
        stmt = select(wallets.c.id).where(wallets.c.id == wallet_id)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())

        async with self._engine.connect() as conn:
            res = await conn.execute(stmt)
            return res.first() is not None

    async def get_by_id(self, wallet_id: int, include_deleted: bool = False) -> Optional[dict[str, Any]]:
        stmt = select(wallets).where(wallets.c.id == wallet_id)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())
        return await self._fetch_one(stmt)

    async def get_all(self, include_deleted: bool = False) -> list[dict[str, Any]]:
        stmt = select(wallets).order_by(wallets.c.id)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())
        return await self._fetch_all(stmt)

    async def create(self, name: str) -> dict[str, Any]:
        stmt = (
            insert(wallets)
            .values(name=name)
            .returning(
                wallets.c.id,
                wallets.c.name,
                wallets.c.balance,
                wallets.c.created_at,
                wallets.c.deleted_at,
            )
        )
        return await self._exec_one(stmt)

    async def update_name(self, wallet_id: int, name: str, include_deleted: bool = False) -> int:
        stmt = update(wallets).where(wallets.c.id == wallet_id).values(name=name)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())
        return await self._exec_rowcount(stmt)

    async def hard_delete(self, wallet_id: int, include_deleted: bool = False) -> int:
        stmt = delete(wallets).where(wallets.c.id == wallet_id)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())
        return await self._exec_rowcount(stmt)

    async def search(
        self,
        name_part: Optional[str] = None,
        min_balance: Optional[float] = None,
        order_by: str = "id",
        desc: bool = False,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        stmt = select(wallets)

        conditions: list[ColumnElement[bool]] = []
        if not include_deleted:
            conditions.append(self._not_deleted())
        if name_part:
            conditions.append(wallets.c.name.ilike(f"%{name_part}%"))
        if min_balance is not None:
            conditions.append(wallets.c.balance >= min_balance)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        column = getattr(wallets.c, order_by, wallets.c.id)
        stmt = stmt.order_by(column.desc() if desc else column.asc())

        return await self._fetch_all(stmt)

    async def count(self, include_deleted: bool = False) -> int:
        stmt = select(func.count()).select_from(wallets)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())

        async with self._engine.connect() as conn:
            value = (await conn.execute(stmt)).scalar_one()
            return int(value)

    async def avg_balance(self, include_deleted: bool = False) -> Optional[float]:
        stmt = select(func.avg(wallets.c.balance)).select_from(wallets)
        if not include_deleted:
            stmt = stmt.where(self._not_deleted())

        async with self._engine.connect() as conn:
            value = (await conn.execute(stmt)).scalar_one()
            return float(value) if value is not None else None

    async def max_balance_wallet(self, include_deleted: bool = False) -> Optional[dict[str, Any]]:
        max_stmt = select(func.max(wallets.c.balance)).select_from(wallets)
        if not include_deleted:
            max_stmt = max_stmt.where(self._not_deleted())

        async with self._engine.connect() as conn:
            max_value = (await conn.execute(max_stmt)).scalar_one()
            if max_value is None:
                return None

            stmt = select(wallets).where(wallets.c.balance == max_value)
            if not include_deleted:
                stmt = stmt.where(self._not_deleted())

            res = await conn.execute(stmt)
            row = res.mappings().first()
            return self._row_to_dict(row) if row else None

    async def update_balance_if_enough(self, wallet_id: int, delta: float) -> int:
        stmt = (
            update(wallets)
            .where(
                and_(
                    wallets.c.id == wallet_id,
                    self._not_deleted(),
                    wallets.c.balance + delta >= 0,
                )
            )
            .values(balance=wallets.c.balance + delta)
        )
        return await self._exec_rowcount(stmt)

    async def create_batch(self, names: Iterable[str]) -> int:
        names_list = [n for n in names if n]
        if not names_list:
            return 0

        payload = [{"name": n} for n in names_list]
        stmt = insert(wallets).values(payload)

        async with self._engine.begin() as conn:
            await conn.execute(stmt)

        return len(payload)

    async def soft_delete(self, wallet_id: int) -> int:
        stmt = (
            update(wallets)
            .where(and_(wallets.c.id == wallet_id, self._not_deleted()))
            .values(deleted_at=func.now())
        )
        return await self._exec_rowcount(stmt)

    async def restore(self, wallet_id: int) -> int:
        stmt = (
            update(wallets)
            .where(and_(wallets.c.id == wallet_id, wallets.c.deleted_at.is_not(None)))
            .values(deleted_at=None)
        )
        return await self._exec_rowcount(stmt)

# -------
# здесь все новые функции
# функция проверки существования кошелька
async def wallet_exists(engine: AsyncEngine, wallet_id: int) -> bool:
    """
    Проверяет, существует ли кошелёк с заданным ID.

    Учитывает soft-delete: удалённые кошельки не считаются существующими.

    :param engine: AsyncEngine SQLAlchemy.
    :param wallet_id: Идентификатор кошелька.
    :return: True, если кошелёк существует и не удалён, иначе False.
    """
    return await WalletRepo(engine).exists(wallet_id)

# функция вызова кошелька
async def get_wallet_by_id(engine: AsyncEngine, wallet_id: int) -> dict[str, Any] | None:
    """
    Возвращает кошелёк по ID.

    Не возвращает soft-deleted записи.

    :param engine: AsyncEngine SQLAlchemy.
    :param wallet_id: Идентификатор кошелька.
    :return: Словарь с данными кошелька или None, если кошелёк не найден.
    """
    return await WalletRepo(engine).get_by_id(wallet_id)

# функция получения всех кошельков
async def get_all_wallets(engine: AsyncEngine) -> list[dict[str, Any]]:
    """
    Возвращает список всех не удалённых кошельков.

    :param engine: AsyncEngine SQLAlchemy.
    :return: Список словарей с данными кошельков.
    """
    return await WalletRepo(engine).get_all()

# функция создания нового кошелька
async def create_wallet(engine: AsyncEngine, name: str) -> dict[str, Any]:
    """
    Создаёт новый кошелёк.

    Баланс и дата создания устанавливаются на уровне базы данных.

    :param engine: AsyncEngine SQLAlchemy.
    :param name: Название кошелька.
    :return: Созданный кошелёк.
    """
    return await WalletRepo(engine).create(name)

# функция обновление кошелька: вернуть количество затронутых строк (0 или 1)
async def update_wallet(engine: AsyncEngine, wallet_id: int, name: str) -> int:
    """
    Обновляет имя кошелька.

    Работает только для не удалённых кошельков.

    :param engine: AsyncEngine SQLAlchemy.
    :param wallet_id: Идентификатор кошелька.
    :param name: Новое имя.
    :return: 1 если кошелёк обновлён, 0 если не найден.
    """
    return await WalletRepo(engine).update_name(wallet_id, name)

# функция удаление кошелька: вернуть количество затронутых строк (0 или 1)
async def delete_wallet(engine: AsyncEngine, wallet_id: int) -> int:
    """
    Физически удаляет кошелёк из базы данных.

    По умолчанию удаляются только не soft-deleted записи.

    :param engine: AsyncEngine SQLAlchemy.
    :param wallet_id: Идентификатор кошелька.
    :return: 1 если кошелёк удалён, 0 если не найден.
    """
    return await WalletRepo(engine).hard_delete(wallet_id)

# Подзадача 1: поиск/фильтрация/сортировка
async def search_wallets(
    engine: AsyncEngine,
    name_part: str | None = None,
    min_balance: float | None = None,
    order_by: str = "id",
    desc: bool = False,
) -> list[dict[str, Any]]:
    """
    Выполняет поиск кошельков с фильтрацией и сортировкой.

    По умолчанию исключает soft-deleted записи.

    :param engine: AsyncEngine SQLAlchemy.
    :param name_part: Подстрока для поиска по имени.
    :param min_balance: Минимальный баланс.
    :param order_by: Имя колонки для сортировки.
    :param desc: Сортировать по убыванию.
    :return: Список найденных кошельков.
    """
    return await WalletRepo(engine).search(
        name_part=name_part,
        min_balance=min_balance,
        order_by=order_by,
        desc=desc,
    )


# Подзадача 2: агрегации
async def count_wallets(engine: AsyncEngine) -> int:
    """
    Возвращает количество не удалённых кошельков.

    :param engine: AsyncEngine SQLAlchemy.
    :return: Количество кошельков.
    """
    return await WalletRepo(engine).count()

async def avg_balance(engine: AsyncEngine) -> float | None:
    """
    Возвращает средний баланс по не удалённым кошелькам.

    :param engine: AsyncEngine SQLAlchemy.
    :return: Средний баланс или None, если кошельков нет.
    """
    return await WalletRepo(engine).avg_balance()

async def max_balance_wallet(engine: AsyncEngine) -> dict[str, Any] | None:
    """
    Возвращает кошелёк с максимальным балансом.

    Учитывает только не удалённые кошельки.

    :param engine: AsyncEngine SQLAlchemy.
    :return: Кошелёк с максимальным балансом или None.
    """
    return await WalletRepo(engine).max_balance_wallet()

# Подзадача 3: сложные условия/пакетные/soft delete
async def update_balance_if_enough(
    engine: AsyncEngine,
    wallet_id: int,
    delta: float,
) -> int:
    """
    Изменяет баланс кошелька на delta, если итоговый баланс не станет отрицательным.

    Работает только для не удалённых кошельков.

    :param engine: AsyncEngine SQLAlchemy.
    :param wallet_id: Идентификатор кошелька.
    :param delta: Изменение баланса (может быть отрицательным).
    :return: 1 если обновление произошло, 0 если недостаточно средств или кошелёк не найден.
    """
    return await WalletRepo(engine).update_balance_if_enough(wallet_id, delta)

async def create_wallets_batch(engine: AsyncEngine, names: list[str]) -> int:
    """
    Создаёт несколько кошельков за одну операцию.

    :param engine: AsyncEngine SQLAlchemy.
    :param names: Список имён кошельков.
    :return: Количество созданных кошельков.
    """
    return await WalletRepo(engine).create_batch(names)

async def soft_delete_wallet(
    engine: AsyncEngine,
    wallet_id: int,
) -> int:
    """
    Помечает кошелёк как удалённый (soft delete).

    Устанавливает deleted_at, не удаляя запись физически.

    :param engine: AsyncEngine SQLAlchemy.
    :param wallet_id: Идентификатор кошелька.
    :return: 1 если кошелёк был помечен как удалённый, 0 если не найден.
    """
    return await WalletRepo(engine).soft_delete(wallet_id)


# ниже будут старые функции
''''# функция проверки существования кошелька
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
'''