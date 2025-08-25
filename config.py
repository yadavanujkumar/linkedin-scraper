"""
Configuration management for LinkedIn Scraper
"""
import json
import os
from typing import Dict, Any

class Config:
    """Configuration manager for LinkedIn scraper settings"""
    
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self.default_config = {
            'linkedin': {
                'email': '',
                'password': ''
            },
            'scraping': {
                'max_profiles': 200,
                'headless': True,
                'max_pages': 20,
                'delay_range': [3, 6]
            },
            'output': {
                'formats': ['json'],  # ['json', 'csv'] or both
                'json_file': 'linkedin_profiles.json',
                'csv_file': 'linkedin_profiles.csv',
                'cache_file': 'profiles_cache.json'
            },
            'search': {
                'default_keyword': 'software engineer',
                'default_company': '',
                'job_types': {
                    'software_developer': 'software developer OR software engineer OR programmer',
                    'data_scientist': 'data scientist OR data analyst OR machine learning engineer',
                    'hr': 'human resources OR HR OR talent acquisition OR recruiter',
                    'marketing': 'marketing manager OR digital marketing OR marketing specialist',
                    'sales': 'sales manager OR sales representative OR business development',
                    'product_manager': 'product manager OR product owner OR product lead',
                    'designer': 'UI designer OR UX designer OR graphic designer OR web designer',
                    'manager': 'manager OR director OR team lead OR supervisor'
                }
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_config(self.default_config, config)
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"⚠️ Could not load config from {self.config_file}, using defaults")
        
        return self.default_config.copy()
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'linkedin.email')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config_ref = self.config
        
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value
    
    def get_job_types(self) -> Dict[str, str]:
        """Get available job types for searching"""
        return self.get('search.job_types', {})
    
    def get_search_keyword(self, job_type: str) -> str:
        """Get search keyword for a specific job type"""
        job_types = self.get_job_types()
        if job_type in job_types:
            return job_types[job_type]
        return job_type  # Return as-is if not in predefined types