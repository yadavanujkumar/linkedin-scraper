# Import necessary libraries
import json
import time
import random
from selenium import webdriver  # For browser automation
from selenium.webdriver.common.by import By  # For locating elements
from selenium.webdriver.chrome.service import Service  # To manage ChromeDriver
from selenium.webdriver.support.ui import WebDriverWait  # For explicit waits
from selenium.webdriver.support import expected_conditions as EC  # For wait conditions
from selenium.common.exceptions import NoSuchElementException, TimeoutException  # For exception handling
from webdriver_manager.chrome import ChromeDriverManager  # To automatically manage ChromeDriver
from urllib.parse import quote  # For URL encoding
from selenium.webdriver.common.action_chains import ActionChains  # For advanced interactions

# Define the LinkedInScraper class
class LinkedInScraper:
    def __init__(self, headless=True, max_profiles=200, cache_file='profiles.json'):
        """
        Initialize the LinkedInScraper with options for headless mode, maximum profiles to scrape, and cache file.
        """
        self.cache_file = cache_file  # File to store scraped profiles
        self.max_profiles = max_profiles  # Maximum number of profiles to scrape
        self.scraped_data = self._load_cache()  # Load previously scraped profiles from cache
        self.visited_urls = set(entry['profile_url'] for entry in self.scraped_data)  # Track visited profile URLs

        # Configure Chrome options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')  # Run in headless mode (no GUI)

        # Add browser options to improve performance and bypass detection
        options.add_argument("--disable-gpu")  
        options.add_argument("--disable-software-rasterizer")  
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-webrtc")
        options.add_argument("--no-default-browser-check")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Initialize the Chrome WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),  # Automatically install ChromeDriver
            options=options
        )
        self.driver.implicitly_wait(10)  # Set an implicit wait for element loading

    def _load_cache(self):
        """
        Load previously scraped profiles from the cache file.
        :return: A list of cached profiles.
        """
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []  # Return an empty list if the cache file doesn't exist or is invalid

    def _save_to_cache(self):
        """
        Save the current scraped profiles to the cache file.
        """
        with open(self.cache_file, 'w') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)

    def login(self, email, password):
        """
        Log in to LinkedIn using the provided email and password.
        """
        self.driver.get('https://www.linkedin.com/login')  # Open the LinkedIn login page
        try:
            # Wait for the login form to load and enter credentials
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, 'username'))
            ).send_keys(email)
            
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

            # Wait for the login to succeed (check for the presence of the user menu)
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.global-nav__me'))
            )
            time.sleep(random.uniform(3, 5))  # Add a random delay to mimic human behavior
        except TimeoutException:
            print("❌ Login failed! Check credentials or solve CAPTCHA manually")
            self.driver.quit()
            exit()

    def search_people(self, keyword='software engineer', company='Google'):
        """
        Search for people on LinkedIn based on a keyword and company.
        """
        # Encode the keyword and company for use in the URL
        encoded_keyword = quote(keyword)
        encoded_company = quote(company)
        
        # Construct the search URL
        search_url = f'https://www.linkedin.com/search/results/people/?keywords={encoded_keyword}&currentCompany={encoded_company}'
        self.driver.get(search_url)  # Navigate to the search page
        
        # Wait for the search results to load
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results-container'))
        )
        time.sleep(random.uniform(3, 5))  # Add a delay to ensure the page is fully loaded

    def scrape_profiles(self):
        """
        Scrape LinkedIn profiles from the search results.
        :return: A list of scraped profiles.
        """
        step_counter = 0  # Track the number of steps (pages visited)
        max_steps = self.max_profiles * 2  # Set a limit to avoid infinite loops
        
        while len(self.scraped_data) < self.max_profiles and step_counter < max_steps:
            step_counter += 1
            try:
                # Wait for the profile containers to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.reusable-search__result-container, .search-result__info'))
                )  

                # Find all profile cards on the current page
                results = self.driver.find_elements(By.CSS_SELECTOR, '.reusable-search__result-container, .search-result__info')

                for result in results:
                    if len(self.scraped_data) >= self.max_profiles:
                        break
                    try:
                        # Extract profile details (name, URL, headline, location)
                        link_element = result.find_element(By.CSS_SELECTOR, '.app-aware-link')
                        name = link_element.get_attribute('innerText').strip()
                        url = link_element.get_attribute('href').split('?')[0]

                        if url not in self.visited_urls:  # Avoid duplicates
                            try:
                                headline = result.find_element(
                                    By.CSS_SELECTOR, '.entity-result__primary-subtitle'
                                ).text.strip()
                            except NoSuchElementException:
                                headline = "N/A"

                            try:
                                location = result.find_element(
                                    By.CSS_SELECTOR, '.entity-result__secondary-subtitle'
                                ).text.strip()
                            except NoSuchElementException:
                                location = "N/A"

                            # Add the profile to the scraped data
                            self.scraped_data.append({
                                'name': name,
                                'profile_url': url,
                                'headline': headline,
                                'location': location
                            })
                            self.visited_urls.add(url)  # Mark the URL as visited
                            self._save_to_cache()  # Save the updated cache
                            
                    except NoSuchElementException:
                        continue

                # Handle pagination (navigate to the next page)
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                    
                    if 'disabled' in next_btn.get_attribute('class'):  # Check if the "Next" button is disabled
                        print("✅ No more pages to scrape.")
                        break

                    # Scroll to the "Next" button and click it
                    self.driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                    time.sleep(random.uniform(1, 2))
                    next_btn.click()

                    # Wait for the next page to load
                    WebDriverWait(self.driver, 20).until(
                        EC.staleness_of(results[0])
                    )
                    time.sleep(random.uniform(3, 5))  # Add a delay for loading
                    
                except Exception as e:
                    print(f"⚠️ Pagination error: {str(e)}")
                    break
                
            except (NoSuchElementException, TimeoutException) as e:
                print(f"⚠️ Scraping error: {str(e)}")
                break
        
        self.driver.quit()  # Close the browser
        return self.scraped_data

# Main script execution
if __name__ == "__main__":
    HEADLESS = True  # Run in headless mode
    MAX_PROFILES = 200  # Maximum number of profiles to scrape
    OUTPUT_FILE = 'linkedin_profiles.json'  # File to save the scraped profiles
    LINKEDIN_EMAIL = 'yourlinkedinemail'  # Replace with your LinkedIn email
    LINKEDIN_PASSWORD = 'yourlinkedinpassword'  # Replace with your LinkedIn password

    # Initialize the scraper
    scraper = LinkedInScraper(
        headless=HEADLESS,
        max_profiles=MAX_PROFILES
    )
    
    try:
        # Log in to LinkedIn
        scraper.login(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
        # Search for profiles
        scraper.search_people(keyword='machine learning', company='Microsoft')
        # Scrape profiles
        data = scraper.scrape_profiles()
        
        # Save the scraped profiles to a file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Successfully saved {len(data)} profiles to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        scraper.driver.quit()  # Ensure the browser is closed in case of an error


