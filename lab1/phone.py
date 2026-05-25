import json
import random

def generate_phonebook(filename="phonebook.json"):
    """
    Генерує JSON файл з тестовою телефонною книгою на 1000 записів.

    Створює список словників, де кожен словник містить випадкове ім'я 
    із заданого списку та згенерований номер телефону. Список сортується 
    за ім'ям і зберігається у вказаний файл.

    Args:
        filename (str, optional): Ім'я файлу для збереження даних. 
            За замовчуванням "phonebook.json".
    """
    names = ["Moore", "Moon", "Morse", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]
    phonebook = []
    
    for _ in range(1000):
        name = random.choice(names)
        number = f"+380{random.randint(100000000, 999999999)}"
        phonebook.append({"name": name, "phone": number})
    
    phonebook.sort(key=lambda x: x["name"])
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(phonebook, f, indent=4)

class TreeNode:
    """
    Вузол бінарного дерева пошуку, що представляє запис у телефонній книзі.

    Attributes:
        name (str): Ім'я контакту (ключ для пошуку).
        phones (list of tuple): Список кортежів (телефон, оригінальний_індекс) 
            для зберігання дублікатів імен.
        left (TreeNode or None): Посилання на лівий дочірній вузол.
        right (TreeNode or None): Посилання на правильний дочірній вузол.
    """
    def __init__(self, name, phone, index):
        """
        Ініціалізує новий вузол дерева.

        Args:
            name (str): Ім'я контакту.
            phone (str): Номер телефону.
            index (int): Початковий індекс запису в JSON масиві.
        """
        self.name = name
        self.phones = [(phone, index)]
        self.left = None
        self.right = None

class PhonebookBST:
    """
    Реалізація бінарного дерева пошуку (BST) для телефонної книги.

    Дозволяє додавати та шукати контакти за їхнім ім'ям.
    """
    def __init__(self):
        """Ініціалізує порожнє бінарне дерево."""
        self.root = None

    def insert(self, name, phone, index):
        """
        Додає новий запис контакту в дерево.

        Якщо вузол із таким ім'ям вже існує, номер телефону та індекс 
        додаються до списку phones цього вузла. В іншому випадку 
        створюється новий вузол у відповідній позиції дерева.

        Args:
            name (str): Ім'я контакту.
            phone (str): Номер телефону.
            index (int): Початковий індекс запису в JSON масиві.
        """
        if not self.root:
            self.root = TreeNode(name, phone, index)
            return
        
        current = self.root
        while True:
            if name == current.name:
                current.phones.append((phone, index))
                break
            elif name < current.name:
                if current.left is None:
                    current.left = TreeNode(name, phone, index)
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = TreeNode(name, phone, index)
                    break
                current = current.right

    def search(self, name):
        """
        Шукає контакт за ім'ям у дереві.

        Args:
            name (str): Ім'я для пошуку.

        Returns:
            list of tuple or None: Список кортежів (номер_телефону, індекс), 
            якщо ім'я знайдено, інакше None.
        """
        current = self.root
        while current:
            if name == current.name:
                return current.phones
            elif name < current.name:
                current = current.left
            else:
                current = current.right
        return None

generate_phonebook()

with open("phonebook.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Побудова дерева
bst = PhonebookBST()
for i, record in enumerate(data):
    bst.insert(record["name"], record["phone"], i)

# Пошук та вивід результатів
results = bst.search("Moore")
if results:
    for phone, idx in results:
        print(f"Індекс: {idx} | Телефон: {phone}")