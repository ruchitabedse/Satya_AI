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

## 2026-03-13 - Directory mtime-based caching
**Learning:** For read-heavy operations on flat-file directories (like `list_tasks`), caching the results in memory using the directory's `mtime` as a validation signal reduces latency significantly (~93% improvement).
**Action:** Implement `mtime` validation for folder-scanning functions. Use `copy.deepcopy()` when returning cached objects to prevent mutation side effects.
