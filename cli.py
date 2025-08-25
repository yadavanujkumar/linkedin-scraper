#!/usr/bin/env python3
"""
LinkedIn Scraper CLI - Command Line Interface
"""
import argparse
import sys
import os
from typing import List
from config import Config
from linkedin_scraper import LinkedInScraper

def setup_config(args):
    """Setup configuration from arguments and config file"""
    config = Config(args.config)
    
    # Override config with command line arguments
    if args.email:
        config.set('linkedin.email', args.email)
    if args.password:
        config.set('linkedin.password', args.password)
    if args.max_profiles:
        config.set('scraping.max_profiles', args.max_profiles)
    if args.headless is not None:
        config.set('scraping.headless', args.headless)
    if args.formats:
        config.set('output.formats', args.formats)
    if args.output:
        if 'json' in args.formats:
            config.set('output.json_file', f"{args.output}.json")
        if 'csv' in args.formats:
            config.set('output.csv_file', f"{args.output}.csv")
    
    return config

def validate_credentials(config):
    """Validate that credentials are provided"""
    email = config.get('linkedin.email')
    password = config.get('linkedin.password')
    
    if not email or not password:
        print("❌ LinkedIn credentials are required!")
        print("You can provide them via:")
        print("  1. Command line: --email your@email.com --password yourpass")
        print("  2. Config file: config.json")
        print("  3. Environment variables: LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
        return False
    
    return True

def scrape_job_type(args):
    """Scrape profiles for a specific job type"""
    config = setup_config(args)
    
    # Check for environment variables
    if not config.get('linkedin.email'):
        config.set('linkedin.email', os.getenv('LINKEDIN_EMAIL', ''))
    if not config.get('linkedin.password'):
        config.set('linkedin.password', os.getenv('LINKEDIN_PASSWORD', ''))
    
    if not validate_credentials(config):
        return 1
    
    # Get search keyword for job type
    keyword = config.get_search_keyword(args.job_type)
    print(f"🔍 Searching for: {keyword}")
    
    try:
        with LinkedInScraper(config) as scraper:
            # Login
            if not scraper.login():
                print("❌ Failed to login to LinkedIn")
                return 1
            
            # Scrape profiles
            new_profiles = scraper.scrape_profiles(
                keyword=keyword,
                max_profiles=args.max_profiles,
                company=args.company or ''
            )
            
            if new_profiles:
                # Export data
                exported_files = scraper.export_data(args.formats)
                
                print(f"\n✅ Successfully scraped {len(new_profiles)} profiles!")
                for format_type, filename in exported_files.items():
                    print(f"📄 {format_type.upper()} file: {filename}")
            else:
                print("⚠️ No new profiles found")
    
    except KeyboardInterrupt:
        print("\n❌ Scraping interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return 1
    
    return 0

def list_job_types(args):
    """List available job types"""
    config = Config(args.config)
    job_types = config.get_job_types()
    
    print("📋 Available job types:")
    print("-" * 50)
    for job_type, keywords in job_types.items():
        print(f"🔸 {job_type}")
        print(f"   Keywords: {keywords}")
        print()

def create_sample_config(args):
    """Create a sample configuration file"""
    config = Config()
    
    # Set sample values
    config.set('linkedin.email', 'your-email@example.com')
    config.set('linkedin.password', 'your-password')
    
    config.save_config()
    print(f"✅ Sample configuration created: {config.config_file}")
    print("📝 Please edit the file to add your LinkedIn credentials")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LinkedIn Profile Scraper - Extract profiles by job type",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape software developers and save as both JSON and CSV
  python cli.py scrape software_developer --formats json csv --max-profiles 100
  
  # Scrape HR professionals with credentials
  python cli.py scrape hr --email your@email.com --password yourpass
  
  # Scrape data scientists at specific company
  python cli.py scrape data_scientist --company "Google" --max-profiles 50
  
  # List available job types
  python cli.py list-types
  
  # Create sample config file
  python cli.py create-config
        """
    )
    
    parser.add_argument('--config', default='config.json',
                       help='Configuration file path (default: config.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape LinkedIn profiles')
    scrape_parser.add_argument('job_type', 
                              help='Job type to search for (use list-types to see available options)')
    scrape_parser.add_argument('--email', help='LinkedIn email')
    scrape_parser.add_argument('--password', help='LinkedIn password')
    scrape_parser.add_argument('--company', help='Filter by company name')
    scrape_parser.add_argument('--max-profiles', type=int, default=200,
                              help='Maximum number of profiles to scrape (default: 200)')
    scrape_parser.add_argument('--formats', nargs='+', choices=['json', 'csv'], 
                              default=['json'], help='Output formats (default: json)')
    scrape_parser.add_argument('--output', help='Output filename prefix (without extension)')
    scrape_parser.add_argument('--headless', action='store_true', default=None,
                              help='Run browser in headless mode')
    scrape_parser.add_argument('--no-headless', dest='headless', action='store_false',
                              help='Run browser with GUI (useful for debugging)')
    
    # List types command
    list_parser = subparsers.add_parser('list-types', help='List available job types')
    
    # Create config command
    config_parser = subparsers.add_parser('create-config', help='Create sample configuration file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == 'scrape':
        return scrape_job_type(args)
    elif args.command == 'list-types':
        list_job_types(args)
        return 0
    elif args.command == 'create-config':
        create_sample_config(args)
        return 0
    
    return 0

if __name__ == '__main__':
    sys.exit(main())