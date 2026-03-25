import os
import sys
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from satya.core import storage

def test_cache_invalidation():
    # Setup - use a temporary task directory for isolated testing
    TEST_DIR = "satya_data/test_tasks"
    os.makedirs(TEST_DIR, exist_ok=True)

    # Monkeypatch TASKS_DIR
    original_tasks_dir = storage.TASKS_DIR
    storage.TASKS_DIR = TEST_DIR

    # Clear existing cache
    storage._TASKS_CACHE["mtime"] = -1.0
    storage._TASKS_CACHE["tasks"] = []

    try:
        # Create 5 tasks
        for i in range(5):
            filepath = os.path.join(TEST_DIR, f"test_{i}.json")
            storage.save_json(filepath, {"id": f"test_{i}", "val": i})

        # 1. Fill cache
        tasks1 = storage.list_tasks()
        print(f"Loaded {len(tasks1)} tasks into cache")
        assert len(tasks1) == 5

        # 2. Save new task (should invalidate cache)
        new_filepath = os.path.join(TEST_DIR, "test_new.json")
        storage.save_json(new_filepath, {"id": "test_new", "val": 100})

        tasks2 = storage.list_tasks()
        print(f"Reloaded {len(tasks2)} tasks after save")
        assert len(tasks2) == 6

        # 3. Delete task (should invalidate cache)
        os.remove(new_filepath)
        storage._TASKS_CACHE["mtime"] = -1.0 # Simulate what delete_task_file does but with our custom path

        tasks3 = storage.list_tasks()
        print(f"Reloaded {len(tasks3)} tasks after delete")
        assert len(tasks3) == 5

        # 4. Check deep copy (modifying returned list should not affect cache)
        tasks3[0]["val"] = "polluted"
        tasks4 = storage.list_tasks()
        assert tasks4[0]["val"] != "polluted"
        print("Deep copy integrity verified")

    finally:
        # Cleanup
        shutil.rmtree(TEST_DIR)
        storage.TASKS_DIR = original_tasks_dir

if __name__ == "__main__":
    test_cache_invalidation()
