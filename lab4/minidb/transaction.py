import copy
from typing import Any

class TransactionError(Exception):
    pass

class Transaction:
    """Контекстний менеджер для атомарних транзакцій."""
    def __init__(self, db: Any):
        self.db = db
        self._backup = None

    def __enter__(self):
        self._backup = copy.deepcopy(self.db.tables)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.tables = self._backup
            raise TransactionError(f"Transaction failed: {exc_val}")
        return False