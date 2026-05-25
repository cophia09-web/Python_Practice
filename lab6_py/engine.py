import asyncio
import time
from typing import Any
from classifier import classify_image

# Спільний стан
job_queue: asyncio.Queue = asyncio.Queue(maxsize=50)
job_store: dict[str, dict] = {}
store_lock: asyncio.Lock = asyncio.Lock()
inference_semaphore: asyncio.Semaphore = asyncio.Semaphore(4)

# Словник для метрик
metrics: dict[str, Any] = {
    "received": 0,
    "completed": 0,
    "failed": 0,
    "total_processing_time": 0.0
}

async def process_worker(worker_id: int) -> None:
    while True:
        job_id = None
        try:
            # Чекаємо завдання з черги
            job_id = await job_queue.get()

            # Оновлюємо статус під замком (lock)
            async with store_lock:
                job_store[job_id]["status"] = "processing"
                image_bytes = job_store[job_id]["image_bytes"]

            start_time = time.monotonic()

            # Обмежуємо кількість одночасних інференсів
            async with inference_semaphore:
                # Виносимо CPU-bound функцію в окремий потік
                class_name, confidence = await asyncio.to_thread(classify_image, image_bytes)

            processing_time = time.monotonic() - start_time

            # Зберігаємо результат успішної обробки
            async with store_lock:
                job_store[job_id]["status"] = "completed"
                job_store[job_id]["result"] = {"class": class_name, "confidence": confidence}
                job_store[job_id].pop("image_bytes", None) # Звільняємо пам'ять
                metrics["completed"] += 1
                metrics["total_processing_time"] += processing_time

        except asyncio.CancelledError:
            # Придушувати CancelledError — помилка, тому піднімаємо виняток далі
            raise
        except Exception as exc:
            # Обробка інших помилок під час інференсу
            if job_id:
                async with store_lock:
                    job_store[job_id]["status"] = "failed"
                    job_store[job_id]["error"] = str(exc)
                    job_store[job_id].pop("image_bytes", None)
                    metrics["failed"] += 1
        finally:
            # Завжди повідомляємо чергу про завершення завдання
            if job_id:
                job_queue.task_done()