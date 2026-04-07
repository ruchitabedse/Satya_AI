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

## 2024-05-24 - In-memory Caching for Flat-file Lists
**Learning:** For frequently accessed directory-based collections (like tasks), `os.listdir` + multiple `json.load` calls create significant latency.
**Action:** Implement in-memory caching validated by the directory's `mtime`. Ensure `copy.deepcopy()` is used when returning cached mutable objects to prevent accidental state corruption.
