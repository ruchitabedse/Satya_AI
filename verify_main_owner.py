import time
from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Give Streamlit a moment to start
        max_retries = 10
        for i in range(max_retries):
            try:
                page.goto("http://localhost:8501")
                break
            except Exception:
                if i == max_retries - 1:
                    raise
                time.sleep(2)

        # Wait for the dashboard to render
        page.wait_for_selector(".hero-header")
        page.screenshot(path="dashboard_verification.png", full_page=True)
        print("Captured dashboard_verification.png")

        # Navigate to Main Owner Guide
        # page.click('text="Main Owner Guide"') # This might fail if it's in a radio group
        # Better: use the query parameter
        page.goto("http://localhost:8501/?page=Main+Owner+Guide")
        page.wait_for_selector(".hero-header")
        # Wait for potential reruns
        time.sleep(2)
        page.screenshot(path="guide_verification.png", full_page=True)
        print("Captured guide_verification.png")

        browser.close()

if __name__ == "__main__":
    verify()
