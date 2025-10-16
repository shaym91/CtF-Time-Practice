#!/usr/bin/env python3
"""
Remove flag fields from all challenge info.json files
"""

import json
import os
import glob

def remove_flag_from_info_json(file_path):
    """Remove the flag field from an info.json file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Remove flag field if it exists
        if 'flag' in data:
            del data['flag']
            print(f"✅ Removed flag from {file_path}")
        else:
            print(f"ℹ️  No flag found in {file_path}")
        
        # Write back the cleaned data
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        return True
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main function to process all info.json files"""
    print("🔧 Removing flag fields from all challenge info.json files...")
    print("=" * 60)
    
    # Find all info.json files in the static/files directory
    pattern = "static/files/*/info.json"
    info_files = glob.glob(pattern)
    
    if not info_files:
        print("❌ No info.json files found!")
        return
    
    success_count = 0
    total_count = len(info_files)
    
    for file_path in info_files:
        if remove_flag_from_info_json(file_path):
            success_count += 1
    
    print("=" * 60)
    print(f"✅ Successfully processed {success_count}/{total_count} files")
    print("🎯 All flags removed from downloadable files!")
    print("=" * 60)

if __name__ == "__main__":
    main()
