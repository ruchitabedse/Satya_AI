import os
import json
import fcntl
import logging
import copy
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# In-memory cache for tasks to avoid N+1 disk I/O in the flat-file architecture
_tasks_cache: List[Dict[str, Any]] = []
_tasks_cache_mtime: float = -1.0

SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")

def ensure_satya_dirs() -> None:
    os.makedirs(TASKS_DIR, exist_ok=True)
    os.makedirs(TRUTH_DIR, exist_ok=True)
    os.makedirs(AGENTS_DIR, exist_ok=True)

def save_json(filepath: str, data: Any) -> bool:
    tmp_filepath = filepath + ".tmp"
    lock_filepath = filepath + ".lock"

    try:
        # Create a separate lock file
        with open(lock_filepath, 'w') as lock_f:
            # Acquire exclusive lock
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                # Write to temp file
                with open(tmp_filepath, 'w') as tmp_f:
                    json.dump(data, tmp_f, indent=4)

                # Atomic rename
                os.rename(tmp_filepath, filepath)

                # ⚡ Bolt Optimization:
                # Invalidate the in-memory task cache if we just saved a task
                if filepath.startswith(TASKS_DIR):
                    global _tasks_cache_mtime
                    _tasks_cache_mtime = -1.0

                return True
            finally:
                # Release lock
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        # Clean up tmp file if rename failed
        if os.path.exists(tmp_filepath):
            try:
                os.remove(tmp_filepath)
            except Exception:
                pass
        return False

def load_json(filepath: str) -> Dict[str, Any]:
    if not os.path.exists(filepath):
        return {}

    lock_filepath = filepath + ".lock"

    try:
        # We need to lock while reading to avoid reading an incomplete file
        # Even with atomic rename, it's safer to acquire a shared lock
        with open(lock_filepath, 'a+') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_SH)
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return {}

def save_markdown(filename: str, content: str) -> Optional[str]:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        logger.error(f"Error saving markdown to {filepath}: {e}")
        return None

def list_truth_files() -> List[str]:
    if not os.path.exists(TRUTH_DIR):
        return []
    return [f for f in os.listdir(TRUTH_DIR) if f.endswith('.md')]

def get_task_path(task_id: str) -> str:
    safe_task_id = os.path.basename(task_id)
    return os.path.join(TASKS_DIR, f"{safe_task_id}.json")

def list_tasks() -> List[Dict[str, Any]]:
    """
    Lists all tasks by reading JSON files from the tasks directory.

    ⚡ Bolt Optimization:
    Uses an in-memory cache validated by the directory's last modified time (mtime).
    This eliminates redundant disk I/O when the task list hasn't changed.
    """
    if not os.path.exists(TASKS_DIR):
        return []

    global _tasks_cache, _tasks_cache_mtime
    try:
        current_mtime = os.path.getmtime(TASKS_DIR)
    except OSError:
        current_mtime = -1.0

    # If the directory hasn't changed, return a deep copy of the cached list
    if current_mtime != -1.0 and current_mtime == _tasks_cache_mtime:
        return copy.deepcopy(_tasks_cache)

    tasks = []
    # Sort files alphabetically for stable UI rendering and cache consistency
    filenames = sorted([f for f in os.listdir(TASKS_DIR) if f.endswith('.json')])
    for f in filenames:
        tasks.append(load_json(os.path.join(TASKS_DIR, f)))

    # Update cache
    _tasks_cache = tasks
    _tasks_cache_mtime = current_mtime

    # Return a deep copy to ensure the caller cannot mutate our internal cache state
    return copy.deepcopy(tasks)

def delete_task_file(task_id: str) -> bool:
    filepath = get_task_path(task_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        # ⚡ Bolt Optimization: Invalidate the in-memory task cache
        global _tasks_cache_mtime
        _tasks_cache_mtime = -1.0
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
