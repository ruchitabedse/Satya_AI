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

## 2024-05-23 - In-memory Caching with Directory Mtime
**Learning:** For flat-file systems where files are frequently read but less frequently modified, an in-memory cache validated by the directory's `mtime` provides a massive performance boost (e.g., 90% reduction in read time for 500 tasks).
**Action:** Implement `mtime`-validated caches in core storage layers. Ensure deep copies are returned using `json.loads(json.dumps())` to prevent cache mutation, and use explicit invalidation (`mtime = -1.0`) during write operations to handle filesystem resolution limits.
