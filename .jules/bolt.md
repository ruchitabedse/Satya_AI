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

## 2025-02-07 - In-memory caching for flat-file task storage
**Learning:** Frequent disk I/O and JSON parsing of hundreds of small files in a Streamlit app leads to significant rendering latency (~16ms for 200 tasks). Directory `mtime` is an efficient invalidation signal for file additions/deletions, but not always for file content updates.
**Action:** Use an in-memory cache validated by directory `mtime`, and manually invalidate it on file writes and deletes to ensure cross-platform consistency. Always return deep copies of cached mutable objects to prevent accidental corruption by callers.
