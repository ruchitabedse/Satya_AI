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

## 2024-05-24 - Directory-mtime-validated caching
**Learning:** For flat-file systems where writes are infrequent but reads (like Streamlit reruns) are constant, caching list results validated by the directory's `mtime` provides massive performance gains (e.g., 90%+ reduction in latency for 500+ files) while maintaining high data consistency.
**Action:** Implement `mtime`-validated in-memory caches for frequently read data directories like `tasks/`. Ensure deep copies are returned to prevent accidental cache corruption.
