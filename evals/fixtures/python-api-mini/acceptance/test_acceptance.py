import sqlite3
import unittest

from app import ledger


def count(conn, table="records"):
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.conn = ledger.connect()

    def test_withdraw_more_than_balance_is_rejected(self):
        acc = ledger.open_account(self.conn, owner_id=1, balance=50)
        with self.assertRaises(ledger.InsufficientFunds):
            ledger.withdraw(self.conn, acc, 80)
        self.assertEqual(ledger.get_balance(self.conn, acc), 50)

    def test_withdraw_non_positive_amount_is_rejected(self):
        acc = ledger.open_account(self.conn, owner_id=1, balance=50)
        for bad in (0, -5):
            with self.assertRaises(ledger.InvalidAmount):
                ledger.withdraw(self.conn, acc, bad)
        self.assertEqual(ledger.get_balance(self.conn, acc), 50)

    def test_reimporting_same_rows_does_not_duplicate(self):
        rows = [{"ref": "A", "amount": 10}, {"ref": "B", "amount": 20}]
        ledger.import_rows(self.conn, source_id=1, rows=rows)
        ledger.import_rows(self.conn, source_id=1, rows=rows)
        self.assertEqual(count(self.conn), 2)

    def test_same_ref_in_a_different_source_is_allowed(self):
        rows = [{"ref": "A", "amount": 10}]
        ledger.import_rows(self.conn, source_id=1, rows=rows)
        ledger.import_rows(self.conn, source_id=2, rows=rows)
        self.assertEqual(count(self.conn), 2)

    def test_database_itself_rejects_duplicate_business_key(self):
        self.conn.execute(
            "INSERT INTO records (source_id, external_ref, amount) VALUES (1, 'A', 10)"
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO records (source_id, external_ref, amount) VALUES (1, 'A', 99)"
            )


if __name__ == "__main__":
    unittest.main()
