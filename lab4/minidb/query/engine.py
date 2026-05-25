from typing import List, Any, Dict, Optional
from .conditions import Condition

class Query:
    """Підтримка ланцюжка методів (Method Chaining) для запитів."""
    def __init__(self, table):
        self.table = table
        self._columns: List[str] = []
        self._conditions: List[Condition] = []
        self._limit: Optional[int] = None
        self._offset: int = 0

    def select(self, columns: List[str]):
        self._columns = columns
        return self

    def where(self, column: str, operator: str, value: Any):
        self._conditions.append(Condition(column, operator, value))
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def offset(self, count: int):
        self._offset = count
        return self

    def execute(self) -> List[Dict[str, Any]]:
        results = []
        for row in self.table:
            if all(cond.evaluate(row._data) for cond in self._conditions):
                results.append(row._data.copy())

        start = self._offset
        end = (start + self._limit) if self._limit is not None else None
        results = results[start:end]

        if self._columns:
            return [{col: r.get(col) for col in self._columns} for r in results]
        return results

    def count(self) -> int:
        return len(self.execute())

    def sum(self, column: str) -> float:
        return sum(r.get(column, 0) for r in self.execute())

    def avg(self, column: str) -> float:
        res = self.execute()
        return sum(r.get(column, 0) for r in res) / len(res) if res else 0

class JoinedTable:
    """Внутрішнє з'єднання (INNER JOIN) між двома таблицями."""
    def __init__(self, table1, table2, left_on: str, right_on: str):
        self.table1 = table1 
        self.table2 = table2 
        self.left_on = left_on   
        self.right_on = right_on 

    def execute(self) -> List[Dict[str, Any]]:
        joined_results = []
        for row1 in self.table1:
            for row2 in self.table2:
                if row1[self.left_on] == row2[self.right_on]:
                    combined_data = {}
                    for key, value in row1:
                        combined_data[f"{self.table1.name}.{key}"] = value
                    for key, value in row2:
                        combined_data[f"{self.table2.name}.{key}"] = value
                    joined_results.append(combined_data)
        return joined_results