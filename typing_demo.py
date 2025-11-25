from typing import List, Optional
# здесь мы разбираемся с такой штукой как типизация

def add(a: int, b: int) -> int: # функция сложения, подписываем типы
    return a + b

def average(values: list[float]) -> float: # функция ср.арифметического
    if not values:
        return 0.0
    return sum(values) / len(values)

def format_user(name: str, age: int | None) -> str:
    if age is None:
        return name
    return f'{name} {age}'

def is_adult(age: int) -> bool:
    if age >= 18:
        return True
    return False

# пишутся с большой буквы во имя поддержки старого питон:
# List[str]
# Dict[str, int]
# Set[int]
# Tuple[int, str]
# Optional[int]
# Union[int, str]
# нужные типы добавить в список import сверху

# 'poetry add --group dev mypy'
# проверка правильности типизации: 'poetry run mypy .'