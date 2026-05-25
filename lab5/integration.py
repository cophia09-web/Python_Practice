import time
import threading
import multiprocessing as mp
from simulator import drone_task, onboard_analysis

# --- Етап 1: Потоки збору даних ---
def flight_worker(drone_id: int, upload_sem: threading.Semaphore, ingestion_q: mp.Queue):
    # Виконуємо імітацію польоту та збору
    res = drone_task(drone_id, upload_sem)
    if res is not None:
        # Кладемо "сирі" дані в Ingestion Queue
        ingestion_q.put(res)

# --- Етап 2: Процеси аналітики ---
def analysis_worker(cpu_sem: mp.Semaphore, ingestion_q: mp.Queue, results_q: mp.Queue, data_size: int):
    while True:
        # Читаємо з Ingestion Queue
        raw_data = ingestion_q.get()
        if raw_data is None:  # Сигнал про завершення роботи (Poison pill)
            break
            
        drone_id = raw_data["drone_id"]
        
        # Обмежуємо кількість одночасних обчислень ядер
        with cpu_sem:
            res = onboard_analysis(drone_id, data_size)
            # Додаємо оригінальні дані до результату
            res["raw_data"] = raw_data["data"]
            
        # Розміщення результатів в Results Queue
        results_q.put(res)

# --- Головний координатор ---
def run_integrated_system(n_drones=20, data_size=5_000_000, n_processes=4):
    print("=== ЗАПУСК ІНТЕГРОВАНОЇ СИСТЕМИ (ЗАВДАННЯ 3) ===")
    t0 = time.perf_counter()
    
    upload_sem = threading.Semaphore(3)
    cpu_sem = mp.Semaphore(n_processes)
    
    ingestion_q = mp.Queue()
    results_q = mp.Queue()
    
    # Запуск процесів-аналітиків (Етап 2)
    processes = []
    for _ in range(n_processes):
        p = mp.Process(target=analysis_worker, args=(cpu_sem, ingestion_q, results_q, data_size))
        p.start()
        processes.append(p)
        
    # Запуск потоків-дронів (Етап 1)
    threads = []
    for i in range(1, n_drones + 1):
        t = threading.Thread(target=flight_worker, args=(i, upload_sem, ingestion_q))
        t.start()
        threads.append(t)
        
    # Чекаємо, поки всі дрони завершать "політ і передачу"
    for t in threads:
        t.join()
        
    # Відправляємо "отруйну пігулку" (None) процесам, щоб вони зупинились
    for _ in range(n_processes):
        ingestion_q.put(None)
        
    # Чекаємо завершення обчислень
    for p in processes:
        p.join()
        
    # Етап 3: Агрегація
    results = []
    while not results_q.empty():
        results.append(results_q.get())
        
    duration = time.perf_counter() - t0
    
    print("\n--- ЗВІТ ---")
    print(f"Загальний час виконання: {duration:.2f} сек")
    print(f"Успішно зібрано та проаналізовано даних: {len(results)}/{n_drones}")
    for r in results[:3]: # Виводимо перші 3 для прикладу
        print(f"Дрон {r['drone_id']} | Оцінка: {r['score']:.2f} | Сирі дані: {r['raw_data']:.2f}")
    if len(results) > 3:
        print("...")

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    run_integrated_system(n_drones=20)