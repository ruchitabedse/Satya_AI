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

## 2026-02-07 - Optimized cloning for cache integrity
**Learning:** For simple task dictionaries in this Python environment, `json.loads(json.dumps(obj))` is significantly faster (~50%) than `copy.deepcopy(obj)` for ensuring cache integrity when returning results from a shared in-memory cache.
**Action:** Prefer JSON roundtrip for cloning simple, serializable data structures in performance-critical paths.
