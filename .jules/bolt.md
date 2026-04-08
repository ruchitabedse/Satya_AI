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

## 2025-02-10 - mtime-based In-memory Caching
**Learning:** For flat-file storage, in-memory caching validated by the directory's `mtime` can reduce retrieval latency by >95% while maintaining correctness across multiple processes.
**Action:** Implement `mtime` validation for directory-wide scans and use `copy.deepcopy()` to protect the cache from accidental mutation by callers.
