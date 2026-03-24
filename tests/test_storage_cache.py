import os
import shutil
import unittest
import json
import sys
import time
from types import ModuleType

# Mock 'requests' and other potentially missing dependencies
sys.modules['requests'] = ModuleType('requests')
bs4_mock = ModuleType('bs4')
from unittest.mock import MagicMock
bs4_mock.BeautifulSoup = MagicMock()
sys.modules['bs4'] = bs4_mock
sys.modules['markdownify'] = ModuleType('markdownify')
sys.modules['git'] = ModuleType('git')
sys.modules['pandas'] = ModuleType('pandas')
sys.modules['streamlit'] = ModuleType('streamlit')

# Ensure src is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import satya.core.storage as storage

class TestStorageCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.abspath("test_cache_dir")
        os.makedirs(self.test_dir, exist_ok=True)
        self.tasks_dir = os.path.join(self.test_dir, "tasks")
        os.makedirs(self.tasks_dir, exist_ok=True)

        # Patch storage directories
        self.orig_tasks_dir = storage.TASKS_DIR
        storage.TASKS_DIR = self.tasks_dir

        # Reset cache
        storage._tasks_cache = []
        storage._tasks_cache_mtime = -1.0

    def tearDown(self):
        storage.TASKS_DIR = self.orig_tasks_dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cache_functionality(self):
        # 1. Create a task
        task_id = "task1"
        task_data = {"id": task_id, "title": "Test Task"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        # 2. List tasks (should populate cache)
        tasks = storage.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Test Task")

        # 3. Modify the returned task (should NOT affect the cache due to deepcopy)
        tasks[0]["title"] = "Modified"

        # 4. List tasks again (should come from cache)
        tasks2 = storage.list_tasks()
        self.assertEqual(tasks2[0]["title"], "Test Task")

        # 5. Update task via save_json (should invalidate cache)
        task_data["title"] = "Updated Task"
        storage.save_json(filepath, task_data)

        # 6. List tasks again (should be updated)
        tasks3 = storage.list_tasks()
        self.assertEqual(tasks3[0]["title"], "Updated Task")

    def test_cache_invalidation_on_delete(self):
        # 1. Create a task
        task_id = "task1"
        task_data = {"id": task_id, "title": "Test Task"}
        filepath = storage.get_task_path(task_id)
        storage.save_json(filepath, task_data)

        # 2. List tasks
        self.assertEqual(len(storage.list_tasks()), 1)

        # 3. Delete the task
        storage.delete_task_file(task_id)

        # 4. List tasks (should be empty)
        self.assertEqual(len(storage.list_tasks()), 0)

if __name__ == "__main__":
    unittest.main()
