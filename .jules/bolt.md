# Bolt's Performance Journal

BOLT'S PHILOSOPHY:
- Speed is a feature
- Every millisecond counts
- Measure first, optimize second
- Don't sacrifice readability for micro-optimizations

## Critical Learnings

## 2025-02-07 - Mtime-validated in-memory caching
**Learning:** In flat-file systems, $O(N)$ disk I/O for reading many small files (like tasks) on every request is a major bottleneck. An in-memory cache validated by the directory's `mtime` allows for $O(1)$ memory access while still being sensitive to external file changes.
**Action:** Use a global cache and `os.path.getmtime()` to validate it. Always return deep copies (e.g., via `json.loads(json.dumps())`) to prevent callers from accidentally mutating the cached state.

## 2024-05-23 - Flat-file N+1 file reads
**Learning:** In a flat-file architecture, calling functions that scan the entire data directory (like `get_stale_tasks` or `list_all`) multiple times per request leads to an N+1 disk I/O problem.
**Action:** Always allow passing already-loaded data into secondary checkers or metrics calculators to reuse in-memory state.
