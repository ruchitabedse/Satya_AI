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

## 2025-05-15 - Mtime-based directory caching
**Learning:** For flat-file architectures, `os.path.getmtime(directory)` is a reliable and extremely fast way to detect if files were added, removed, or renamed (using atomic operations like `os.rename`) within that directory. This allows for safe in-memory caching of file listings.
**Action:** Use `mtime` validation for directory-based listings to avoid N+1 disk reads in every render loop.

## 2025-05-15 - Efficient deep copying
**Learning:** While `json.loads(json.dumps(obj))` is a common "quick" way to deep copy in Python, it is CPU-bound and significantly slower than `copy.deepcopy()`. In performance-critical paths like the Streamlit render loop, `copy.deepcopy()` provides a measurable speedup (~40% better than JSON serialization).
**Action:** Always prefer `copy.deepcopy()` for cloning in-memory state in performance-critical paths.
