import os
import shutil
import unittest
import sys
from types import ModuleType
from unittest.mock import MagicMock

# Mock Streamlit and other UI-related modules
sys.modules['streamlit'] = ModuleType('streamlit')
sys.modules['pandas'] = ModuleType('pandas')
sys.modules['git'] = ModuleType('git')

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from satya.core import storage

class TestStorageCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_satya_data_cache"
        storage.SATYA_DIR = self.test_dir
        storage.TASKS_DIR = os.path.join(self.test_dir, "tasks")
        storage.TRUTH_DIR = os.path.join(self.test_dir, "truth")
        storage.AGENTS_DIR = os.path.join(self.test_dir, "agents")

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        storage.ensure_satya_dirs()
        # Reset cache
        storage._tasks_cache = {}

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache_functionality(self):
        # 1. Initially empty
        self.assertEqual(len(storage.list_tasks()), 0)

        # 2. Add a task
        task_id = "task1"
        task_data = {"id": task_id, "title": "Test Task"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        # 3. Read back - should be in list
        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Test Task")

        # 4. Modify returned list - should NOT affect cache
        tasks[0]["title"] = "Modified"

        # 5. Read back again - should still be original due to deepcopy
        tasks2 = storage.list_tasks()
        self.assertEqual(tasks2[0]["title"], "Test Task")

        # 6. Update file - cache should invalidate
        task_data["title"] = "Updated Task"
        storage.save_json(filepath, task_data)

        tasks3 = storage.list_tasks()
        self.assertEqual(len(tasks3), 1)
        self.assertEqual(tasks3[0]["title"], "Updated Task")

    def test_cache_invalidation_on_delete(self):
        task_id = "task1"
        storage.save_json(storage.get_task_path(task_id), {"id": task_id})

        self.assertEqual(len(storage.list_tasks()), 1)

        storage.delete_task_file(task_id)

        self.assertEqual(len(storage.list_tasks()), 0)

if __name__ == "__main__":
    unittest.main()
