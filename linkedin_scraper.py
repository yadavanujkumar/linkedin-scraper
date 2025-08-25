"""
Improved LinkedIn Scraper with enhanced features
"""
import json
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
from typing import List, Dict, Any, Optional
from config import Config
from data_exporter import DataExporter

class LinkedInScraper:
    """Enhanced LinkedIn scraper with improved features"""
    
    def __init__(self, config: Config):
        self.config = config
        self.exporter = DataExporter(config)
        self.scraped_data = []
        self.visited_urls = set()
        self.driver = None
        self._setup_logging()
        self._load_cache()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('linkedin_scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_cache(self):
        """Load previously scraped profiles from cache"""
        cache_file = self.config.get('output.cache_file', 'profiles_cache.json')
        self.scraped_data = self.exporter.load_existing_data(cache_file)
        self.visited_urls = {profile.get('profile_url', '') for profile in self.scraped_data}
        
        if self.scraped_data:
            self.logger.info(f"Loaded {len(self.scraped_data)} profiles from cache")
    
    def _save_to_cache(self):
        """Save current data to cache"""
        cache_file = self.config.get('output.cache_file', 'profiles_cache.json')
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
    
    def _init_driver(self):
        """Initialize the Chrome WebDriver with optimized options"""
        options = webdriver.ChromeOptions()
        
        if self.config.get('scraping.headless', True):
            options.add_argument('--headless=new')
        
        # Anti-detection options
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-webrtc")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Faster loading
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Performance options
        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Block images
            "profile.default_content_setting_values.notifications": 2  # Block notifications
        }
        options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            self.driver.implicitly_wait(10)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def login(self, email: str = None, password: str = None) -> bool:
        """Login to LinkedIn"""
        if not self.driver:
            self._init_driver()
        
        # Use provided credentials or from config
        email = email or self.config.get('linkedin.email')
        password = password or self.config.get('linkedin.password')
        
        if not email or not password:
            self.logger.error("LinkedIn credentials not provided")
            return False
        
        try:
            self.logger.info("Logging into LinkedIn...")
            self.driver.get('https://www.linkedin.com/login')
            
            # Wait for login form and enter credentials
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, 'username'))
            ).send_keys(email)
            
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            
            # Wait for successful login
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.global-nav__me, .feed-identity-module'))
            )
            
            self.logger.info("Successfully logged into LinkedIn")
            time.sleep(random.uniform(2, 4))
            return True
            
        except TimeoutException:
            self.logger.error("Login failed - check credentials or solve CAPTCHA manually")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def search_profiles(self, keyword: str, company: str = '', location: str = '') -> bool:
        """Navigate to LinkedIn search results"""
        try:
            # Build search URL
            encoded_keyword = quote(keyword)
            search_params = [f'keywords={encoded_keyword}']
            
            if company:
                search_params.append(f'currentCompany={quote(company)}')
            if location:
                search_params.append(f'geoUrn={quote(location)}')
            
            search_url = f'https://www.linkedin.com/search/results/people/?{"&".join(search_params)}'
            
            self.logger.info(f"Searching for: {keyword}")
            self.driver.get(search_url)
            
            # Wait for search results
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.search-results-container, .reusable-search__result-container'))
            )
            
            time.sleep(random.uniform(3, 5))
            return True
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return False
    
    def extract_profile_data(self, result_element) -> Optional[Dict[str, Any]]:
        """Extract data from a single profile result element"""
        try:
            # Extract name and URL
            link_element = result_element.find_element(By.CSS_SELECTOR, '.app-aware-link')
            name = link_element.get_attribute('innerText').strip()
            url = link_element.get_attribute('href').split('?')[0]
            
            if url in self.visited_urls:
                return None
            
            # Extract headline/designation
            headline = "N/A"
            try:
                headline = result_element.find_element(
                    By.CSS_SELECTOR, '.entity-result__primary-subtitle'
                ).text.strip()
            except NoSuchElementException:
                pass
            
            # Extract location
            location = "N/A"
            try:
                location = result_element.find_element(
                    By.CSS_SELECTOR, '.entity-result__secondary-subtitle'
                ).text.strip()
            except NoSuchElementException:
                pass
            
            # Extract additional info if available
            profile_data = {
                'name': name,
                'profile_url': url,
                'headline': headline,
                'location': location,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Try to extract company info from headline
            if headline != "N/A" and " at " in headline:
                parts = headline.split(" at ")
                if len(parts) >= 2:
                    profile_data['company'] = parts[-1].strip()
            
            return profile_data
            
        except Exception as e:
            self.logger.debug(f"Error extracting profile data: {e}")
            return None
    
    def scrape_profiles(self, keyword: str, max_profiles: int = None, company: str = '') -> List[Dict[str, Any]]:
        """Main scraping method"""
        max_profiles = max_profiles or self.config.get('scraping.max_profiles', 200)
        max_pages = self.config.get('scraping.max_pages', 20)
        delay_range = self.config.get('scraping.delay_range', [3, 6])
        
        if not self.search_profiles(keyword, company):
            return []
        
        new_profiles = []
        page_count = 0
        
        self.logger.info(f"Starting to scrape profiles for: {keyword}")
        
        while len(new_profiles) < max_profiles and page_count < max_pages:
            page_count += 1
            
            try:
                # Wait for results to load
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.reusable-search__result-container'))
                )
                
                # Find all profile results
                results = self.driver.find_elements(By.CSS_SELECTOR, '.reusable-search__result-container')
                
                self.logger.info(f"Page {page_count}: Found {len(results)} profiles")
                
                # Extract data from each profile
                page_profiles = 0
                for result in results:
                    if len(new_profiles) >= max_profiles:
                        break
                    
                    profile_data = self.extract_profile_data(result)
                    if profile_data:
                        new_profiles.append(profile_data)
                        self.visited_urls.add(profile_data['profile_url'])
                        page_profiles += 1
                
                self.logger.info(f"Extracted {page_profiles} new profiles from page {page_count}")
                
                # Try to navigate to next page
                try:
                    next_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                    
                    if 'disabled' in next_btn.get_attribute('class') or not next_btn.is_enabled():
                        self.logger.info("No more pages available")
                        break
                    
                    # Scroll to and click next button
                    self.driver.execute_script("arguments[0].scrollIntoView();", next_btn)
                    time.sleep(random.uniform(1, 2))
                    next_btn.click()
                    
                    # Wait for new page to load
                    time.sleep(random.uniform(delay_range[0], delay_range[1]))
                    
                except Exception as e:
                    self.logger.info(f"Pagination ended: {e}")
                    break
                
            except Exception as e:
                self.logger.error(f"Error on page {page_count}: {e}")
                break
        
        # Update main data list
        self.scraped_data.extend(new_profiles)
        self._save_to_cache()
        
        self.logger.info(f"Scraping completed. Total new profiles: {len(new_profiles)}")
        return new_profiles
    
    def export_data(self, formats: List[str] = None) -> Dict[str, str]:
        """Export scraped data to specified formats"""
        if not self.scraped_data:
            self.logger.warning("No data to export")
            return {}
        
        return self.exporter.export_data(self.scraped_data, formats)
    
    def close(self):
        """Close the browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()