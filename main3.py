# Import necessary libraries for web scraping and automation
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time, json, random

# Define a class for LinkedIn scraping functionality
class LinkedInScraper:
    def __init__(self, email, password):
        """
        Initialize the LinkedInScraper with user credentials and set up the web driver.
        """
        self.email = email  # LinkedIn email
        self.password = password  # LinkedIn password
        self.driver = self.init_driver()  # Initialize the Selenium WebDriver
        self.output_file = "output.json"  # File to save scraped data

    def init_driver(self):
        """
        Configure and initialize the Selenium WebDriver with Chrome options.
        """
        options = webdriver.ChromeOptions()
        # Disable automation detection and popup blocking
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")  # Start browser maximized
        # Prevent detection of automation
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        return webdriver.Chrome(options=options)  # Return the configured WebDriver

    def login(self):
        """
        Log in to LinkedIn using the provided credentials.
        """
        self.driver.get('https://www.linkedin.com/login')  # Open LinkedIn login page
        try:
            # Wait for the username field to load and enter the email
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, 'username'))
            ).send_keys(self.email)
            
            # Enter the password and click the login button
            self.driver.find_element(By.ID, 'password').send_keys(self.password)
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            
            # Wait until the login is successful by checking for the presence of the profile icon
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.global-nav__me'))
            )
            time.sleep(random.uniform(2, 4))  # Add a random delay to mimic human behavior
        except TimeoutException:
            # Handle login failure (e.g., incorrect credentials or CAPTCHA)
            print("❌ Login failed! Check credentials or solve CAPTCHA manually")
            self.driver.quit()  # Close the browser
            exit()  # Exit the program

    def scrape_profiles(self, keyword="data scientist", max_profiles=200, max_pages=20):
        """
        Scrape LinkedIn profiles based on a search keyword.
        :param keyword: The search term to find profiles (default: "data scientist").
        :param max_profiles: Maximum number of profiles to scrape (default: 200).
        :param max_pages: Maximum number of search result pages to scan (default: 20).
        """
        collected = []  # List to store collected profile data
        visited = set()  # Set to track visited profile URLs

        # Construct the LinkedIn search URL with the given keyword
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword.replace(' ', '%20')}"
        self.driver.get(search_url)  # Open the search results page
        time.sleep(3)  # Wait for the page to load

        for page in range(max_pages):
            print(f"🔄 Scanning page {page + 1}... Collected so far: {len(collected)}")
            try:
                # Wait for the profile cards to load on the page
                cards = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.reusable-search__result-container"))
                )
            except:
                # Handle case where results fail to load (e.g., rate-limiting or blocking)
                print("❌ Couldn't load results, possibly blocked.")
                break

            for card in cards:
                try:
                    # Extract the profile name and URL from each card
                    name_el = card.find_element(By.CSS_SELECTOR, "span.entity-result__title-text > a > span[aria-hidden='true']")
                    url_el = card.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                    name = name_el.text.strip()  # Get the profile name
                    url = url_el.get_attribute("href").split("?")[0]  # Get the profile URL (without query params)

                    # Add the profile to the collected list if it hasn't been visited
                    if url not in visited:
                        collected.append({"name": name, "url": url})
                        visited.add(url)

                        # Stop if the maximum number of profiles is reached
                        if len(collected) >= max_profiles:
                            break
                except:
                    # Skip profiles that fail to load or parse
                    continue

            # Stop if the maximum number of profiles is reached
            if len(collected) >= max_profiles:
                break

            try:
                # Find and click the "Next" button to go to the next page of results
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(random.uniform(3, 6))  # Add a random delay to mimic human behavior
                else:
                    print("🚦 No more pages.")
                    break
            except:
                # Handle case where the "Next" button is not clickable
                print("⚠️ Can't click next, ending.")
                break

        # Save the collected profiles to a JSON file
        self.save_to_file(collected)
        print(f"✅ Done! Total profiles collected: {len(collected)}")
        self.driver.quit()  # Close the browser

    def save_to_file(self, data):
        """
        Save the collected profile data to a JSON file.
        :param data: List of profile data to save.
        """
        with open(self.output_file, "w") as f:
            json.dump(data, f, indent=2)  # Write data to file with indentation for readability

#  Usage example
if __name__ == "__main__":
    # Replace with your LinkedIn credentials
    EMAIL = "yourlinkedlnemail"
    PASSWORD = "yourlinkedinpassword"
    # Note: Make sure to handle your credentials securely in production code

    # Create an instance of the scraper and start scraping
    scraper = LinkedInScraper(EMAIL, PASSWORD)
    scraper.login()  # Log in to LinkedIn
    scraper.scrape_profiles(keyword="data scientist", max_profiles=100)  # Scrape profiles based on the keyword
