## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.

## 2026-03-25 - [Accessible Informational Emojis]
**Learning:** Informational emojis used in Dashboard metrics and Task Board metadata are often skipped or misinterpreted by screen readers. Wrapping them in a span with `role="img"` and a descriptive `aria-label` ensures the visual meaning (e.g., "Assignee", "Status") is communicated to all users.
**Action:** For every informational or decorative emoji used in a Streamlit Markdown or HTML block, always provide a semantic role and ARIA label to ensure accessibility compliance.
