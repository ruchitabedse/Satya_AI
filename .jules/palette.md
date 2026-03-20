## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.

## 2026-03-10 - [Streamlit Navigation Synchronization]
**Learning:** Manual URL manipulation or query parameter links in Streamlit can lead to a desynchronized UI state where the sidebar radio button doesn't match the displayed page.
**Action:** Use a shared `nav_options` list for both the radio button and query parameter validation. Always pass `index=default_index` (calculated from `st.query_params`) to `st.radio` to ensure the sidebar correctly reflects the current page state, especially when navigated via internal HTML links.
