import time
from simulator import drone_task, onboard_analysis

def run_sequential_task1(n: int) -> list:
    results = []
    print(f"\n--- Запуск послідовної версії (Завдання 1), Дронів: {n} ---")
    for i in range(1, n + 1):
        res = drone_task(i)
        if res is not None:
            results.append(res)
    return results

def run_sequential_task2(n: int, data_size: int) -> list:
    results = []
    print(f"\n--- Запуск послідовної версії (Завдання 2), Дронів: {n} ---")
    for i in range(1, n + 1):
        res = onboard_analysis(i, data_size)
        results.append(res)
    return results