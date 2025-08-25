# LinkedIn Scraper

A comprehensive LinkedIn profile scraper that can extract profiles by job type and export data in both JSON and CSV formats. The project provides multiple scraping implementations and a powerful command-line interface for easy usage.

## Features

- **Multiple Scraping Methods**: 
  - Enhanced Selenium-based scraper with comprehensive features
  - Playwright-based scraper with persistent login support
  - Alternative Selenium implementations
- **Flexible Export Formats**: Export to JSON, CSV, or both simultaneously
- **Job Type Targeting**: Pre-configured search terms for common job types (software developer, HR, data scientist, etc.)
- **Command Line Interface**: Easy-to-use CLI for quick profile extraction
- **Configuration Management**: Secure credential storage and customizable settings
- **Profile Caching**: Automatic deduplication and resume capability
- **Comprehensive Data Extraction**: Name, profile URL, headline/designation, and location
- **Anti-Detection Features**: Advanced browser configurations to bypass LinkedIn's bot detection
- **Pagination Handling**: Automatically navigates through multiple pages of search results
- **Error Handling**: Robust error handling and logging

## Requirements

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (managed automatically by `webdriver_manager`)
- Playwright (optional, for alternative scraper)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yadavanujkumar/linkedin-scraper.git
cd linkedin-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers (optional, for main2.py):
```bash
playwright install
```

## Quick Start

### Using the Command Line Interface (Recommended)

1. **Create a configuration file:**
```bash
python cli.py create-config
```

2. **Edit the config.json file with your LinkedIn credentials:**
```json
{
  "linkedin": {
    "email": "your-email@example.com",
    "password": "your-password"
  }
}
```

3. **List available job types:**
```bash
python cli.py list-types
```

4. **Scrape profiles:**
```bash
# Scrape software developers (JSON format)
python cli.py scrape software_developer --max-profiles 100

# Scrape HR professionals (both JSON and CSV)
python cli.py scrape hr --formats json csv --max-profiles 50

# Scrape with company filter
python cli.py scrape data_scientist --company "Google" --max-profiles 30
```

### Using Environment Variables

You can also provide credentials via environment variables:
```bash
export LINKEDIN_EMAIL="your-email@example.com"
export LINKEDIN_PASSWORD="your-password"
python cli.py scrape software_developer
```

### Using the Python API

```python
from config import Config
from linkedin_scraper import LinkedInScraper

# Setup configuration
config = Config()
config.set('linkedin.email', 'your-email@example.com')
config.set('linkedin.password', 'your-password')
config.set('output.formats', ['json', 'csv'])

# Use the scraper
with LinkedInScraper(config) as scraper:
    if scraper.login():
        profiles = scraper.scrape_profiles('software engineer', max_profiles=100)
        exported_files = scraper.export_data()
        print(f"Exported to: {exported_files}")
```

## Project Structure

```
linkedin-scraper/
├── cli.py                 # Command-line interface
├── config.py              # Configuration management
├── data_exporter.py       # Data export utilities (JSON/CSV)
├── linkedin_scraper.py    # Enhanced scraper implementation
├── example.py             # Usage examples
├── main.py                # Original Selenium-based scraper
├── main2.py               # Playwright-based scraper (enhanced)
├── main3.py               # Alternative Selenium scraper (enhanced)
├── save_login_state.py    # Persistent login utility for Playwright
├── requirements.txt       # Python dependencies
└── readme.md              # This file
```

## Available Job Types

The scraper comes with pre-configured search terms for common job types:

- **software_developer**: Software developer, software engineer, programmer
- **data_scientist**: Data scientist, data analyst, machine learning engineer
- **hr**: Human resources, HR, talent acquisition, recruiter
- **marketing**: Marketing manager, digital marketing, marketing specialist
- **sales**: Sales manager, sales representative, business development
- **product_manager**: Product manager, product owner, product lead
- **designer**: UI designer, UX designer, graphic designer, web designer
- **manager**: Manager, director, team lead, supervisor

You can also use custom search terms by passing any string as the job type.

## Configuration Options

The `config.json` file supports extensive customization:

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
  },
  "search": {
    "job_types": {
      "custom_job": "your custom search terms"
    }
  }
}
```

## Output Formats

### JSON Format
```json
{
  "metadata": {
    "exported_at": "2024-01-01T12:00:00",
    "total_profiles": 100,
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

### CSV Format
```csv
name,profile_url,headline,location
John Doe,https://linkedin.com/in/johndoe,Software Engineer at Google,"San Francisco, CA"
```

## CLI Commands

### Scrape Profiles
```bash
python cli.py scrape JOB_TYPE [OPTIONS]

Options:
  --email EMAIL              LinkedIn email
  --password PASSWORD         LinkedIn password
  --company COMPANY          Filter by company name
  --max-profiles NUM         Maximum profiles to scrape (default: 200)
  --formats FORMAT [FORMAT]  Output formats: json, csv (default: json)
  --output PREFIX           Output filename prefix
  --headless / --no-headless Browser mode
  --config FILE             Configuration file path
```

### List Job Types
```bash
python cli.py list-types
```

### Create Configuration
```bash
python cli.py create-config
```

## Legacy Scripts

The repository includes the original implementations for reference:

- **main.py**: Original Selenium-based scraper (enhanced with CSV export)
- **main2.py**: Playwright-based scraper (enhanced with headline extraction and CSV)
- **main3.py**: Alternative Selenium implementation (enhanced with additional data fields)

These can still be used directly but lack the advanced features of the new unified system.

## Important Notes

### Security
- **Never commit credentials to version control**
- Use environment variables or secure config files for credentials
- Consider using LinkedIn's official API for production applications

### Rate Limiting and Ethics
- **Respect LinkedIn's Terms of Service**
- Implement appropriate delays between requests
- Avoid excessive scraping to prevent being blocked
- Use responsibly and consider the privacy of LinkedIn users

### CAPTCHA Handling
- If LinkedIn prompts for CAPTCHA, solve it manually
- Consider using `--no-headless` mode for debugging
- Persistent login (main2.py) can help reduce CAPTCHA frequency

### Legal Considerations
- Ensure compliance with applicable laws and regulations
- Respect robots.txt and LinkedIn's terms of service
- Use scraped data responsibly and ethically

## Troubleshooting

### Common Issues

1. **Login Failed**: Check credentials, solve any CAPTCHA manually
2. **No Profiles Found**: Try different search terms or check if you're blocked
3. **Browser Issues**: Update Chrome, clear browser data, or try different browser options
4. **Rate Limited**: Reduce scraping frequency, use longer delays

### Debug Mode
Use `--no-headless` to see what's happening in the browser:
```bash
python cli.py scrape software_developer --no-headless
```

### Logs
Check the `linkedin_scraper.log` file for detailed error information.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational purposes. Please ensure compliance with LinkedIn's Terms of Service and applicable laws when using this software.

## Disclaimer

This tool is for educational and research purposes only. Users are responsible for complying with LinkedIn's Terms of Service and applicable laws. The authors are not responsible for any misuse of this software.
