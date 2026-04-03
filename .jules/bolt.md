# Bolt's Performance Journal

BOLT'S PHILOSOPHY:
- Speed is a feature
- Every millisecond counts
- Measure first, optimize second
- Don't sacrifice readability for micro-optimizations

## Critical Learnings

## 2024-05-23 - Flat-file N+1 file reads
**Learning:** In a flat-file architecture, calling functions that scan the entire data directory (like `get_stale_tasks` or `list_all`) multiple times per request leads to an N+1 disk I/O problem.
**Action:** Always allow passing already-loaded data into secondary checkers or metrics calculators to reuse in-memory state.

## 2024-05-23 - In-memory Caching with mtime
**Learning:** For flat-file systems where writes are atomic (rename), using the directory's `mtime` as a cache validation key is an extremely efficient way to avoid redundant disk I/O and JSON parsing for large collections.
**Action:** Implement `_TASKS_CACHE` and `_LAST_MTIME` globals in storage modules. Return `copy.deepcopy` to prevent callers from corrupting the cache. Explicitly invalidate on writes/deletes.
