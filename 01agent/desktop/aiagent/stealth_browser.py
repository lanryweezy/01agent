from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# This module is potentially deprecated. 
# New browser automation should use browser_automation.py

def launch_stealth_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        stealth = Stealth(page)
        stealth.apply()
        print("Browser launched and stealth applied.")
        return page

if __name__ == '__main__':
    page = launch_stealth_browser()
    page.goto("https://www.google.com")
    print("Browser navigated to Google.")
    page.browser.close()
    print("Browser closed.")
