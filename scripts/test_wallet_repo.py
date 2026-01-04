import asyncio

from app.database import engine
from app.repositories.wallet_repository import (
    create_wallets_batch,
    search_wallets,
    count_wallets,
    avg_balance,
    max_balance_wallet,
    update_balance_if_enough,
    soft_delete_wallet,
    get_all_wallets,
)


async def main():
    print("1) Batch create")
    created = await create_wallets_batch(engine, ["Alpha", "Beta", "Gamma"])
    print("rowcount:", created)

    print("\n2) Search by name_part='a' (case-insensitive)")
    res = await search_wallets(engine, name_part="a", order_by="name")
    print(res)

    print("\n3) Count / Avg / Max")
    print("count:", await count_wallets(engine))
    print("avg:", await avg_balance(engine))
    print("max_wallet:", await max_balance_wallet(engine))

    print("\n4) Update balance with check (pick first wallet from get_all_wallets)")
    wallets = await get_all_wallets(engine)
    if not wallets:
        print("no wallets to test")
        return
    wid = wallets[0]["id"]
    print("wallet_id:", wid)

    print("deposit +100 =>", await update_balance_if_enough(engine, wid, 100))
    print("withdraw -30 =>", await update_balance_if_enough(engine, wid, -30))
    print("withdraw -1000000 (should fail) =>", await update_balance_if_enough(engine, wid, -1_000_000))

    print("\n5) Soft delete wallet and verify it disappears from search/aggregates")
    print("soft_delete =>", await soft_delete_wallet(engine, wid))
    print("soft_delete again =>", await soft_delete_wallet(engine, wid))

    print("search by id still in DB via get_all_wallets (may include deleted if you didn't filter there):")
    print(await get_all_wallets(engine))

    print("search_wallets (should exclude deleted):")
    print(await search_wallets(engine))

    print("count (should exclude deleted):", await count_wallets(engine))


if __name__ == "__main__":
    asyncio.run(main())
