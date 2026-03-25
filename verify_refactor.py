import sys
import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def run_verification():
    # Start streamlit server in background
    print("Starting Streamlit server...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    process = subprocess.Popen(
        ["uv", "run", "streamlit", "run", "app.py", "--server.port", "5001"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(10)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # 1. Check Dashboard and Hero Card
            print("Checking Dashboard...")
            page.goto("http://localhost:5001")
            page.wait_for_selector('div.hero-header', timeout=20000)

            # Verify Hero Card exists
            hero_card = page.locator('a.hero-card')
            if hero_card.count() > 0:
                print("Hero card found.")
                # Capture screenshot of dashboard
                page.screenshot(path="verify_dashboard.png")
            else:
                print("Hero card NOT found.")
                sys.exit(1)

            # 2. Click Hero Card and check navigation
            print("Clicking Hero card...")
            hero_card.click()

            # Wait for navigation and page reload (st.rerun)
            # The URL should change to ?page=Main+Owner+Guide and then potentially clean up
            page.wait_for_selector('div.hero-header:has-text("Main Owner Guide")', timeout=10000)

            # Verify URL reflects the guide page
            current_url = page.url
            print(f"Current URL: {current_url}")

            # Check if query params were cleaned (st.query_params.clear() was called)
            if "clicked_promo" not in current_url:
                print("Query parameters cleaned successfully.")

            # Verify Guide content
            page.wait_for_selector('text=3-Step Setup Guide')
            page.screenshot(path="verify_guide.png")
            print("Guide page verified.")

            # 3. Check sidebar for Compact Card
            print("Checking Sidebar Compact Card...")
            compact_card = page.locator('a.compact-card')
            if compact_card.count() > 0:
                print("Compact card found in sidebar.")
            else:
                # Might need to check sidebar on Dashboard
                page.goto("http://localhost:5001?page=Dashboard")
                page.wait_for_selector('a.compact-card', timeout=5000)
                print("Compact card found on Dashboard sidebar.")

            browser.close()
            print("Verification successful!")

    finally:
        process.kill()

if __name__ == "__main__":
    run_verification()
