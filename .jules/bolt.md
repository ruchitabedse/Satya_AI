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

## 2024-05-24 - Directory-mtime based caching
**Learning:** Directory `mtime` changes reliably on file creation, deletion, and atomic `os.rename` replacement in Linux. This allows implementing an $O(1)$ `stat`-based cache check for directory listings, avoiding expensive $O(N)$ disk I/O and JSON parsing for mostly-read-only data. `copy.deepcopy()` is essential to prevent in-memory cache corruption.
**Action:** Use `os.path.getmtime(DIR)` to validate caches for local directory-based storage.
