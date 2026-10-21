import unittest

from app import ledger


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.conn = ledger.connect()

    def test_open_account_and_read_balance(self):
        acc = ledger.open_account(self.conn, owner_id=1, balance=100)
        self.assertEqual(ledger.get_balance(self.conn, acc), 100)

    def test_withdraw_within_balance(self):
        acc = ledger.open_account(self.conn, owner_id=1, balance=100)
        self.assertEqual(ledger.withdraw(self.conn, acc, 30), 70)
        self.assertEqual(ledger.get_balance(self.conn, acc), 70)

    def test_import_inserts_rows(self):
        rows = [{"ref": "A", "amount": 10}, {"ref": "B", "amount": 20}]
        ledger.import_rows(self.conn, source_id=1, rows=rows)
        count = self.conn.execute("SELECT COUNT(*) AS c FROM records").fetchone()["c"]
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
