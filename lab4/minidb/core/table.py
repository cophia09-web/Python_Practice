from typing import Any, List, Dict, Optional
from .column import Column
from .row import Row

class Table:
    """Координатор структури даних таблиці."""
    def __init__(self, name: str, columns: List[Column], database: Any):
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.database = database
        self._rows: List[Row] = []
        self._next_id = 1
        self._unique_indexes: Dict[str, Dict[Any, Row]] = {col.name: {} for col in columns if col.unique}

    def insert(self, data: Dict[str, Any]) -> Row:
        for col_name, col in self.columns.items():
            val = data.get(col_name)
            col.validate(val)
            if col.unique:
                col.check_unique(val, [r._data for r in self._rows])
            if col.references:
                col.check_foreign_key(val, self.database)

        new_row = Row(data, self._next_id)
        self._rows.append(new_row)
        self._next_id += 1

        for col_name in self._unique_indexes:
            val = data.get(col_name)
            if val is not None:
                self._unique_indexes[col_name][val] = new_row

        return new_row

    def get_by_id(self, row_id: int) -> Optional[Row]:
        for row in self._rows:
            if row.id == row_id:
                return row
        return None

    def update(self, row_id: int, new_data: Dict[str, Any]) -> Row:
        """Оновлення даних рядка за його ID."""
        row = self.get_by_id(row_id)
        if not row:
            raise ValueError(f"Row with ID {row_id} not found.")

        # 1. Валідація нових даних перед записом
        for col_name, value in new_data.items():
            if col_name in self.columns:
                col = self.columns[col_name]
                col.validate(value)
                
                if col.unique and value != row[col_name]:
                    col.check_unique(value, [r._data for r in self._rows if r.id != row_id])
                
                if col.references:
                    col.check_foreign_key(value, self.database)

        # 2. Якщо все ок — оновлюємо
        for col_name, value in new_data.items():
            if col_name in self.columns:
                if col_name in self._unique_indexes:
                    old_val = row[col_name]
                    if old_val in self._unique_indexes[col_name]:
                        del self._unique_indexes[col_name][old_val]
                    self._unique_indexes[col_name][value] = row
                
                row[col_name] = value 
        return row

    def delete(self, row_id: int, policy: str = "RESTRICT") -> bool:
        """Видалення рядка за ID з урахуванням політики цілісності."""
        row = self.get_by_id(row_id)
        if not row:
            raise ValueError(f"Row with ID {row_id} not found in table {self.name}.")

        # Перевірка залежностей
        for t_name, table in self.database.tables.items():
            for col in table.columns.values():
                if col.references and col.references[0] == self.name:
                    ref_col = col.references[1]
                    for other_row in table:
                        if other_row[col.name] == row[ref_col]:
                            if policy == "RESTRICT":
                                raise ValueError(f"RESTRICT: Cannot delete row. Table '{t_name}' has dependency.")
                            elif policy == "CASCADE":
                                table.delete(other_row.id, policy="CASCADE")

        for col_name in self._unique_indexes:
            val = row[col_name]
            if val in self._unique_indexes[col_name]:
                del self._unique_indexes[col_name][val]

        self._rows.remove(row)
        return True

    def __iter__(self):
        return iter(self._rows)

    def __len__(self) -> int:
        return len(self._rows)