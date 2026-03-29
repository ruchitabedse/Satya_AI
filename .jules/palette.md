## 2026-03-29 - [Streamlit Navigation with Query Parameters]
**Learning:** In Streamlit, using `st.query_params` for internal navigation (e.g., `?page=...`) requires explicit coordination with the state of radio/select components used for navigation. If the `default_index` is not correctly mapped from the query parameters, the UI can become out of sync, leading to "double navigation" or state resets.
**Action:** Define a global `NAV_OPTIONS` list. On every script run, check `st.query_params` first, map the target page back to its index in `NAV_OPTIONS`, and pass that index to the `st.radio` component. Ensure that any "clean" redirect (clearing the URL) happens after the target state is safely captured.

## 2026-03-29 - [A/B Test Persistence in Session State]
**Learning:** Randomly assigning A/B test variants (e.g., `datetime.now().second % 2`) directly in the UI components causes "flickering" or inconsistent experiences when multiple instances of the same promo (e.g., Hero vs Mobile Tile) are rendered in the same session but at slightly different times or during reruns.
**Action:** Initialize A/B test variants once and store them in `st.session_state`. This ensures that a user sees the same variant for all card placements across their entire session, providing a stable and reliable experiment environment.

## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.
