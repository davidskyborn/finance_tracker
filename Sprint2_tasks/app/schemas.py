# импортируем нужные элементы
import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator

"""
зачем мы импортируем BaseModel и наследуем от него?
это движок pydantic
он делает 3 вещи:
- валидирует входящие данные
- конвертирует типы
- генерирует схемы для fastapi/swagger
- чтобы pydantic знал что наш класс это модель данных,
а не просто произвольный класс, надо наследоваться от basemodel
далее. зачем field validator
обычный str не знает наших бизнес правил, для этого нужно подключать правило
он сообщает питону "эта функция отвечает за проверку поля name" 
далее. зачем cls
на момент валидации экзэмпляр обььекта еще не создан
значит единственный метод это передать в метод сам класс - cls
это нужно чтобы метод можно было использовать до создания обьекта
"""
# wallet create - модель данных, которую клиент отправляет
# при создании кошелька
# field_validator - указывает что функция валидирует именно поле name


# создаем класс для создания кошелька
# в нем зашиты условия валидаци
# создаем класс pydantic, который наследует параметры basemodel
# class Wallet(BaseModel):
#     name: str
#     balance: float
# класс создания кошелька
class WalletCreate(BaseModel):
    name: str

    @field_validator("name")  # декоратор, связанный с pydantic, для валидации
    @classmethod  # метод привязан ко всему классу и наследным обьектам
    def validate_name(cls, value: str) -> str:
        if len(value) < 2:
            raise ValueError("имя слишком короткое")
        if len(value) > 50:
            raise ValueError("имя слишком длинное")
        return value


# класс обновления кошелька
class WalletUpdate(BaseModel):
    name: str

    @field_validator("name")  # декоратор, связанный с pydantic, для валидации
    @classmethod  # метод привязан ко всему классу и наследным обьектам
    def validate_name(cls, value: str) -> str:
        if len(value) < 2:
            raise ValueError("имя слишком короткое")
        if len(value) > 50:
            raise ValueError("имя слишком длинное")
        return value


# класс по выдаче информации кошелька
class WalletResponse(BaseModel):
    id: int
    name: str
    balance: float


# класс по пополнению кошелька
class WalletTopup(BaseModel):
    amount: float

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("сумма должна быть положительной")
        return value


# класс Enum! Для перечислений
class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


# модель транзакции
class Transaction(BaseModel):
    wallet_id: int  # id кошелька из нашей базы в памяти
    type: TransactionType  # либо income либо expense
    amount: float  # сумма
    date: datetime.date  # обьект datetime.date, pydantic даст строку в гуд виде

    # сперва валидация положительной суммы
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("сумма должна быть положительная")
        return value

    # теперь валидация не будущей даты
    @field_validator("date")
    @classmethod
    def validate_date(cls, value: datetime.date) -> datetime.date:
        today = datetime.date.today()
        if value > today:
            raise ValueError("дата не может быть в будущем")
        return value


# cls - класс, такой же обьект, как self, но
# - self: конкретный обьект
# - cls: сам класс (чертеж)
# в валидаторах Pydantic надо писать cls
# тк Pydantic вызывает валидаторы у класса, а не экзэмпляра
