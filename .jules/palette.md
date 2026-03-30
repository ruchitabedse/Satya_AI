## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.

## 2026-03-10 - [A/B Test Stability & Navigation Sync]
**Learning:** In Streamlit, using volatile state (like `datetime.now()`) for UI variants causes jarring flickering because the script reruns on every interaction. Storing these in `st.session_state` is essential for a stable UX. Additionally, deep-linking via query parameters requires strict synchronization between the URL mapping logic and the UI component labels (e.g., `st.radio`) to prevent broken navigation states.
**Action:** Always initialize A/B variants in `st.session_state` and use a shared constant for navigation options to ensure the UI and routing logic remain in sync.
