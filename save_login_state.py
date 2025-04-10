from playwright.sync_api import sync_playwright
import os

# Define absolute path manually using os.path.abspath
USER_DATA_DIR = os.path.abspath("linkedin_user_data")  # Change this to your desired directory
# Create the directory if it doesn't exist

def save_persistent_login():
    with sync_playwright() as p:
        print(f"💾 Using user data directory: {USER_DATA_DIR}")

        # Launch browser using persistent context
        browser = p.chromium.launch_persistent_context(
           USER_DATA_DIR,
           headless=False,
           args=["--disable-blink-features=AutomationControlled"]
)
        page = browser.new_page()

        print("🔐 Opening LinkedIn login page...")
        page.goto("https://www.linkedin.com/login")

        input("✅ Login manually in browser and press Enter when done...")

        print(f"✅ Login state saved! You can now close the browser window.")
        browser.close()

if __name__ == "__main__":
    save_persistent_login()
