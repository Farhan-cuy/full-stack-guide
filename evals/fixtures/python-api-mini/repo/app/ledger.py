import sqlite3


class InsufficientFunds(Exception):
    pass


class InvalidAmount(Exception):
    pass


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER NOT NULL,
            balance INTEGER NOT NULL
        );
        CREATE TABLE records (
            id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            external_ref TEXT NOT NULL,
            amount INTEGER NOT NULL
        );
        """
    )
    return conn


def open_account(conn, owner_id, balance=0):
    cur = conn.execute(
        "INSERT INTO accounts (owner_id, balance) VALUES (?, ?)", (owner_id, balance)
    )
    conn.commit()
    return cur.lastrowid


def get_balance(conn, account_id):
    row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
    return row["balance"]


def withdraw(conn, account_id, amount):
    row = conn.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,)).fetchone()
    new_balance = row["balance"] - amount
    conn.execute("UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, account_id))
    conn.commit()
    return new_balance


def import_rows(conn, source_id, rows):
    for r in rows:
        conn.execute(
            "INSERT INTO records (source_id, external_ref, amount) VALUES (?, ?, ?)",
            (source_id, r["ref"], r["amount"]),
        )
    conn.commit()
    return len(rows)
