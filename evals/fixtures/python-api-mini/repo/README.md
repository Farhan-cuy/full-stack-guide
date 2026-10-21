# python-api-mini

A tiny ledger/import module used as a test fixture (standard library only, SQLite in memory).

- Run tests: `python -m unittest discover -s tests -v` (Python 3.9+)
- Source: `app/ledger.py`
- Functions: `connect`, `open_account`, `get_balance`, `withdraw`, `import_rows`
- Domain errors: `InsufficientFunds`, `InvalidAmount`
