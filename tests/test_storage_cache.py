
import os
import shutil
import unittest
import sys
from types import ModuleType

# Mock dependencies
sys.modules['requests'] = ModuleType('requests')
sys.modules['bs4'] = ModuleType('bs4')
sys.modules['markdownify'] = ModuleType('markdownify')
sys.modules['git'] = ModuleType('git')
sys.modules['pandas'] = ModuleType('pandas')
sys.modules['streamlit'] = ModuleType('streamlit')

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core import storage

class TestStorageCache(unittest.TestCase):
    def setUp(self):
        # Setup test directories
        self.test_root = "test_cache_env"
        self.test_tasks_dir = os.path.join(self.test_root, "tasks")
        os.makedirs(self.test_tasks_dir, exist_ok=True)

        # Override storage constants for test
        self.orig_tasks_dir = storage.TASKS_DIR
        storage.TASKS_DIR = self.test_tasks_dir

        # Reset cache
        storage._TASKS_CACHE = []
        storage._TASKS_CACHE_MTIME = -1.0

    def tearDown(self):
        # Restore storage constants
        storage.TASKS_DIR = self.orig_tasks_dir
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_cache_is_effective(self):
        # 1. Create a task
        task_id = "test_task"
        task_data = {"id": task_id, "title": "Initial Title"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        # 2. First call (cold)
        tasks1 = storage.list_tasks()
        self.assertEqual(len(tasks1), 1)
        self.assertEqual(tasks1[0]["title"], "Initial Title")
        mtime1 = storage._TASKS_CACHE_MTIME

        # 3. Second call (warm) - should reuse cache
        tasks2 = storage.list_tasks()
        self.assertEqual(storage._TASKS_CACHE_MTIME, mtime1)
        self.assertEqual(tasks2[0]["title"], "Initial Title")

    def test_cache_invalidation_on_save(self):
        # 1. Create a task and load it
        task_id = "test_task"
        task_data = {"id": task_id, "title": "Initial Title"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)
        storage.list_tasks()

        # 2. Modify the task through save_json
        task_data["title"] = "Updated Title"
        storage.save_json(filepath, task_data)

        # 3. list_tasks should now reflect the update
        tasks = storage.list_tasks()
        self.assertEqual(tasks[0]["title"], "Updated Title")

    def test_cache_invalidation_on_delete(self):
        # 1. Create a task and load it
        task_id = "test_task"
        task_data = {"id": task_id, "title": "Initial Title"}
        storage.save_json(storage.get_task_path(task_id), task_data)
        storage.list_tasks()
        self.assertEqual(len(storage._TASKS_CACHE), 1)

        # 2. Delete the task
        storage.delete_task_file(task_id)

        # 3. list_tasks should now be empty
        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 0)

    def test_cache_returns_deep_copy(self):
        # 1. Create a task and load it
        task_id = "test_task"
        task_data = {"id": task_id, "title": "Initial Title"}
        storage.save_json(storage.get_task_path(task_id), task_data)
        tasks = storage.list_tasks()

        # 2. Mutate the returned object
        tasks[0]["title"] = "MUTATED"

        # 3. Fetch again, should NOT be mutated
        tasks_again = storage.list_tasks()
        self.assertEqual(tasks_again[0]["title"], "Initial Title")

if __name__ == "__main__":
    unittest.main()
