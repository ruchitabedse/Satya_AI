## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.

## 2026-03-10 - [Streamlit Navigation & Deep Linking]
**Learning:** Internal navigation links using query parameters in Streamlit (e.g., `?page=...`) require manual synchronization with the main navigation component (like `st.radio` or `st.sidebar.selectbox`). Without explicitly setting the `index` based on `st.query_params`, the UI state can reset to default, causing a jarring user experience where the URL says one thing but the sidebar says another.
**Action:** Always derive the `default_index` for navigation widgets from `st.query_params` at the start of the rendering loop. Use `target="_self"` in HTML anchors to ensure the app handles the link internally without a full browser reload.
