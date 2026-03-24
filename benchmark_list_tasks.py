import os
import time
import sys
import json
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from satya.core import storage

def setup_benchmark_data(num_tasks=500):
    storage.ensure_satya_dirs()
    print(f"Creating {num_tasks} tasks...")
    for i in range(num_tasks):
        task_id = str(uuid.uuid4())[:8]
        task = {
            "id": task_id,
            "title": f"Task {i}",
            "description": f"Description for task {i}",
            "status": "queued",
            "priority": "Medium",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        storage.save_json(storage.get_task_path(task_id), task)

def run_benchmark(iterations=10):
    print(f"Running benchmark with {iterations} iterations...")
    start_time = time.time()
    for _ in range(iterations):
        tasks = storage.list_tasks()
    end_time = time.time()
    avg_time = (end_time - start_time) / iterations
    print(f"Average time for list_tasks: {avg_time*1000:.2f}ms")
    return avg_time

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_benchmark_data()

    run_benchmark()
