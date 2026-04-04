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

## 2024-05-23 - Directory mtime caching
**Learning:** Using directory `mtime` as a cache invalidation key for `list_tasks` can reduce dashboard rendering latency by over 90% (e.g., from 16ms to 1.6ms for 200 tasks).
**Action:** Implement in-memory caches validated by `mtime` for read-heavy operations. Use `copy.deepcopy()` to return cached objects safely, preventing unintended mutation by callers.
