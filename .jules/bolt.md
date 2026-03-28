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

## 2025-02-14 - Directory mtime-based caching for flat-file storage
**Learning:** For flat-file architectures, directory `mtime` serves as an efficient "version number" for cache validation. In-memory caching with `mtime` checks reduces collection reads from O(N) disk I/O to O(1) memory access, significantly improving dashboard latency.
**Action:** Use directory `mtime` for collection-level caches. Always return deep copies (using `json.loads(json.dumps())` for performance with simple dicts) to prevent cache corruption.
