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

## 2024-05-24 - Directory mtime as a reliable cache invalidator
**Learning:** For flat-file storage, tracking the directory `mtime` is an extremely efficient way to implement caching for file listing operations. It avoids full directory scans and JSON parsing on every call, which was a significant bottleneck in the Streamlit render loop.
**Action:** Implement `mtime`-based caching for `list_tasks()` and ensure explicit invalidation in all write paths (`save_json`, `delete_task_file`) to maintain consistency.
