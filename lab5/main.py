import time
import multiprocessing as mp
from sequential import run_sequential_task1, run_sequential_task2
from threaded import run_threaded
from multiprocessing_mod import run_multiprocessing

def benchmark_task1(n=40, runs=5):
    print("="*50)
    print("БЕНЧМАРК ЗАВДАННЯ 1 (I/O BOUND - ПОТОКИ)")
    print("="*50)
    
    seq_times = []
    thread_times = []
    
    for _ in range(runs):
        t0 = time.perf_counter()
        run_sequential_task1(n)
        seq_times.append(time.perf_counter() - t0)
        
        t0 = time.perf_counter()
        run_threaded(n)
        thread_times.append(time.perf_counter() - t0)
        
    avg_seq = sum(seq_times) / runs
    avg_thread = sum(thread_times) / runs
    speedup = avg_seq / avg_thread if avg_thread > 0 else float('inf')
    
    print(f"\n--- РЕЗУЛЬТАТИ ТЕСТУ 1 ---")
    print(f"Середній час (послідовно): {avg_seq:.2f} сек")
    print(f"Середній час (потоки):     {avg_thread:.2f} сек")
    print(f"Прискорення (Speedup):     {speedup:.2f}x\n")


def benchmark_task2(n=20, data_size=5_000_000, runs=5, max_workers=4):
    print("="*50)
    print("БЕНЧМАРК ЗАВДАННЯ 2 (CPU BOUND - ПРОЦЕСИ)")
    print("="*50)
    
    seq_times = []
    mp_times = []
    
    for _ in range(runs):
        t0 = time.perf_counter()
        run_sequential_task2(n, data_size)
        seq_times.append(time.perf_counter() - t0)
        
        t0 = time.perf_counter()
        run_multiprocessing(n, data_size, max_workers)
        mp_times.append(time.perf_counter() - t0)
        
    avg_seq = sum(seq_times) / runs
    avg_mp = sum(mp_times) / runs
    speedup = avg_seq / avg_mp if avg_mp > 0 else float('inf')
    
    print(f"\n--- РЕЗУЛЬТАТИ ТЕСТУ 2 ---")
    print(f"Середній час (послідовно): {avg_seq:.2f} сек")
    print(f"Середній час (процеси):    {avg_mp:.2f} сек")
    print(f"Прискорення (Speedup):     {speedup:.2f}x\n")

if __name__ == "__main__":
    # Уніфікована поведінка на всіх ОС (особливо важливо для Windows/macOS)
    mp.set_start_method("spawn", force=True) 
    
    benchmark_task1(n=40, runs=5)
    
    # Використовуємо 5_000_000, щоб обчислення гарантовано зайняли ~1-2 секунди на сучасних CPU
    benchmark_task2(n=20, data_size=5_000_000, runs=5, max_workers=4)