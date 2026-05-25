from typing import Any, Dict

class Row:
    """Рядок таблиці, що обгортає словник."""
    def __init__(self, data: Dict[str, Any], row_id: int):
        self._data = data
        self.id = row_id

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Row):
            return self._data == other._data
        return False

    def __iter__(self):
        return iter(self._data.items())