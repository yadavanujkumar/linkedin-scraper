#!/usr/bin/env python3
"""
LinkedIn Scraper Example - Demonstrates the enhanced functionality
"""
from config import Config
from linkedin_scraper import LinkedInScraper
import os

def example_basic_usage():
    """Example: Basic usage with configuration"""
    print("🔄 Example 1: Basic usage with configuration")
    
    # Create config
    config = Config()
    
    # Set credentials (you can also use environment variables or config file)
    config.set('linkedin.email', 'your-email@example.com')  # Replace with actual email
    config.set('linkedin.password', 'your-password')        # Replace with actual password
    
    # Configure scraping settings
    config.set('scraping.max_profiles', 50)
    config.set('scraping.headless', True)
    config.set('output.formats', ['json', 'csv'])  # Export both formats
    
    # Use the scraper
    with LinkedInScraper(config) as scraper:
        # Login (will use credentials from config)
        if scraper.login():
            # Scrape software developers
            profiles = scraper.scrape_profiles('software developer')
            
            # Export data
            if profiles:
                exported_files = scraper.export_data()
                print(f"✅ Exported {len(profiles)} profiles to: {exported_files}")
        else:
            print("❌ Login failed")

def example_job_types():
    """Example: Using predefined job types"""
    print("\n🔄 Example 2: Using predefined job types")
    
    config = Config()
    
    # Show available job types
    job_types = config.get_job_types()
    print("Available job types:")
    for job_type, keywords in job_types.items():
        print(f"  {job_type}: {keywords}")
    
    # Use a specific job type
    hr_keywords = config.get_search_keyword('hr')
    print(f"\nSearching for HR professionals: {hr_keywords}")

def example_environment_variables():
    """Example: Using environment variables for credentials"""
    print("\n🔄 Example 3: Using environment variables")
    
    # Set environment variables
    os.environ['LINKEDIN_EMAIL'] = 'your-email@example.com'
    os.environ['LINKEDIN_PASSWORD'] = 'your-password'
    
    config = Config()
    config.set('linkedin.email', os.getenv('LINKEDIN_EMAIL', ''))
    config.set('linkedin.password', os.getenv('LINKEDIN_PASSWORD', ''))
    
    print(f"Email from env: {config.get('linkedin.email')}")
    print("Password configured from environment variable")

def example_csv_export():
    """Example: Demonstrating CSV export functionality"""
    print("\n🔄 Example 4: CSV export functionality")
    
    # Sample data (would come from actual scraping)
    sample_data = [
        {
            'name': 'John Doe',
            'profile_url': 'https://linkedin.com/in/johndoe',
            'headline': 'Software Engineer at Google',
            'location': 'San Francisco, CA'
        },
        {
            'name': 'Jane Smith',
            'profile_url': 'https://linkedin.com/in/janesmith',
            'headline': 'Data Scientist at Microsoft',
            'location': 'Seattle, WA'
        }
    ]
    
    # Export to CSV
    from data_exporter import DataExporter
    config = Config()
    exporter = DataExporter(config)
    
    # Export sample data
    exported_files = exporter.export_data(sample_data, ['json', 'csv'])
    print(f"Sample data exported to: {exported_files}")

def main():
    """Run all examples"""
    print("LinkedIn Scraper Enhanced Features Examples")
    print("=" * 50)
    
    # Note: These examples use placeholder credentials
    print("⚠️  Note: Replace placeholder credentials with real ones to test")
    print()
    
    # Run examples
    example_basic_usage()
    example_job_types()
    example_environment_variables()
    example_csv_export()
    
    print("\n" + "=" * 50)
    print("Examples completed! Check the generated files:")
    print("- config.json (configuration)")
    print("- linkedin_profiles.json (JSON export)")
    print("- linkedin_profiles.csv (CSV export)")
    print("- linkedin_scraper.log (log file)")

if __name__ == '__main__':
    main()