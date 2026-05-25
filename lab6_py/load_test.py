import asyncio
import httpx
import time
from PIL import Image
import io

API_URL = "http://127.0.0.1:8000"

async def submit_one(client, image_bytes, results):
    files = {'file': ('test.jpg', image_bytes, 'image/jpeg')}
    try:
        response = await client.post(f"{API_URL}/submit", files=files)
        if response.status_code == 202:
            results.append({"job_id": response.json()["job_id"], "status": "submitted"})
        elif response.status_code == 503:
            results.append({"status": "rejected_503"})
        else:
            results.append({"status": f"error_{response.status_code}"})
    except Exception as e:
         results.append({"status": "connection_error"})

async def poll_until_done(client, job_id, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = await client.get(f"{API_URL}/status/{job_id}")
            if response.status_code == 200:
                status = response.json()["status"]
                if status in ["completed", "failed"]:
                    return status
        except:
            pass
        await asyncio.sleep(1)
    return "timeout"

async def main():
    # Створюємо тестове зображення в пам'яті (червоний квадрат)
    img = Image.new('RGB', (224, 224), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()

    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Надсилаємо 40 запитів...")
        start_time = time.time()
        
        tasks = [submit_one(client, image_bytes, results) for _ in range(40)]
        await asyncio.gather(*tasks)

        accepted = [r for r in results if r["status"] == "submitted"]
        rejected = [r for r in results if r["status"] == "rejected_503"]
        
        print(f"Прийнято: {len(accepted)}, Відхилено (503): {len(rejected)}")

        print("Опитуємо статуси прийнятих завдань...")
        poll_tasks = [poll_until_done(client, r["job_id"]) for r in accepted]
        final_statuses = await asyncio.gather(*poll_tasks)

        completed = final_statuses.count("completed")
        print(f"Завершено: {completed}. Загальний час тесту: {round(time.time() - start_time, 2)} с.")

if __name__ == "__main__":
    asyncio.run(main())