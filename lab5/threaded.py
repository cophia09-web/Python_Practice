import time
import threading
from simulator import drone_task

def worker_thread(drone_id: int, results: list, upload_sem: threading.Semaphore, 
                  results_lock: threading.Lock, print_lock: threading.Lock):
    
    res = drone_task(drone_id, upload_sem)
    
    with print_lock:
        if res:
            print(f"Дрон {drone_id}: дані успішно завантажено.")
        else:
            print(f"Дрон {drone_id}: помилка зв'язку!")
            
    if res is not None:
        with results_lock:
            results.append(res)

def run_threaded(n: int) -> list:
    results = []
    threads = []
    
    # Синхронізація
    upload_sem = threading.Semaphore(3) # Максимум 3 одночасні передачі
    results_lock = threading.Lock()     # Захист списку результатів
    print_lock = threading.Lock()       # Читабельний вивід у консоль
    
    print(f"\n--- Запуск багатопоточної версії (Завдання 1), Дронів: {n} ---")
    for i in range(1, n + 1):
        t = threading.Thread(target=worker_thread, args=(i, results, upload_sem, results_lock, print_lock))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    return results