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

## 2025-02-07 - In-memory Storage Caching for Flat-Files
**Learning:** For flat-file architectures with many small JSON files, reading the entire directory on every dashboard refresh creates a significant latency bottleneck (~125ms for 500 tasks). Directory `mtime` is a reliable and extremely fast way to validate an in-memory cache, reducing latency to <5ms (~96% improvement).
**Action:** Implement module-level caching with `mtime` validation and returning deep copies (via `json.loads(json.dumps())` for speed) to prevent cache pollution.
