# LinkedIn Scraper

This project provides tools to scrape LinkedIn profiles using Selenium and Playwright. It automates the process of logging in, searching for profiles, and extracting relevant information such as names, profile URLs, headlines, and locations.

## Features

- **Selenium-based Scraper**: Automates LinkedIn scraping with advanced browser configurations to bypass detection.
- **Playwright-based Scraper**: Provides an alternative scraping method with persistent login support.
- **Persistent Login**: Save and reuse login sessions to avoid repeated manual logins.
- **Profile Caching**: Avoids scraping duplicate profiles by maintaining a cache.
- **Customizable Search**: Search for profiles based on keywords and companies.
- **Pagination Handling**: Automatically navigates through multiple pages of search results.

## Requirements

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (managed automatically by `webdriver_manager`)
- Playwright



## Project Structure
- linkedin-scrapper/ ├── main.py # Selenium-based 
- LinkedIn scraper ├── main2.py # Playwright-based 
- LinkedIn scraper ├── main3.py # 
Alternative Selenium-based scraper 


save_login_state.py # Script to save persistent login state using Playwright 

To use playwright

## installation
- pip install -r requirements.txt
- playwright install


## notes
  
- **Login Credentials:** Replace yourlinkedinemail and yourlinkedinpassword in the scripts with your LinkedIn credentials.
- **Search Parameters:** Modify the keyword and company parameters in the scripts to customize your search.
- **Output Files:** Scraped profiles are saved in JSON format (linkedin_profiles.json, output.json, etc.).
  
- **CAPTCHA Handling:** If LinkedIn prompts for CAPTCHA, you may need to solve it manually.
- **Rate Limiting:** Avoid excessive scraping to prevent being blocked by LinkedIn.
- **Ethical Use:** Ensure compliance with LinkedIn's terms of service and scrape responsibly.
