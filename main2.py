# Import necessary libraries
from playwright.sync_api import sync_playwright  # Playwright for browser automation
import json, time, random  # For JSON handling, delays, and randomness
from pathlib import Path  # For file path handling

# Constants
CACHE_FILE = "cache.json"  # File to store cached profile URLs
OUTPUT_FILE = "output.json"  # File to save collected profile data
USER_DATA_DIR = "linkedin_user_data"  # Directory for persistent login session
MAX_PROFILES = 200  # Maximum number of profiles to scrape
MAX_ITERATIONS = 20  # Maximum number of iterations (pages) to scan

# Custom User-Agent to Bypass Bot Detection
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

# ⏳ Load Cached Profiles to Avoid Duplicates
def load_cache():
    """
    Load cached profile URLs from the cache file to avoid scraping duplicates.
    :return: A set of cached profile URLs.
    """
    if Path(CACHE_FILE).exists():  # Check if the cache file exists
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))  # Load and return the cached URLs as a set
    return set()  # Return an empty set if the cache file doesn't exist

# 💾 Save Cache to File
def save_cache(cache):
    """
    Save the updated cache of profile URLs to the cache file.
    :param cache: A set of profile URLs to save.
    """
    with open(CACHE_FILE, "w") as f:
        json.dump(list(cache), f)  # Save the cache as a JSON list

# 🔄 Save Collected Profiles
def save_profiles(profiles):
    """
    Save the collected profile data to the output file.
    :param profiles: A list of profile data dictionaries to save.
    """
    with open(OUTPUT_FILE, "w") as f:
        json.dump(profiles, f, indent=2)  # Save profiles with indentation for readability
    print(f"✅ Saved {len(profiles)} profiles to '{OUTPUT_FILE}'")  # Log the save operation

# 🚀 Main Scraper Function
def run_scraper():
    """
    Main function to scrape LinkedIn profiles using Playwright.
    """
    # Load cached profiles to avoid duplicates
    cache = load_cache()
    collected = []  # List to store collected profiles
    print(f"⚡ Loaded {len(cache)} profiles from cache...")  # Log the number of cached profiles

    # Use Playwright for browser automation
    with sync_playwright() as p:
        # Launch a persistent browser context with anti-detection settings
        browser = p.chromium.launch_persistent_context(
            USER_DATA_DIR,  # Use the persistent login directory
            headless=False,  # Run the browser in non-headless mode for debugging
            args=[
                "--disable-blink-features=AutomationControlled",  # Bypass automation detection
                "--disable-features=site-per-process",  # Disable site isolation
                "--disable-popup-blocking"  # Disable popup blocking
            ],
            user_agent=USER_AGENT  # Set a custom User-Agent to mimic a real browser
        )
        page = browser.new_page()  # Open a new page in the browser

        print("🔍 Opening LinkedIn search page...")
        # Navigate to the LinkedIn search page with the keyword "data scientist"
        page.goto("https://www.linkedin.com/search/results/people/?keywords=data%20scientist")

        try:
            # Wait for the search results to load (timeout after 30 seconds)
            page.wait_for_selector("div.reusable-search__result-container", timeout=30000)
        except:
            # Handle timeout if the search results don't load
            print("❌ Timeout: Search results didn't load.")
            return

        iteration = 0  # Track the number of iterations (pages scanned)
        while len(collected) < MAX_PROFILES and iteration < MAX_ITERATIONS:
            print(f"🔄 Scanning page {iteration + 1}... (So far: {len(collected)})")
            # Get all profile cards on the current page
            cards = page.query_selector_all("div.reusable-search__result-container")

            for card in cards:
                try:
                    # Extract the profile name and URL from each card
                    name_el = card.query_selector("span.entity-result__title-text > a > span[aria-hidden='true']")
                    link_el = card.query_selector("a.app-aware-link")
                    if name_el and link_el:  # Ensure both elements exist
                        name = name_el.inner_text().strip()  # Get the profile name
                        url = link_el.get_attribute("href").split("?")[0]  # Get the profile URL (without query params)
                        if url not in cache:  # Check if the profile is already cached
                            collected.append({"name": name, "url": url})  # Add to collected profiles
                            cache.add(url)  # Add to cache
                except Exception as e:
                    # Handle errors while parsing a profile card
                    print("⚠️ Error parsing card:", e)

            # 🚦 Handle Pagination (Next Page)
            try:
                # Find and click the "Next" button to go to the next page
                next_button = page.query_selector("button[aria-label='Next']")
                if next_button and next_button.is_enabled():  # Check if the button exists and is enabled
                    next_button.click()  # Click the "Next" button
                    time.sleep(random.uniform(3, 6))  # Add a random delay to mimic human behavior
                else:
                    # Stop if there are no more pages to navigate
                    print("🚦 No more pages to navigate.")
                    break
            except Exception as e:
                # Handle errors while clicking the "Next" button
                print("⚠️ Couldn't click next:", e)
                break

            iteration += 1  # Increment the iteration count

        browser.close()  # Close the browser after scraping is complete

    # Save the updated cache and collected profiles
    save_cache(cache)
    save_profiles(collected)

# Entry point of the script
if __name__ == "__main__":
    run_scraper()  # Run the scraper

