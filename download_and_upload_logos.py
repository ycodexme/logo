#!/usr/bin/env python3
import os
import sys
import requests
import hashlib
import argparse
import json
import time
import subprocess
from pathlib import Path
from urllib.parse import urlparse

# Configuration
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
LOGOS_DIR = os.path.join(REPO_PATH, "logos")
GITHUB_REPO_URL = "https://github.com/ycodexme/logo.git"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/ycodexme/logo/main/logos/"

def ensure_dir_exists(dir_path):
    """Ensure the specified directory exists"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def download_logo(url, save_path):
    """Download logo from insecure URL and save it locally"""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Save the file
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_file_extension(url, content_type=None):
    """Get file extension from URL or content-type"""
    # Try to get extension from URL path
    parsed_url = urlparse(url)
    path = parsed_url.path
    ext = os.path.splitext(path)[1].lower()
    
    if ext and ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
        return ext
    
    # Fallback to content-type if available
    if content_type:
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        elif 'svg' in content_type:
            return '.svg'
        elif 'webp' in content_type:
            return '.webp'
    
    # Default to .png if we can't determine
    return '.png'

def get_secure_url(filename):
    """Generate secure HTTPS URL for the uploaded logo"""
    return f"{GITHUB_RAW_URL}{filename}"

def commit_and_push_changes(message):
    """Commit and push changes to GitHub using subprocess"""
    try:
        # Add all new and changed files
        subprocess.run(['git', 'add', '--all'], cwd=REPO_PATH, check=True)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', message], cwd=REPO_PATH, check=True)
        
        # Push changes
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_PATH, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error committing and pushing changes: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def process_urls_from_file(input_file, output_file=None):
    """Process URLs from an input file and save results to output file"""
    # Create directory for logos if it doesn't exist
    ensure_dir_exists(LOGOS_DIR)
    
    results = {}
    urls_processed = 0
    
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    total_urls = len(urls)
    print(f"Found {total_urls} URLs to process")
    
    for i, url in enumerate(urls):
        print(f"Processing {i+1}/{total_urls}: {url}")
        
        # Generate a unique filename based on URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Try to get file info
        try:
            head_response = requests.head(url, timeout=5)
            content_type = head_response.headers.get('Content-Type', '')
            file_ext = get_file_extension(url, content_type)
        except:
            # If head request fails, guess extension from URL
            file_ext = get_file_extension(url)
        
        filename = f"{url_hash}{file_ext}"
        save_path = os.path.join(LOGOS_DIR, filename)
        
        # Download the logo
        if download_logo(url, save_path):
            secure_url = get_secure_url(filename)
            results[url] = secure_url
            urls_processed += 1
            
            # Commit every 10 files to avoid large commits
            if urls_processed % 10 == 0:
                commit_and_push_changes(f"Add {urls_processed} logos")
                print(f"Committed and pushed {urls_processed} logos")
        
        # Add a small delay to avoid overwhelming the server
        time.sleep(0.5)
    
    # Final commit for any remaining files
    if urls_processed % 10 != 0:
        commit_and_push_changes(f"Add remaining logos, total: {urls_processed}")
    
    # Save results to output file if specified
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    print(f"Processed {urls_processed} URLs successfully")
    return results

def main():
    parser = argparse.ArgumentParser(description='Download logos from insecure URLs and upload to GitHub')
    parser.add_argument('input_file', help='File containing list of URLs to process (one per line)')
    parser.add_argument('--output', '-o', help='Output file to save URL mapping (original -> secure)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file {args.input_file} does not exist")
        sys.exit(1)
    
    process_urls_from_file(args.input_file, args.output)

if __name__ == "__main__":
    main() 