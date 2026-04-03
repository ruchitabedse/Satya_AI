import os
import json
import fcntl
import logging
import copy
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SATYA_DIR = "satya_data"
TASKS_DIR = os.path.join(SATYA_DIR, "tasks")
TRUTH_DIR = os.path.join(SATYA_DIR, "truth")
AGENTS_DIR = os.path.join(SATYA_DIR, "agents")

# In-memory cache for tasks to avoid N+1 disk I/O
_TASKS_CACHE: List[Dict[str, Any]] = []
_LAST_MTIME: float = -1.0

def ensure_satya_dirs() -> None:
    os.makedirs(TASKS_DIR, exist_ok=True)
    os.makedirs(TRUTH_DIR, exist_ok=True)
    os.makedirs(AGENTS_DIR, exist_ok=True)

def save_json(filepath: str, data: Any) -> bool:
    global _LAST_MTIME
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

                # Invalidate tasks cache if a task file was updated
                if filepath.startswith(TASKS_DIR):
                    _LAST_MTIME = -1.0

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
    global _TASKS_CACHE, _LAST_MTIME
    if not os.path.exists(TASKS_DIR):
        return []

    try:
        current_mtime = os.path.getmtime(TASKS_DIR)
    except OSError:
        current_mtime = -1.0

    # Return cached copy if directory hasn't changed
    if _LAST_MTIME != -1.0 and current_mtime == _LAST_MTIME:
        return copy.deepcopy(_TASKS_CACHE)

    tasks = []
    # Sort filenames for consistent ordering
    filenames = sorted([f for f in os.listdir(TASKS_DIR) if f.endswith('.json')])
    for f in filenames:
        tasks.append(load_json(os.path.join(TASKS_DIR, f)))

    _TASKS_CACHE = tasks
    _LAST_MTIME = current_mtime
    return copy.deepcopy(tasks)

def delete_task_file(task_id: str) -> bool:
    global _LAST_MTIME
    filepath = get_task_path(task_id)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Invalidate tasks cache
        _LAST_MTIME = -1.0
        return True
    return False

def delete_truth_file(filename: str) -> bool:
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(TRUTH_DIR, safe_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False
