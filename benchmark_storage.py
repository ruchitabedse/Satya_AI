import os
import sys
import time
import shutil
import json
import uuid

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from satya.core import storage

def benchmark():
    # Setup test environment
    test_tasks_dir = "benchmark_tasks"
    if os.path.exists(test_tasks_dir):
        shutil.rmtree(test_tasks_dir)
    os.makedirs(test_tasks_dir)

    # Override TASKS_DIR for benchmarking
    storage.TASKS_DIR = test_tasks_dir

    # Create 100 dummy tasks with many comments/audit events
    print("Creating 100 large dummy tasks...")
    for i in range(100):
        task_id = str(uuid.uuid4())[:8]
        task_data = {
            "id": task_id,
            "title": f"Task {i}",
            "description": "A very long description " * 10,
            "comments": [{"text": "comment " * 20} for _ in range(20)],
            "audit_trail": [{"details": "audit " * 20} for _ in range(20)]
        }
        with open(os.path.join(test_tasks_dir, f"{task_id}.json"), 'w') as f:
            json.dump(task_data, f)

    # Reset cache
    storage._TASK_CACHE["mtime"] = -1
    storage._TASK_CACHE["tasks"] = []

    # Benchmark Cold Read (Cache Miss)
    start_time = time.perf_counter()
    tasks_cold = storage.list_tasks()
    end_time = time.perf_counter()
    cold_time = (end_time - start_time) * 1000
    print(f"Cold Read (Cache Miss): {cold_time:.2f} ms")

    # Benchmark Warm Read (Cache Hit)
    start_time = time.perf_counter()
    tasks_warm = storage.list_tasks()
    end_time = time.perf_counter()
    warm_time = (end_time - start_time) * 1000
    print(f"Warm Read (Cache Hit): {warm_time:.2f} ms")

    # Benchmark after modification (Cache Invalidation)
    time.sleep(1) # Ensure mtime changes
    task_id = "new_task"
    with open(os.path.join(test_tasks_dir, f"{task_id}.json"), 'w') as f:
        json.dump({"id": task_id, "title": "New Task"}, f)

    start_time = time.perf_counter()
    tasks_new = storage.list_tasks()
    end_time = time.perf_counter()
    new_time = (end_time - start_time) * 1000
    print(f"Read after modification (Cache Invalidation): {new_time:.2f} ms")

    print(f"Speedup: {cold_time / warm_time:.1f}x")

    # Cleanup
    shutil.rmtree(test_tasks_dir)

if __name__ == "__main__":
    benchmark()
