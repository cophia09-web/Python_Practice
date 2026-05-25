import asyncio
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from typing import List
from engine import process_worker, job_queue, job_store, store_lock, metrics

worker_tasks: list[asyncio.Task] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаємо рівно 4 воркер-задачі при старті
    for i in range(4):
        task = asyncio.create_task(process_worker(i))
        worker_tasks.append(task)
    yield
    # При зупинці скасовуємо всі задачі та чекаємо їх завершення
    for task in worker_tasks:
        task.cancel()
    await asyncio.gather(*worker_tasks, return_exceptions=True)

app = FastAPI(lifespan=lifespan)

@app.post("/submit", status_code=status.HTTP_202_ACCEPTED)
async def submit(file: UploadFile = File(...)):
    # Перевіряємо, чи не заповнена черга
    if job_queue.full():
        raise HTTPException(status_code=503, detail="Queue is full")

    image_bytes = await file.read()
    job_id = str(uuid.uuid4())

    async with store_lock:
        job_store[job_id] = {"status": "pending", "image_bytes": image_bytes}
        metrics["received"] += 1

    await job_queue.put(job_id)
    return {"job_id": job_id}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    async with store_lock:
        if job_id not in job_store:
            raise HTTPException(status_code=404, detail="Not found")
        return {"status": job_store[job_id]["status"]}

@app.get("/result/{job_id}")
async def get_result(job_id: str):
    async with store_lock:
        if job_id not in job_store:
            raise HTTPException(status_code=404, detail="Not found")
        job = job_store[job_id]
        if job["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"Job is still {job['status']}")
        return {"result": job["result"]}

@app.post("/batch")
async def submit_batch(files: List[UploadFile] = File(...)):
    # Надсилаємо кожен файл конкурентно
    tasks = [submit(f) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    formatted_results = []
    for res in results:
        if isinstance(res, Exception):
            formatted_results.append({"error": str(res)})
        else:
            formatted_results.append(res)
    return {"batch_results": formatted_results}

@app.get("/metrics")
async def get_metrics():
    async with store_lock:
        avg_time = 0
        if metrics["completed"] > 0:
            avg_time = metrics["total_processing_time"] / metrics["completed"]
            
        return {
            "received": metrics["received"],
            "completed": metrics["completed"],
            "failed": metrics["failed"],
            "queue_depth": job_queue.qsize(),
            "average_processing_time": round(avg_time, 4)
        }