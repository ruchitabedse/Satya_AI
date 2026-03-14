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
**Learning:** Implementing an in-memory cache for directory-based flat-file storage can be safely validated using `os.path.getmtime()` of the directory. This avoids unnecessary file reads and JSON parsing on every request.
**Action:** Use directory mtime as a cache token, but ensure explicit invalidation on writes and deep-copying of returned data to prevent cache corruption.
