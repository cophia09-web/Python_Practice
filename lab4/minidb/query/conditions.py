from typing import Any

class Condition:
    """Клас для перевірки умов фільтрації (WHERE)."""
    def __init__(self, column: str, operator: str, value: Any):
        self.column = column
        self.operator = operator
        self.value = value

    def evaluate(self, row_data: dict) -> bool:
        val = row_data.get(self.column)
        if val is None:
            return False
            
        if self.operator == '=': return val == self.value
        if self.operator == '>': return val > self.value
        if self.operator == '<': return val < self.value
        if self.operator == '>=': return val >= self.value
        if self.operator == '<=': return val <= self.value
        if self.operator == '!=': return val != self.value
        if self.operator == 'LIKE': return str(self.value) in str(val)
        return False