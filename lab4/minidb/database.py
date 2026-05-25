import json
from typing import List, Dict, Any
from .core.table import Table
from .core.column import Column
from .transaction import Transaction

class Database:
    """Центральна точка доступу до БД."""
    def __init__(self, name: str):
        self.name = name
        self.tables: Dict[str, Table] = {}

    def create_table(self, name: str, columns: List[Column]):
        if name in self.tables:
            raise ValueError(f"Table {name} already exists.")
        self.tables[name] = Table(name, columns, self)

    def get_table(self, name: str) -> Table:
        if name not in self.tables:
            raise ValueError(f"Table {name} not found.")
        return self.tables[name]

    def transaction(self) -> Transaction:
        return Transaction(self)
        
    def save_to_json(self, filename: str):
        data = {
            t_name: [row._data for row in table] 
            for t_name, table in self.tables.items()
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)