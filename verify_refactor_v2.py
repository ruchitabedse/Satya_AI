import sys
import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def run_verification():
    print("Starting Streamlit server on port 5002...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    process = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "app.py", "--server.port", "5002"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(12)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Check Dashboard
            print("Navigating to Dashboard...")
            page.goto("http://localhost:5002")
            page.wait_for_selector('div.hero-header', timeout=30000)
            print(f"Dashboard Title: {page.locator('div.hero-header').inner_text()}")
            page.screenshot(path="debug_dashboard_start.png")

            hero_card = page.locator('a.hero-card')
            if hero_card.count() == 0:
                print("Hero card NOT found.")
                sys.exit(1)

            # 2. Click Hero Card
            print(f"Clicking Hero card. Link: {hero_card.get_attribute('href')}")
            # Use click and wait for navigation if needed, but Streamlit is an SPA-like thing
            # We expect a rerun and a new page title
            hero_card.click()

            # Wait for the Main Owner Guide header to appear
            print("Waiting for Main Owner Guide header...")
            try:
                page.wait_for_selector('div.hero-header:has-text("Main Owner Guide")', timeout=15000)
                print("Main Owner Guide page reached!")
            except Exception as e:
                print(f"Failed to reach Guide page: {e}")
                print(f"Current URL: {page.url}")
                page.screenshot(path="debug_after_click_failure.png")
                # Let's see what headers ARE there
                headers = page.locator('div.hero-header').all_inner_texts()
                print(f"Visible headers: {headers}")
                # Check query params in URL
                sys.exit(1)

            page.screenshot(path="debug_guide_final.png")
            browser.close()
            print("Verification successful!")

    finally:
        process.kill()

if __name__ == "__main__":
    run_verification()
