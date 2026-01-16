# создаем скрипт запуска кода для БД

import asyncio
from database.database import create_tables


def main() -> None:
    asyncio.run(create_tables())


if __name__ == "__main__":
    main()
