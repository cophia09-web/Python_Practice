import time
import multiprocessing as mp
from simulator import onboard_analysis

def worker_process(drone_id: int, data_size: int, sem: mp.Semaphore, q: mp.Queue, lock: mp.Lock):
    # Обмежуємо кількість одночасних обчислень
    with sem:
        with lock:
            print(f"Дрон {drone_id}: почав обчислення...")
            
        result = onboard_analysis(drone_id, data_size)
        
        with lock:
            print(f"Дрон {drone_id}: завершив обчислення")
            
        # Безпечна передача результату в батьківський процес
        q.put(result)

def run_multiprocessing(n: int, data_size: int, max_workers: int = 4) -> list:
    results = []
    
    # Синхронізація
    sem = mp.Semaphore(max_workers)
    lock = mp.Lock()
    q = mp.Queue()
    processes = []
    
    print(f"\n--- Запуск багатопроцесної версії (Завдання 2), Дронів: {n} ---")
    
    for i in range(1, n + 1):
        p = mp.Process(target=worker_process, args=(i, data_size, sem, q, lock))
        processes.append(p)
        p.start()
        
    # Чекаємо завершення всіх процесів
    for p in processes:
        p.join()
        
    # Збираємо результати з черги
    while not q.empty():
        results.append(q.get())
        
    return results