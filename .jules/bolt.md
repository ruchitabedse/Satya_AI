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

## 2024-05-24 - Directory-level caching for flat-file storage
**Learning:** For a flat-file storage system, `list_tasks` performance can be significantly improved by caching the entire list in memory and validating it via the directory's `mtime`. However, explicit cache invalidation (setting `mtime = -1.0`) is necessary during write/delete operations in the same process to guarantee immediate consistency.
**Action:** Use a module-level cache for frequently read directories, return deep copies to prevent mutation, and ensure all write paths invalidate the cache.
