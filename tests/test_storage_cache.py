import os
import shutil
import unittest
import json
import sys

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core.storage import save_json, list_tasks, get_task_path, TASKS_DIR, delete_task_file

class TestStorageCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = "satya_data"
        self.tasks_dir = "satya_data/tasks"
        os.makedirs(self.tasks_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache_cloning(self):
        # Create a task
        task_id = "cache_test"
        task_path = get_task_path(task_id)
        task_data = {"id": task_id, "title": "Cache Test"}
        save_json(task_path, task_data)

        # Load tasks (should populate cache)
        tasks1 = list_tasks()
        self.assertEqual(len(tasks1), 1)
        self.assertEqual(tasks1[0]["title"], "Cache Test")

        # Mutate the returned object
        tasks1[0]["title"] = "MUTATED"

        # Load again (should come from cache)
        tasks2 = list_tasks()
        self.assertEqual(tasks2[0]["title"], "Cache Test", "Cache was mutated!")

    def test_cache_invalidation_on_save(self):
        # Initial load
        list_tasks()

        # Save a new task
        task_id = "new_task"
        task_path = get_task_path(task_id)
        save_json(task_path, {"id": task_id, "title": "New Task"})

        # Load again
        tasks = list_tasks()
        self.assertTrue(any(t["id"] == "new_task" for t in tasks), "Cache not invalidated on save!")

    def test_cache_invalidation_on_delete(self):
        # Create and load
        task_id = "delete_me"
        task_path = get_task_path(task_id)
        save_json(task_path, {"id": task_id, "title": "Delete Me"})
        list_tasks()

        # Delete task
        delete_task_file(task_id)

        # Load again
        tasks = list_tasks()
        self.assertFalse(any(t["id"] == "delete_me" for t in tasks), "Cache not invalidated on delete!")

if __name__ == "__main__":
    unittest.main()
