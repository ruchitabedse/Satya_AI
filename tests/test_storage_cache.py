
import os
import sys
import unittest
import shutil
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core import storage

class TestStorageCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_cache_dir"
        os.makedirs(self.test_dir, exist_ok=True)
        self.tasks_dir = os.path.join(self.test_dir, "tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)

        # Patch storage constants
        self.orig_tasks_dir = storage.TASKS_DIR
        storage.TASKS_DIR = self.tasks_dir

        # Reset cache
        storage._tasks_cache_mtime = -1.0
        storage._tasks_cache = []

    def tearDown(self):
        storage.TASKS_DIR = self.orig_tasks_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache_hits(self):
        # Create a task
        task = {"id": "t1", "title": "Task 1"}
        path = os.path.join(self.tasks_dir, "t1.json")
        storage.save_json(path, task)

        # First call should load from disk
        tasks1 = storage.list_tasks()
        self.assertEqual(len(tasks1), 1)
        self.assertEqual(tasks1[0]["id"], "t1")

        # Second call should be a cache hit
        tasks2 = storage.list_tasks()
        self.assertEqual(tasks1, tasks2)

    def test_cache_invalidation_on_save(self):
        # Create initial task
        task1 = {"id": "t1", "title": "Task 1"}
        storage.save_json(os.path.join(self.tasks_dir, "t1.json"), task1)

        # Load and cache
        storage.list_tasks()
        self.assertEqual(len(storage._tasks_cache), 1)

        # Save another task
        task2 = {"id": "t2", "title": "Task 2"}
        storage.save_json(os.path.join(self.tasks_dir, "t2.json"), task2)

        # Cache should be invalidated (mtime reset)
        self.assertEqual(storage._tasks_cache_mtime, -1.0)

        # Next list_tasks should see both
        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 2)

    def test_cache_deep_copy(self):
        task = {"id": "t1", "title": "Task 1"}
        storage.save_json(os.path.join(self.tasks_dir, "t1.json"), task)

        tasks = storage.list_tasks()
        tasks[0]["title"] = "MUTATED"

        # Verify cache wasn't mutated
        tasks_again = storage.list_tasks()
        self.assertEqual(tasks_again[0]["title"], "Task 1")

if __name__ == "__main__":
    unittest.main()
