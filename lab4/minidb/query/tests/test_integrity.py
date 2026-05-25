import unittest
from minidb import Database, Column, IntegerType, StringType
from minidb.transaction import TransactionError

class TestDatabaseIntegrity(unittest.TestCase):
    def setUp(self):
        """Цей метод запускається перед кожним тестом, створюючи чисту базу."""
        self.db = Database("test_integrity_db")
        self.db.create_table("departments", [
            Column("id", IntegerType(), unique=True),
            Column("name", StringType(), nullable=False)
        ])
        self.db.create_table("employees", [
            Column("id", IntegerType(), unique=True),
            Column("name", StringType()),
            Column("dept_id", IntegerType(), references=("departments", "id"))
        ])

    def test_type_validation(self):
        """Перевірка, чи працює захист від неправильних типів даних."""
        with self.assertRaises(TypeError):
            # Намагаємося записати рядок замість числа
            self.db.get_table("departments").insert({"id": "one", "name": "IT"})

    def test_unique_constraint(self):
        """Перевірка обмеження unique=True."""
        self.db.get_table("departments").insert({"id": 1, "name": "IT"})
        with self.assertRaises(ValueError):
            # Намагаємося додати інший відділ з таким самим ID
            self.db.get_table("departments").insert({"id": 1, "name": "HR"})

    def test_foreign_key_constraint(self):
        """Перевірка зв'язків між таблицями (Foreign Key)."""
        with self.assertRaises(ValueError):
            # Додаємо працівника у відділ 99, якого не існує
            self.db.get_table("employees").insert({"id": 101, "name": "Bob", "dept_id": 99})

    def test_transaction_rollback(self):
        """Перевірка, чи працює відкат транзакції при помилці."""
        try:
            with self.db.transaction():
                self.db.get_table("departments").insert({"id": 1, "name": "IT"})
                # Ця дія викличе помилку, бо dept_id 99 не існує
                self.db.get_table("employees").insert({"id": 101, "name": "Alice", "dept_id": 99})
        except TransactionError:
            pass
        
        # Перевіряємо, що відділ IT не зберігся (транзакція відкотилася)
        dept_count = len(list(self.db.get_table("departments")))
        self.assertEqual(dept_count, 0)