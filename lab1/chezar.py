def crack_caesar(ciphertext, keys):
    """
    Розшифровує текст, зашифрований модифікованим шифром Цезаря.

    Алгоритм перевіряє всі можливі початкові зсуви (від 0 до 35) та 
    шукає такий зсув, за якого розшифрований текст містить усі вказані 
    ключові рядки у вигляді анаграм.

    Args:
        ciphertext (str): Зашифрований текст, що складається з літер та цифр.
        keys (list of str): Список ключових рядків для пошуку в тексті.

    Returns:
        tuple: Кортеж із трьох елементів:
            - int: Знайдений початковий зсув (base).
            - str: Повністю розшифрований текст.
            - dict: Словник з індексами знайдених ключів.
            Якщо правильного зсуву не знайдено, повертає (None, None, None).
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    alphabet_len = 36
    
    def is_anagram(window, key_sorted):
        """
        Перевіряє, чи є рядок анаграмою ключа.
        
        Args:
            window (str): Фрагмент тексту для перевірки.
            key_sorted (list): Відсортований список символів ключа.
            
        Returns:
            bool: True, якщо рядок є анаграмою, інакше False.
        """
        return sorted(window) == key_sorted

    for base in range(alphabet_len):
        decrypted_chars = []
        
        for i, char in enumerate(ciphertext):
            if char not in alphabet:
                continue
            
            shift = base + i
            current_pos = alphabet.index(char)
            original_pos = (current_pos - shift) % alphabet_len
            decrypted_chars.append(alphabet[original_pos])
            
        decrypted_text = "".join(decrypted_chars)
        
        all_keys_found = True
        key_indices = {}
        
        for key in keys:
            key_sorted = sorted(key)
            key_len = len(key)
            found_indices = []
            
            for i in range(len(decrypted_text) - key_len + 1):
                window = decrypted_text[i:i + key_len]
                if is_anagram(window, key_sorted):
                    found_indices.append(i)
            
            if not found_indices:
                all_keys_found = False
                break
            else:
                key_indices[key] = found_indices
                
        if all_keys_found:
            return base, decrypted_text, key_indices
            
    return None, None, None

base, decrypted, indices = crack_caesar("kos0kw62rzz", ["opyhtn"])
if base is not None:
    print(f"Base: {base} | Розшифрований текст: {decrypted} | Індекси ключів: {indices}")



if __name__ == "__main__":
    user_cipher = input("Введіть зашифрований текст: ")
    user_keys_input = input("Введіть ключі (через пробіл): ")
    user_keys = user_keys_input.split()
    
    base, decrypted, indices = crack_caesar(user_cipher, user_keys)
    
    if base is not None:
        print(f"Значення Base: {base}")
        print(f"Розшифрований текст: {decrypted}")
        print(f"Індекси знайдених ключів: {indices}")
    else:
        print("Не вдалося знайти правильний зсув для цих ключів.")