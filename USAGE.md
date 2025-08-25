# LinkedIn Scraper Usage Guide

## Quick Start Commands

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create configuration file
python cli.py create-config

# Edit config.json with your LinkedIn credentials
```

### 2. List Available Job Types
```bash
python cli.py list-types
```
Output:
```
📋 Available job types:
🔸 software_developer: software developer OR software engineer OR programmer
🔸 data_scientist: data scientist OR data analyst OR machine learning engineer
🔸 hr: human resources OR HR OR talent acquisition OR recruiter
... and more
```

### 3. Basic Scraping Examples

#### Scrape Software Developers (JSON format)
```bash
python cli.py scrape software_developer --max-profiles 50
```

#### Scrape HR Professionals (Both JSON and CSV)
```bash
python cli.py scrape hr --formats json csv --max-profiles 100
```

#### Scrape with Company Filter
```bash
python cli.py scrape data_scientist --company "Google" --max-profiles 30
```

#### Scrape with Credentials via Command Line
```bash
python cli.py scrape marketing --email your@email.com --password yourpass --max-profiles 75
```

### 4. Output Examples

#### CSV Output (`linkedin_profiles.csv`)
```csv
name,profile_url,headline,location
John Doe,https://linkedin.com/in/johndoe,Software Engineer at Google,"San Francisco, CA"
Jane Smith,https://linkedin.com/in/janesmith,Data Scientist at Microsoft,"Seattle, WA"
```

#### JSON Output (`linkedin_profiles.json`)
```json
{
  "metadata": {
    "exported_at": "2024-01-01T12:00:00",
    "total_profiles": 2,
    "version": "2.0"
  },
  "profiles": [
    {
      "name": "John Doe",
      "profile_url": "https://linkedin.com/in/johndoe",
      "headline": "Software Engineer at Google",
      "location": "San Francisco, CA",
      "scraped_at": "2024-01-01 12:00:00"
    }
  ]
}
```

## Alternative Methods

### Using Original Scripts (Enhanced)

#### main.py (Most comprehensive)
```python
from main import LinkedInScraper

scraper = LinkedInScraper(headless=True, max_profiles=100)
scraper.login('your@email.com', 'password')
scraper.search_people(keyword='software engineer', company='Google')
data = scraper.scrape_profiles()
# Automatically saves to JSON
```

#### main2.py (Playwright-based with enhanced data)
```python
# Run directly - now includes headline and CSV export
python main2.py
```

#### main3.py (Alternative Selenium with enhanced data)
```python
from main3 import LinkedInScraper

scraper = LinkedInScraper('your@email.com', 'password')
scraper.login()
scraper.scrape_profiles(keyword='data scientist', max_profiles=50)
# Saves to both JSON and CSV
```

### Using the New Unified API
```python
from config import Config
from linkedin_scraper import LinkedInScraper

config = Config()
config.set('linkedin.email', 'your@email.com')
config.set('linkedin.password', 'password')
config.set('output.formats', ['json', 'csv'])

with LinkedInScraper(config) as scraper:
    if scraper.login():
        profiles = scraper.scrape_profiles('software engineer', max_profiles=100)
        exported_files = scraper.export_data()
        print(f"Exported to: {exported_files}")
```

## Configuration Options

### config.json Structure
```json
{
  "linkedin": {
    "email": "your-email@example.com",
    "password": "your-password"
  },
  "scraping": {
    "max_profiles": 200,
    "headless": true,
    "max_pages": 20,
    "delay_range": [3, 6]
  },
  "output": {
    "formats": ["json", "csv"],
    "json_file": "linkedin_profiles.json",
    "csv_file": "linkedin_profiles.csv",
    "cache_file": "profiles_cache.json"
  }
}
```

### Environment Variables
Instead of storing credentials in config.json:
```bash
export LINKEDIN_EMAIL="your@email.com"
export LINKEDIN_PASSWORD="yourpassword"
python cli.py scrape software_developer
```

## Tips & Best Practices

### 1. Start Small
```bash
# Test with a small number first
python cli.py scrape software_developer --max-profiles 10 --no-headless
```

### 2. Use Company Filters
```bash
# Target specific companies
python cli.py scrape software_developer --company "Microsoft" --max-profiles 50
```

### 3. Debug Mode
```bash
# Use --no-headless to see what's happening
python cli.py scrape hr --no-headless --max-profiles 5
```

### 4. Custom Output Names
```bash
# Custom output filenames
python cli.py scrape data_scientist --output "data_scientists_2024" --formats json csv
```

### 5. Resume Interrupted Scraping
The scraper automatically caches results, so you can stop and resume:
```bash
# First run (interrupted)
python cli.py scrape software_developer --max-profiles 200

# Resume later - will skip already scraped profiles
python cli.py scrape software_developer --max-profiles 200
```

## Troubleshooting

### Login Issues
1. Check credentials in config.json
2. Try manual login first with `--no-headless`
3. Solve any CAPTCHA manually
4. Check if account is temporarily restricted

### No Profiles Found
1. Try different search terms
2. Check if you're being rate-limited
3. Use broader search terms
4. Try without company filters first

### Rate Limiting
1. Reduce `max_profiles`
2. Increase delays in config
3. Use headless mode
4. Take breaks between scraping sessions

## Security Notes

1. **Never commit credentials** to version control
2. Use environment variables for production
3. Keep your `config.json` private
4. Regularly update your LinkedIn password
5. Be aware of LinkedIn's terms of service

## Legal & Ethical Considerations

1. **Respect LinkedIn's Terms of Service**
2. **Don't scrape excessively** - use reasonable delays
3. **Respect user privacy** - only scrape public information
4. **Use data responsibly** - don't spam or misuse contact information
5. **Consider LinkedIn's API** for commercial applications