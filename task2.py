"""
Модуль для керування телефонною книгою.
Використовує бінарний пошук для максимальної ефективності[cite: 15].
"""

import json
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

FILE_NAME = "phonebook.json"

def generate_and_save_data(count=1000):
    """
    Генерує випадкові контакти, сортує їх та зберігає в JSON[cite: 15].

    Args:
        count (int): Кількість контактів для генерації.
    """
    names = ["Moore", "Morse", "Moon", "Smith", "Taylor", "Anderson"]
    data = []
    
    for i in range(1, count + 1):
        data.append({
            "name": f"{random.choice(names)}_{i:03d}",
            "phone": f"+380{random.randint(50, 99)}{random.randint(1000000, 9999999)}"
        })
    
    # Сортування обов'язкове для бінарного пошуку [cite: 15]
    data.sort(key=lambda x: x["name"])
    
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info("Базу даних на 1000 номерів створено та відсортовано.")

def binary_search(target_name):
    """
    Виконує бінарний пошук контакту за іменем.

    Args:
        target_name (str): Ім'я для пошуку.

    Returns:
        tuple: (індекс, номер телефону) або (-1, None), якщо не знайдено.
    """
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            contacts = json.load(f)
            
        low = 0
        high = len(contacts) - 1
        
        while low <= high:
            mid = (low + high) // 2
            if contacts[mid]["name"] == target_name:
                return mid, contacts[mid]["phone"]
            elif contacts[mid]["name"] < target_name:
                low = mid + 1
            else:
                high = mid - 1
        return -1, None
    except FileNotFoundError:
        return -1, None

if __name__ == "__main__":
    generate_and_save_data()
    name = "Moore_050"
    idx, phone = binary_search(name)
    if idx != -1:
        logger.info(f"Знайдено {name} на індексі {idx}. Телефон: {phone}")
    else:
        logger.warning(f"Контакт {name} не знайдено.")