# CREATE TABLE wallets (...)
wallets = Table(
    "wallets",
    metadata,
    Column("id", Integer, primary_key=True),  # SERIAL PRIMARY KEY
    Column("name", String(255), nullable=False),  # VARCHAR(255) NOT NULL
    Column("balance", Numeric(12, 2), nullable=False, server_default="0"),  # NUMERIC(12,2) NOT NULL DEFAULT 0
    Column("created_at", DateTime, nullable=False, server_default=func.now()),  # TIMESTAMP NOT NULL DEFAULT NOW()
    Column("deleted_at", DateTime, nullable=True),
)

# CREATE TABLE transactions (...)
transactions = Table(
    "transactions",
    metadata,
    Column("id", Integer, primary_key=True),  # SERIAL PRIMARY KEY
    Column("wallet_id", Integer, ForeignKey("wallets.id"), nullable=False),  # INTEGER NOT NULL REFERENCES wallets(id)
    Column("amount", Numeric(12, 2), nullable=False),  # NUMERIC(12,2) NOT NULL
    Column("description", String(255), nullable=True),  # VARCHAR(255)
    Column("created_at", DateTime, nullable=False, server_default=func.now()),  # TIMESTAMP NOT NULL DEFAULT NOW()
    Column("deleted_at", DateTime, nullable=True),
)


--CREATE TABLE wallets (
--    id SERIAL PRIMARY KEY,
--    name VARCHAR(255) NOT NULL,
--    balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
--    created_at TIMESTAMP NOT NULL DEFAULT NOW()
--);
--
--CREATE TABLE transactions (
--    id SERIAL PRIMARY KEY,
--    wallet_id INTEGER NOT NULL,
--    amount NUMERIC(12, 2) NOT NULL,
--    description VARCHAR(255),
--    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
--
--    FOREIGN KEY (wallet_id) REFERENCES wallets(id)
--);

