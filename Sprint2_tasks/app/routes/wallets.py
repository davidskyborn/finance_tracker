from typing import Any, Callable, Dict, List, Optional
from app.schemas import WalletCreate, WalletResponse, WalletTopup, WalletUpdate
from fastapi import APIRouter, HTTPException
from starlette import status

# ниже будет метадата для расширенного описания генераторов!
# region Endpoints metadata
CREATE_WALLET_META = {
    "path": "/",
    "response_model": WalletResponse,
    "summary": "Создание кошелька",
    "description": (
        "Создаёт новый кошелёк с указанным названием и начальным балансом. "
        "Данные сохраняются во временное хранилище в памяти."
    ),
    "response_description": "Созданный кошелёк с присвоенным идентификатором.",
}

GET_WALLET_META = {
    "path": "/{wallet_id}",
    "response_model": WalletResponse,
    "summary": "Получение кошелька по идентификатору",
    "description": (
        "Возвращает данные одного кошелька по его идентификатору. "
        "Если кошелёк не найден, возвращает ошибку 404."
    ),
    "response_description": "Объект кошелька с указанным идентификатором.",
}

LIST_WALLETS_META = {
    "path": "/",
    "response_model": List[WalletResponse],
    "summary": "Список кошельков",
    "description": (
        "Возвращает список кошельков с поддержкой фильтрации по названию, "
        "пагинации (limit/offset) и сортировки по выбранному полю и порядку."
    ),
    "response_description": "Список кошельков после применения фильтров и сортировки.",
}

UPDATE_WALLET_META = {
    "path": "/{wallet_id}",
    "response_model": WalletResponse,
    "summary": "Обновление параметров кошелька",
    "description": (
        "Обновляет имя или другие параметры существующего кошелька. "
        "Если кошелёк с указанным идентификатором не найден, возвращает ошибку 404."
    ),
    "response_description": "Обновлённый объект кошелька.",
}

TOPUP_WALLET_META = {
    "path": "/{wallet_id}/topup",
    "response_model": WalletResponse,
    "summary": "Пополнение баланса кошелька",
    "description": (
        "Увеличивает баланс кошелька на указанную сумму. "
        "Сумма пополнения должна быть больше нуля. "
        "Если кошелёк не найден, возвращает ошибку 404."
    ),
    "response_description": "Кошелёк после успешного пополнения баланса.",
}

DELETE_WALLET_META = {
    "path": "/{wallet_id}",
    "summary": "Удаление кошелька",
    "description": (
        "Удаляет кошелёк по идентификатору из временного хранилища. "
        "Если кошелёк не найден, возвращает ошибку 404."
    ),
    "response_description": "Результат операции удаления в виде флага success.",
}
# endregion

"""
Что такое роутер?
Что такоое роутер API Router? Это мини приложение внутри фреймворка.
Весь код из мейна мы повесим на роутер. 
Префикс = /wallets. Все что мы опишем как @router.get("/") с этим префиксом 
- превратится в /wallets.
Например: @router.get("/{wallet_id}") → /wallets/{wallet_id} и т.д.

tags= ["wallets"] в swagger все эти маршруты будут в группе wallets.
"""
router = APIRouter(prefix="/wallets", tags=["wallets"])
# наша псевдо-база в памяти: id -> WalletResponse
fake_db: dict[int, WalletResponse] = {}

# Обертки над router.get/post/put/delete для облегченных генераторов
def wallet_get(**kwargs: Any) -> Callable[..., Any]:
    """Обёртка над router.get с подавлением проблем типизации для mypy."""
    return router.get(**kwargs)  # type: ignore[arg-type]
def wallet_post(**kwargs: Any) -> Callable[..., Any]:
    """Обёртка над router.post с подавлением проблем типизации для mypy."""
    return router.post(**kwargs)  # type: ignore[arg-type]
def wallet_put(**kwargs: Any) -> Callable[..., Any]:
    """Обёртка над router.put с подавлением проблем типизации для mypy."""
    return router.put(**kwargs)  # type: ignore[arg-type]
def wallet_delete(**kwargs: Any) -> Callable[..., Any]:
    """Обёртка над router.delete с подавлением проблем типизации для mypy."""
    return router.delete(**kwargs)  # type: ignore[arg-type]

# созданию кошельков
@wallet_post(**CREATE_WALLET_META)
#     "/", response_model=WalletResponse,
#     summary="создание нового кошелька",
#     description=( "Создаёт новый кошелёк с указанным названием и начальным балансом. "
#         "Данные сохраняются во временное хранилище в памяти."
#     ),
# response_description="Созданный кошелёк с присвоенным идентификатором.")
def create_wallet(wallet: WalletCreate) -> WalletResponse:
    """
    Создает новый кошелек.

    Эндпоинт принимает имя и начальный баланс кошелька, сохраняет данные в in-memory и возвращает
    созданный обьект.

    Args:
        wallet: Данные для создания кошелька (имя, начальный баланс).
    Returns:
        Обьект кошелька с присвоенным идентификатором.
    """
    new_id = len(fake_db) + 1
    wallet_response = WalletResponse(
        id=new_id,
        name=wallet.name,
        balance=0.0,
    )
    fake_db[new_id] = wallet_response
    return wallet_response

# четвертый эндпоинт, выдача списка кошельков по значению
# @router.get(
#     path="/",
#     response_model=list[WalletResponse],
#     summary="Список кошельков",
#     description=(
#         "Возвращает список кошельков с поддержкой фильтрации по названию, "
#         "пагинации (limit/offset) и сортировки по выбранному полю и порядку."
#     ),
#     response_description="Список кошельков после применения фильтров и сортировки.",
# )
@wallet_get(**LIST_WALLETS_META)
def list_wallets(
    name: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
) -> list[WalletResponse]:
    """
    Дает список кошельков с фильтрацией, сорт и пагинацией.

    Args:
        name: Фильтр по названию кошелька.
        limit: Количество элементов в выдаче.
        offset: Смещение для пагинации.
        sort_by: Поле для сортировки.
        sort_order: Порядок сортировки.

    Returns:
        Список WalletResponse.
    """
    wallets = list(fake_db.values())
    if name is not None:
        wallets = [wallet for wallet in wallets if name.lower() in wallet.name.lower()]
    # сортировка
    if sort_by is not None:
        if sort_by == "name":
            wallets = sorted(
                wallets,
                key=lambda w: w.name.lower(),
                reverse=(sort_order == "desc"),
            )
        elif sort_by == "balance":
            wallets = sorted(
                wallets,
                key=lambda w: w.balance,
                reverse=(sort_order == "desc"),
            )
    # пагинация через срез списка
    wallet = wallets[offset : offset + limit]
    return wallets

# пятьй эндпоинт, выдача конкретного кошелька
# @router.get(
#     path="/{wallet_id}",
#     response_model=WalletResponse,
#     summary="Получение кошелька по идентификатору",
#     description=(
#         "Возвращает данные одного кошелька по его идентификатору. "
#         "Если кошелёк не найден, возвращает ошибку 404."
#     ),
#     response_description="Объект кошелька с указанным идентификатором.",
# )
@wallet_get(**GET_WALLET_META)
def get_wallet(wallet_id: int) -> WalletResponse:  # int wallet_id - аргумент
    """
     Возвращает данные одного кошелька по его идентификатору.

    Args:
        wallet_id: Идентификатор кошелька.

    Raises:
        HTTPException: 404, если кошелёк с таким ID не найден.

    Returns:
        Объект кошелька.
    """
    wallet = fake_db.get(
        wallet_id
    )  # переменная wallet берет ЗНАЧЕНИЕ по ключу из словаря
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet  # здесь будет значение по ключу из словаря

# шестой эндпоинт, перезапись кошелька
# @router.put(
#     path="/{wallet_id}",
#     response_model=WalletResponse,
#     summary="Обновление параметров кошелька",
#     description=(
#         "Обновляет имя или другие параметры существующего кошелька. "
#         "Если кошелёк с указанным идентификатором не найден, возвращает ошибку 404."
#     ),
#     response_description="Обновлённый объект кошелька.",
# )
@wallet_put(**UPDATE_WALLET_META)
def update_wallet(wallet_id: int, wallet_update: WalletUpdate) -> WalletResponse:
    """
    Обновляет параметры существующего кошелька.

     Args:
         wallet_id: Идентификатор кошелька, который нужно обновить.
         wallet: Объект с новыми значениями полей кошелька.

     Raises:
         HTTPException: 404, если кошелёк не найден.

     Returns:
         Обновлённый объект WalletResponse.
    """
    wallet = fake_db.get(wallet_id)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")

    wallet.name = wallet_update.name
    return wallet

# седьмой эндпоинт - удаление кошелька
# @router.delete(
#     path="/{wallet_id}",
#     summary="Удаление кошелька",
#     description=(
#         "Удаляет кошелёк по идентификатору из временного хранилища. "
#         "Если кошелёк не найден, возвращает ошибку 404."
#     ),
#     response_description="Результат операции удаления в виде флага success.",
# )
@wallet_delete(**DELETE_WALLET_META)
def delete_wallet(wallet_id: int) -> dict[str, bool]:
    """
    Удаляет кошелёк по идентификатору.

    Args:
        wallet_id: Идентификатор кошелька для удаления.

    Raises:
        HTTPException: 404, если кошелёк с таким ID не найден.

    Returns:
        Словарь с ключом 'success', показывающим успешность операции.
    """
    wallet = fake_db.pop(wallet_id, None)
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"success": True}

# восьмой эндпоинт - пополнение кошелька
# @router.post(
#     path="/{wallet_id}/topup",
#     response_model=WalletResponse,
#     summary="Пополнение баланса кошелька",
#     description=(
#         "Увеличивает баланс кошелька на указанную сумму. "
#         "Сумма пополнения должна быть больше нуля. "
#         "Если кошелёк не найден, возвращает ошибку 404."
#     ),
#     response_description="Кошелёк после успешного пополнения баланса.",
# )
@wallet_post(**TOPUP_WALLET_META)
def top_up_wallet(wallet_id: int, top_up: WalletTopup) -> WalletResponse:
    """
    Увеличивает баланс указанного кошелька на заданную сумму.

    Args:
        wallet_id: Идентификатор кошелька.
        amount: Сумма пополнения (должна быть больше нуля).

    Raises:
        HTTPException: 404, если кошелёк не найден.

    Returns:
        Обновлённый объект WalletResponse после пополнения.
    """
    wallet = fake_db.get(wallet_id)  # wallet = значение по ключу из ДБ
    if wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    wallet.balance += top_up.amount
    return wallet
