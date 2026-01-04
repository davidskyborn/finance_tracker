# здесь делаем таски по fastapi
# сперва pip install fastapi
# далее устанавливаем uvicorn pip install uvicorn
"""
поскольку у нас проект имеет несколько папок - команда запуска путается
поэтому запускаем командой:
cd /Users/davidskyborn/PycharmProjects/finance_tracker/Sprint2_tasks
uvicorn app.main:app --reload

либо так:
uvicorn app.main:app --reload
"""
from typing import Optional

from app.routes.wallets import router as wallets_router
from app.schemas import WalletCreate, WalletResponse, WalletUpdate
from fastapi import FastAPI, HTTPException

# импортируем типизацию
# импортируем библиотеку fastapi
# и импортируем pydantic
from pydantic import BaseModel
from starlette import status

# импортируем наши модели из schemas
# создаем обьект приложения
app = FastAPI()
# создаем первый эндпоинт (домашняя страница), и даем ему логику
# этот эндпоинт оказывается нам не нужен поэтому мы его спрячем
# @app.get("/")
# def home() -> dict[str, str]:
#     return {"message": "Finance Tracker API"}


# # создаем второй эндпоинт (по адресу /health) и даем ему логику
# @app.get("/health")
# def healthcheck() -> dict[str, str]:
#     return {"status": "ok"}


app.include_router(wallets_router)
# # фейк база данных для локального хранения
# fake_db: dict[int, WalletResponse] = {}

# для запуска нам надо обратиться к библиотеке uvicorn
# запуск: uvicorn app.main:app --reload
# теперь каждый раз сервер будет перезагружаться (для тестирования)
