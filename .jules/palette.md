## 2026-03-09 - [Time Formatting Robustness]
**Learning:** Naive datetime comparisons against parsed ISO timestamps (which are often offset-aware) lead to TypeErrors, causing UI elements like relative time strings ("X min ago") to fail silently or crash the app. Additionally, the 'Z' suffix in ISO strings is not always handled consistently across Python versions.
**Action:** Always use `datetime.now(timezone.utc)` when comparing against parsed ISO strings. Implement a robust parsing helper that handles 'Z' and offset-aware strings gracefully to ensure UX elements relying on time are always functional.

## 2026-03-20 - [A/B Testing & Promo Design]
**Learning:** Hardcoded A/B test variants in Streamlit components are difficult to maintain. Using `st.session_state` to store `variant` and `cta_variant` ensures consistency across a session and allows for easier A/B testing implementation.
**Action:** Standardize A/B testing by storing variants in `st.session_state`. Use a consistent naming convention (`variant`, `cta_variant`) and implement a centralized selection logic (e.g., based on time or user ID) to ensure session-level stability.
