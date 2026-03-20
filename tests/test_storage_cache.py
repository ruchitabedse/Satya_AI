
import unittest
import os
import shutil
import time
import sys

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core import storage

class TestStorageCache(unittest.TestCase):
    def setUp(self):
        # We need to use the real TASKS_DIR path logic but redirect it
        self.original_tasks_dir = storage.TASKS_DIR
        storage.TASKS_DIR = "test_tasks_cache"
        os.makedirs(storage.TASKS_DIR, exist_ok=True)
        # Reset cache state
        storage._TASKS_CACHE = []
        storage._TASKS_LAST_MTIME = -1.0

    def tearDown(self):
        if os.path.exists(storage.TASKS_DIR):
            shutil.rmtree(storage.TASKS_DIR)
        storage.TASKS_DIR = self.original_tasks_dir

    def test_list_tasks_caching(self):
        # Create a task
        task_id = "test1"
        task_data = {"id": task_id, "title": "Test Task 1"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        # First call should load from disk
        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Test Task 1")
        mtime_after_first = storage._TASKS_LAST_MTIME

        # Second call should use cache
        tasks2 = storage.list_tasks()
        self.assertEqual(len(tasks2), 1)
        self.assertEqual(storage._TASKS_LAST_MTIME, mtime_after_first)

        # Update task should invalidate cache (by changing directory mtime)
        # In many systems, os.rename updates parent dir mtime.
        time.sleep(0.1) # Ensure mtime changes if resolution is low
        task_data["title"] = "Updated Task 1"
        storage.save_json(filepath, task_data)

        tasks3 = storage.list_tasks()
        self.assertEqual(len(tasks3), 1)
        self.assertEqual(tasks3[0]["title"], "Updated Task 1")
        self.assertNotEqual(storage._TASKS_LAST_MTIME, mtime_after_first)

    def test_cache_returns_deep_copy(self):
        task_id = "test_copy"
        task_data = {"id": task_id, "title": "Original"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        tasks = storage.list_tasks()
        tasks[0]["title"] = "Mutated"

        # Call again, should still be "Original" if it was a deep copy
        tasks_again = storage.list_tasks()
        self.assertEqual(tasks_again[0]["title"], "Original")

    def test_delete_invalidates_cache(self):
        task_id = "test_del"
        task_data = {"id": task_id, "title": "Delete Me"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        self.assertEqual(len(storage.list_tasks()), 1)
        mtime_before = storage._TASKS_LAST_MTIME

        time.sleep(0.1)
        storage.delete_task_file(task_id)

        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 0)
        self.assertNotEqual(storage._TASKS_LAST_MTIME, mtime_before)

if __name__ == "__main__":
    unittest.main()
