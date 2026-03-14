from playwright.sync_api import sync_playwright
import time

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Dashboard
        page.goto("http://localhost:5000")
        time.sleep(5)
        page.screenshot(path="baseline_dashboard.png", full_page=True)
        print("Captured baseline_dashboard.png")

        # Main Owner Page
        # Click the "Main Owner" radio button in the sidebar
        # Based on app.py: page = st.radio("Navigation", ["Dashboard", "Task Board", "Truth Source", "Agent Logs", "Main Owner", "SDK Docs"], ...)
        page.click("text=Main Owner")
        time.sleep(3)
        page.screenshot(path="baseline_main_owner.png", full_page=True)
        print("Captured baseline_main_owner.png")

        browser.close()

if __name__ == "__main__":
    capture_screenshots()
