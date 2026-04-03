import os
import time
import json
import sys

sys.path.insert(0, ".")
from src.satya.core import storage

def setup_dummy_tasks(count=100):
    storage.ensure_satya_dirs()
    for i in range(count):
        task_id = f"bench_{i:04d}"
        path = storage.get_task_path(task_id)
        data = {
            "id": task_id,
            "title": f"Benchmark Task {i}",
            "status": "queued",
            "priority": "Medium",
            "updated_at": "2024-05-23T12:00:00Z"
        }
        with open(path, 'w') as f:
            json.dump(data, f)

def run_benchmark(iterations=10):
    print(f"Running benchmark with {iterations} iterations...")
    start_time = time.time()
    for _ in range(iterations):
        tasks = storage.list_tasks()
    end_time = time.time()
    avg_time = (end_time - start_time) / iterations
    print(f"Average time per list_tasks(): {avg_time:.4f}s")
    return avg_time

if __name__ == "__main__":
    # Cleanup old benchmark tasks
    if os.path.exists(storage.TASKS_DIR):
        for f in os.listdir(storage.TASKS_DIR):
            if f.startswith("bench_"):
                os.remove(os.path.join(storage.TASKS_DIR, f))

    setup_dummy_tasks(200)
    print("Baseline (Cold):")
    run_benchmark(5)

    # In a real scenario, subsequent calls in the same process would be "Warm"
    print("\nWarm (after potential caching):")
    run_benchmark(5)

    # Cleanup benchmark tasks
    if os.path.exists(storage.TASKS_DIR):
        for f in os.listdir(storage.TASKS_DIR):
            if f.startswith("bench_"):
                os.remove(os.path.join(storage.TASKS_DIR, f))
