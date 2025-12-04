# region Wallet endpoint descriptions
CREATE_WALLET_DESC = "Создаёт новый кошелёк с указанным названием и начальным балансом."
CREATE_WALLET_RESP = "Созданный кошелёк с присвоенным идентификатором."

GET_WALLET_DESC = (
    "Возвращает данные одного кошелька по идентификатору. "
    "Если кошелёк не найден — ошибка 404."
)
GET_WALLET_RESP = "Объект кошелька."

LIST_WALLETS_DESC = (
    "Возвращает список кошельков с фильтрацией, пагинацией и сортировкой."
)
LIST_WALLETS_RESP = "Список кошельков."

UPDATE_WALLET_DESC = (
    "Обновляет параметры существующего кошелька. "
    "Если кошелёк не найден — ошибка 404."
)
UPDATE_WALLET_RESP = "Обновлённый кошелёк."

TOPUP_WALLET_DESC = (
    "Пополняет баланс кошелька на указанную сумму. " "Сумма должна быть положительной."
)
TOPUP_WALLET_RESP = "Кошелёк после пополнения."

DELETE_WALLET_DESC = (
    "Удаляет кошелёк по идентификатору. " "Если кошелёк не найден — ошибка 404."
)
DELETE_WALLET_RESP = "Флаг успешного удаления."
# endregion
from typing import Dict, List, Optional

from app.schemas import WalletCreate, WalletResponse, WalletUpdate  # ВАЖНО

# region Wallet endpoints metadata
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
