import time
import random

def drone_task(drone_id: int, upload_sem=None) -> dict | None:
    """Імітація збору даних дроном (I/O-bound)"""
    # 1. Політ до зони (0.3 - 1.0 сек)
    time.sleep(random.uniform(0.3, 1.0))
    
    # 2. Зчитування даних з датчиків (0.3 - 1.0 сек)
    time.sleep(random.uniform(0.3, 1.0))
    
    # 3. Завантаження на сервер з імітацією ймовірності помилки 15%
    if random.random() < 0.15:
        return None
    
    upload_time = random.uniform(0.2, 0.5)
    
    # Використовуємо семафор для обмеження каналу, якщо він переданий
    if upload_sem:
        with upload_sem:
            time.sleep(upload_time)
    else:
        time.sleep(upload_time)
        
    return {"drone_id": drone_id, "data": random.uniform(10, 35), "status": "ok"}

def onboard_analysis(drone_id: int, data_size: int) -> dict:
    """Імітація важких обчислень на борту (CPU-bound)"""
    score = 0.0
    # Навантажуємо процесор математичними операціями
    for i in range(data_size):
        score += (i * 0.01) ** 0.5
        
    return {"drone_id": drone_id, "score": score, "iterations": data_size, "status": "ok"}