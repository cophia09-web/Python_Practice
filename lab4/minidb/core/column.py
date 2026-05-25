from typing import Any, Optional, Tuple, List, Dict
from .datatypes import DataType


class Column:
    """Зберігає назву, тип даних та обмеження стовпця."""
    def __init__(
            self, name: str, 
            data_type: DataType, 
            nullable: bool = True, 
            unique: bool = False, 
            references: Optional[Tuple[str, str]] = None
        ) -> None:
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.unique = unique
        self.references = references

    def validate(self, value: Any) -> bool:
        if value is None:
            if not self.nullable:
                raise ValueError(f"Column {self.name} cannot be null.")
            return True
        if not self.data_type.validate(value):
            raise TypeError(f"Invalid type for column {self.name}. Expected {self.data_type}.")
        return True

    def check_unique(self, value: Any, table_rows: List[Dict[str, Any]]) -> bool:
        if value is None:
            return True
        for row in table_rows:
            if row.get(self.name) == value:
                raise ValueError(f"Value {value} in column {self.name} must be unique.")
        return True

    def check_foreign_key(self, value: Any, database: Any) -> bool:
        if self.references and value is not None:
            ref_table_name, ref_column_name = self.references
            ref_table = database.get_table(ref_table_name)
            
            found = any(row[ref_column_name] == value for row in ref_table)
            if not found:
                raise ValueError(f"Foreign key constraint failed: Value {value} not found in {ref_table_name}.{ref_column_name}")
        return True

    def __repr__(self) -> str:
        return f"Column({self.name}, {self.data_type}, nullable={self.nullable}, unique={self.unique})"