from abc import ABC, abstractmethod
from typing import Any

class DataType(ABC):
    """Базовий клас для типів даних."""
    def validate(self, value: Any) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__

    @classmethod
    def from_string(cls, type_str: str) -> 'DataType':
        mapping = {
            "INTEGER": IntegerType,
            "STRING": StringType,
            "BOOLEAN": BooleanType,
            "FLOAT": FloatType
        }
        type_class = mapping.get(type_str.upper())
        if not type_class:
            raise ValueError(f"Unknown type: {type_str}")
        return type_class()

class IntegerType(DataType):
    def validate(self, value: Any) -> bool:
        return isinstance(value, int)

class StringType(DataType):
    """Тип даних для рядків."""
    def validate(self, value: Any) -> bool:
        return isinstance(value, str)

class FloatType(DataType):
    """Тип даних для чисел з плаваючою крапкою."""
    def validate(self, value: Any) -> bool:
        return isinstance(value, float)

class BooleanType(DataType):
    def validate(self, value: Any) -> bool:
        return isinstance(value, bool)