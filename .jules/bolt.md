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

## 2025-02-07 - Directory mtime caching for flat-file lists
**Learning:** In a high-frequency render loop (Streamlit), even a single `list_tasks` call becomes a bottleneck as the number of files grows. Relying on directory `mtime` for cache validation is effective but requires explicit invalidation in `save_json` to handle in-place updates where `mtime` might not reliably trigger.
**Action:** Use `copy.deepcopy` when returning from shared in-memory caches to prevent accidental mutation by UI components.
