# задача номер 2. асинк сборщик информации
"""
мы сделаем 3 асинхронные функции которые
представляют собой разные микросервисы
возвращают разные структуры данных
имитируют сетевую задержку через asyncio.sleep()

надо сджелать функцию которая имитирует сбор данных из 3 внешнних источников
каждый источник должен возвращать разные данные после случайной задержки 0.1-0.5
обьединить результаты и вернуть в структурированном виде

у нас 3 функции, каждая асинк
имеет делей
дает разные данные
потом отдельная асинк запускает все 3 через gather
собирает и что то возвращает

что они могут возвращать так, чтобы были разные структуры данных?
первая может возвращать массив
вторая хеш
третья строку

"""
from typing import Dict, Any
import asyncio
import time

async def aaa():
    await asyncio.sleep(1)
    return [1,2,3]
async def bbb():
    await asyncio.sleep(2)
    return {'status': 'valera'}
async def ccc():
    await asyncio.sleep(3)
    return 'ready!'

async def ddd() -> Dict[str, Any]:
    result1, result2, result3 = await asyncio.gather(
        aaa(),
        aaa(),
        aaa(),
    )
    return {
        'service1': result1,
        'service2': result2,
        'service3': result3
    }

start = time.time()
asyncio.run(aaa())
end = time.time()

print('общее время:', start - end)
