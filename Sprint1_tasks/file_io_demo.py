from pathlib import Path
# Pathlib - стандартный модуль
# Path - класс для работы с путями к файлам и папкам
# корректная работа с путями на всех OS
# удомные методы, читаемость

# with - штука которая открывает файл, работает с ним и закрывает после кода


# базовый шаблон
with open('test.txt', 'w') as file:
    file.write('text valera 123')

# open (...) - открывает файл
# 'w' - команда указывающая на write
# as file - сохраняет как переменную
# метод .write задает текст

def write_read(filename: str, text: str) -> str:
    with open(filename, 'w') as file:
        file.write(text)
    with open(filename, 'r') as file:
        return file.read()

# функция открывает файл, задает текст ('w')
# далее функция открывает его же и читает файл ('r')
# возвращает файл
