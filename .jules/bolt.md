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

## 2026-02-07 - In-memory Caching for Flat-File Storage
**Learning:** For flat-file architectures where record listings (e.g., `list_tasks`) involve reading and parsing hundreds of JSON files, an in-memory cache validated by directory `mtime` can yield an 80-90% performance boost. While `copy.deepcopy()` is the safest way to clone simple task dicts for cache isolation, `json.loads(json.dumps(obj))` was measured to be significantly faster (~50%) for these specific objects in this repository.
**Action:** Use directory `mtime` as a reliable cache invalidator for flat-file listings, and explicitly reset the cache marker on writes/deletes to ensure consistency in environments where directory metadata updates might be delayed.
