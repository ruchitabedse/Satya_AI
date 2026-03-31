## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.

## 2026-03-31 - [Robust ISO Parsing for Mixed Formats]
**Learning:** ISO 8601 strings can vary between formats (e.g., 'Z' vs '+00:00' vs '+00:00Z'). Blindly replacing 'Z' with '+00:00' can lead to malformed strings if an offset already exists (e.g., '+00:00+00:00'), causing `datetime.fromisoformat` to fail and breaking UI date rendering.
**Action:** When parsing ISO strings, check for existing offsets before modifying suffixes. If both '+00:00' and 'Z' are present, strip 'Z' to maintain a valid format for Python's `datetime` module.
