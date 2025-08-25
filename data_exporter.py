"""
Data export utilities for LinkedIn Scraper
"""
import json
import csv
import os
from typing import List, Dict, Any
from datetime import datetime

class DataExporter:
    """Handle data export to various formats"""
    
    def __init__(self, config):
        self.config = config
    
    def export_data(self, data: List[Dict[str, Any]], formats: List[str] = None) -> Dict[str, str]:
        """
        Export data to specified formats
        Returns dictionary with format -> filename mapping
        """
        if not data:
            print("⚠️ No data to export")
            return {}
        
        if formats is None:
            formats = self.config.get('output.formats', ['json'])
        
        exported_files = {}
        
        # Add metadata to data
        export_metadata = {
            'exported_at': datetime.now().isoformat(),
            'total_profiles': len(data),
            'version': '2.0'
        }
        
        if 'json' in formats:
            json_file = self._export_json(data, export_metadata)
            exported_files['json'] = json_file
        
        if 'csv' in formats:
            csv_file = self._export_csv(data)
            exported_files['csv'] = csv_file
        
        return exported_files
    
    def _export_json(self, data: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """Export data to JSON format"""
        json_file = self.config.get('output.json_file', 'linkedin_profiles.json')
        
        json_data = {
            'metadata': metadata,
            'profiles': data
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(data)} profiles to {json_file}")
        return json_file
    
    def _export_csv(self, data: List[Dict[str, Any]]) -> str:
        """Export data to CSV format"""
        csv_file = self.config.get('output.csv_file', 'linkedin_profiles.csv')
        
        if not data:
            return csv_file
        
        # Determine all possible fields from the data
        all_fields = set()
        for profile in data:
            all_fields.update(profile.keys())
        
        # Define the field order (put important fields first)
        important_fields = ['name', 'profile_url', 'headline', 'location', 'company']
        ordered_fields = []
        
        # Add important fields first if they exist
        for field in important_fields:
            if field in all_fields:
                ordered_fields.append(field)
                all_fields.remove(field)
        
        # Add remaining fields
        ordered_fields.extend(sorted(all_fields))
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_fields)
            writer.writeheader()
            
            for profile in data:
                # Fill missing fields with empty strings
                row = {field: profile.get(field, '') for field in ordered_fields}
                writer.writerow(row)
        
        print(f"✅ Exported {len(data)} profiles to {csv_file}")
        return csv_file
    
    def load_existing_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load existing data from JSON file"""
        if not os.path.exists(file_path):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle different JSON formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'profiles' in data:
                    return data['profiles']
                else:
                    # Convert single dict to list
                    return [data]
            
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def merge_data(self, existing_data: List[Dict[str, Any]], new_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge new data with existing data, avoiding duplicates"""
        if not existing_data:
            return new_data
        
        # Create a set of existing URLs for fast lookup
        existing_urls = {profile.get('profile_url', '') for profile in existing_data}
        
        # Add new profiles that don't already exist
        merged_data = existing_data.copy()
        new_count = 0
        
        for profile in new_data:
            profile_url = profile.get('profile_url', '')
            if profile_url and profile_url not in existing_urls:
                merged_data.append(profile)
                existing_urls.add(profile_url)
                new_count += 1
        
        if new_count > 0:
            print(f"✅ Added {new_count} new profiles to existing {len(existing_data)} profiles")
        else:
            print("ℹ️ No new profiles to add (all were duplicates)")
        
        return merged_data