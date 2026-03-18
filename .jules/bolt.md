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

## 2025-02-07 - mtime-based Directory Caching
**Learning:** For flat-file storage, using the directory's `mtime` to validate an in-memory cache of file listings (like `list_tasks`) can reduce latency by ~90%+. However, manual invalidation is still needed for file updates (since `mtime` only changes on add/remove).
**Action:** Implement `mtime` caching with `copy.deepcopy()` to prevent cache corruption, and explicitly invalidate the cache in `save_json` if the modified file belongs to the cached directory.
