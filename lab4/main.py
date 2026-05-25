from minidb import Database, Column, IntegerType, StringType
from minidb.transaction import TransactionError
from minidb.query.engine import Query, JoinedTable

# 1. Ініціалізація бази
db = Database("school_db")
print("Базу даних 'school_db' ініціалізовано.")

# 2. Створення таблиць
db.create_table("departments", [
    Column("id", IntegerType(), unique=True),
    Column("name", StringType(), nullable=False)
])

db.create_table("employees", [
    Column("id", IntegerType(), unique=True),
    Column("name", StringType()),
    Column("dept_id", IntegerType(), references=("departments", "id"))
])
print("Таблиці 'departments' та 'employees' створено.\n")

# 3. Транзакція з відкатом
print("--- Тест невдалої транзакції (Rollback) ---")
try:
    with db.transaction():
        db.get_table("departments").insert({"id": 1, "name": "IT"})
        # Помилка: dept_id 99 не існує
        db.get_table("employees").insert({"id": 101, "name": "Alice", "dept_id": 99})
except TransactionError as e:
    print(f"Відкат успішний. Причина: {e}")
    
print(f"Кількість записів у 'departments' після відкату: {len(list(db.get_table('departments')))}\n")

# 4. Успішна транзакція
print("--- Тест успішної транзакції (Commit) ---")
with db.transaction():
    db.get_table("departments").insert({"id": 1, "name": "IT"})
    db.get_table("departments").insert({"id": 2, "name": "HR"})
    db.get_table("employees").insert({"id": 101, "name": "Bob", "dept_id": 1})
    db.get_table("employees").insert({"id": 102, "name": "Alice", "dept_id": 2})
print("Дані успішно додано.\n")

# 5. Тест Update
print("--- Тест Update ---")
# Оновлюємо 1-й рядок (Боба)
db.get_table("employees").update(1, {"name": "Bob (Senior)"})
updated_bob = db.get_table("employees").get_by_id(1)
print(f"Оновлене ім'я працівника 101: {updated_bob['name']}\n")

# 6. Тест Query Engine (Фільтрація та Агрегація)
print("--- Тест Query Engine ---")
q = Query(db.get_table("employees"))
# Вибираємо тільки імена тих, у кого id >= 101
results = q.select(['name']).where('id', '>=', 101).execute()
print(f"Вибірка імен (id >= 101): {results}")
print(f"Загальна кількість працівників (COUNT): {q.count()}\n")

# 7. Тест INNER JOIN
print("--- Тест INNER JOIN ---")
join_query = JoinedTable(
    db.get_table("employees"), 
    db.get_table("departments"), 
    left_on="dept_id", 
    right_on="id"
)
for entry in join_query.execute():
    print(f"Працівник: {entry['employees.name']} | Відділ: {entry['departments.name']}")
print()

# 8. Тест Delete
print("--- Тест Delete ---")
try:
    # Очікуємо помилку RESTRICT (1 - це внутрішній ID департаменту IT)
    db.get_table("departments").delete(1, policy="RESTRICT")
except ValueError as e:
    print(f"RESTRICT захист спрацював: {e}")

# Видаляємо працівника (внутрішній ID 1), а потім відділ (внутрішній ID 1)
db.get_table("employees").delete(1)
db.get_table("departments").delete(1)
print("Працівника 101 та відділ IT успішно видалено.\n")

# 9. Збереження
db.save_to_json("backup.json")
print("Стан бази даних збережено у 'backup.json'.")