"""
Модуль для дешифрування шифру Цезаря зі зростаючим зсувом.
Використовує алфавіт із 36 символів та перевірку анаграм[cite: 21, 24].
"""

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

ABC = "abcdefghijklmnopqrstuvwxyz0123456789" # Алфавіт [cite: 24]

def decrypt_text(text, base):
    """
    Розшифровує текст за алгоритмом зростаючого зсуву[cite: 35, 43].

    Args:
        text (str): Зашифрований рядок.
        base (int): Початковий зсув.

    Returns:
        str: Розшифрований рядок.
    """
    result = ""
    for i in range(len(text)):
        # Позиція в алфавіті без ord() [cite: 77]
        pos = ABC.find(text[i])
        # Зсув збільшується для кожного символу [cite: 36]
        current_shift = (base + i) % 36
        # Рух назад для дешифрування [cite: 45]
        new_pos = (pos - current_shift) % 36
        result += ABC[new_pos]
    return result

def check_keys(decrypted_text, key_strings):
    """
    Перевіряє наявність анаграм ключових рядків у тексті[cite: 59, 63].

    Args:
        decrypted_text (str): Текст для перевірки.
        key_strings (list): Список ключів.

    Returns:
        list: Індекси знайдених ключів або порожній список.
    """
    found_indices = []
    for key in key_strings:
        sorted_key = sorted(key)
        k_len = len(key)
        for i in range(len(decrypted_text) - k_len + 1):
            chunk = decrypted_text[i : i + k_len]
            if sorted(chunk) == sorted_key: # Перевірка частот символів [cite: 22, 63]
                found_indices.append(i)
                break
    return found_indices

def solve_caesar(encrypted_text, key_strings):
    """
    Перебирає всі можливі бази для знаходження правильної[cite: 68].
    """
    for base in range(36): # Ефективних зсувів лише 36 [cite: 51]
        decrypted = decrypt_text(encrypted_text, base)
        indices = check_keys(decrypted, key_strings)
        
        if len(indices) == len(key_strings):
            logger.info(f"Знайдено! Base: {base}")
            logger.info(f"Текст: {decrypted}")
            logger.info(f"Індекси: {indices}")
            return base, decrypted, indices

if __name__ == "__main__":
    solve_caesar("3mumzyrg4eaz77o4ahge", ["3noypth", "2emlweoc"])