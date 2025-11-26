# делаем контрольную задачу 1
# задача: валидатор данных юзера
"""
Создать функцию validate_user_data, которая принимает словарь с данными
Использовать Pydantic для валидации: имя (строка, 2-50 символов),
возраст (целое число, 18-100), email (строка, валидный email)
Функция должна возвращать валидированные данные или выбрасывать исключение
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel,EmailStr

"""
допустим у нас есть словарь с данными юзера
{ "name" : "valera", "age": 25, "email" : "" }
задача: проверить, что все данные валидны?
name = строка
age= цифры
email - почта (наверное еще одну функцию сделать на чек @ и точки)
если все ок вернуть валидированные данные
если нет то что то другое сделать
"""

class User(BaseModel):
    name: str
    age: int
    email: EmailStr

def validate(data: Dict[str, Any]) -> User:
    # получаем значения
    name = data.get('name')
    age = data.get('age')
    email = data.get('email')
    # проверяем что данные есть
    if name is None or age is None or email is None:
        raise ValueError('нет нужного поля')
    # проверяем длину имени
    if len(str(name)) < 2 or len(str(age)) > 50:
        raise ValueError("слишком длинное имя")
    # проверка возраста
    if int(age) < 18 or int(age) > 100:
        raise ValueError('возраст неверный')
    data['age'] = int(age)
    return User(**data)

name = input('enter name: ')
age = input('enter age: ')
email = input('enter email: ')
data ={
    'name': name,
    'age': age,
    'email': email
}
print(validate(data))
