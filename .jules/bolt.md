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

## 2025-01-24 - Directory mtime-based caching for flat-files
**Learning:** In a flat-file architecture, `os.listdir` followed by individual file reads in a loop creates an N+1 I/O bottleneck. While OS-level caching helps, in-memory caching with directory `mtime` validation is ~40x faster for large task lists (e.g., 200 tasks).
**Action:** Use directory `mtime` as a lightweight cache validator for flat-file storage to avoid redundant disk I/O in frequently rendered views. Always return deep copies (e.g., via `json.loads(json.dumps())`) to prevent internal cache corruption by callers.
