import unittest
from minidb import Database, Column, IntegerType, StringType
from minidb.query.engine import Query, JoinedTable

class TestQueryEngine(unittest.TestCase):
    def setUp(self):
        """Підготовка бази з даними для тестування запитів."""
        self.db = Database("test_query_db")
        self.db.create_table("departments", [
            Column("id", IntegerType(), unique=True),
            Column("name", StringType())
        ])
        self.db.create_table("employees", [
            Column("id", IntegerType(), unique=True),
            Column("name", StringType()),
            Column("dept_id", IntegerType())
        ])
        
        # Наповнюємо даними
        self.db.get_table("departments").insert({"id": 1, "name": "IT"})
        self.db.get_table("employees").insert({"id": 101, "name": "Orest", "dept_id": 1})
        self.db.get_table("employees").insert({"id": 102, "name": "Alice", "dept_id": 1})

    def test_select_and_where(self):
        """Тестування фільтрації (WHERE) та вибірки (SELECT)."""
        q = Query(self.db.get_table("employees"))
        results = q.select(['name']).where('id', '=', 101).execute()
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Orest")
        # Перевіряємо, що id не повернувся, бо ми зробили select(['name'])
        self.assertNotIn('id', results[0])

    def test_aggregation_count(self):
        """Тестування агрегатної функції COUNT."""
        q = Query(self.db.get_table("employees"))
        self.assertEqual(q.count(), 2)

    def test_inner_join(self):
        """Тестування з'єднання таблиць (INNER JOIN)."""
        join_q = JoinedTable(
            self.db.get_table("employees"),
            self.db.get_table("departments"),
            left_on="dept_id",
            right_on="id"
        )
        results = join_q.execute()
        
        self.assertEqual(len(results), 2)
        # Перевіряємо, що префікси таблиць застосувалися правильно
        self.assertEqual(results[0]["departments.name"], "IT")
        self.assertEqual(results[0]["employees.name"], "Orest")