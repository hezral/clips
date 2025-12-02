#!/usr/bin/env python3

import sys
import os
import subprocess
from playwright.sync_api import sync_playwright

def check_and_install_playwright_browsers():
    """
    Checks if Playwright browsers are installed and installs them if they are not.
    """
    marker_file = os.path.join(os.path.dirname(__file__), ".playwright_installed")

    if not os.path.exists(marker_file):
        print("Playwright browsers not found. Installing...")
        try:
            subprocess.run(["playwright", "install"], check=True)
            # Create the marker file to indicate that the browsers have been installed.
            with open(marker_file, "w") as f:
                f.write("installed")
            print("Playwright browsers installed successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error installing Playwright browsers: {e}")
            print("Please run 'playwright install' manually.")
            sys.exit(1)

def take_screenshot(url, output_file):
    """
    Takes a screenshot of a webpage using Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print(f"Loading {url}...")
            page.goto(url)
            print("Page loaded. Taking screenshot...")
            page.screenshot(path=output_file)
            print(f"Screenshot saved to {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            browser.close()

def main():
    check_and_install_playwright_browsers()

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <URL> <output.png>")
        print("Example: python3 playwright.py https://google.com my_screenshot.png")
        sys.exit(1)
        
    url = sys.argv[1]
    output_file = sys.argv[2]
    
    # Ensure the URL has a scheme (like https://)
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    take_screenshot(url, output_file)

if __name__ == "__main__":
    main()