#!/usr/bin/env python3
import os
import sys
import requests
import hashlib
import argparse
import json
import time
import subprocess
import re
import concurrent.futures
from pathlib import Path
from urllib.parse import urlparse

# Configuration
REPO_PATH = os.path.dirname(os.path.abspath(__file__))
LOGOS_DIR = os.path.join(REPO_PATH, "logos_new")
GITHUB_REPO_URL = "https://github.com/ycodexme/logo.git"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/ycodexme/logo/main/logos_new/"
MAX_WORKERS = 10  # Nombre de threads parallèles

def ensure_dir_exists(dir_path):
    """Ensure the specified directory exists"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def clean_filename(name):
    """Convertit un nom de chaîne en nom de fichier valide"""
    # Remplacer les caractères spéciaux et espaces par des tirets
    clean_name = re.sub(r'[^\w\s-]', '', name)
    clean_name = re.sub(r'[\s]+', '-', clean_name)
    return clean_name.lower()

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

def process_logo_item(item, used_names):
    """Process a single logo item"""
    if 'logo' not in item or not item['logo']:
        return None, None
    
    url = item['logo']
    name = item.get('name', '')
    
    # Skip if already HTTPS URL from GitHub
    if url.startswith(GITHUB_RAW_URL):
        return url, None
    
    # Nettoyer le nom pour l'utiliser comme nom de fichier
    clean_name = clean_filename(name)
    
    # Ajouter un suffixe numérique si le nom est déjà utilisé
    base_name = clean_name
    counter = 1
    while clean_name in used_names:
        clean_name = f"{base_name}-{counter}"
        counter += 1
    
    used_names[clean_name] = True
    
    # Déterminer l'extension du fichier
    try:
        head_response = requests.head(url, timeout=5)
        content_type = head_response.headers.get('Content-Type', '')
        file_ext = get_file_extension(url, content_type)
    except:
        # If head request fails, guess extension from URL
        file_ext = get_file_extension(url)
    
    filename = f"{clean_name}{file_ext}"
    save_path = os.path.join(LOGOS_DIR, filename)
    
    # Download the logo
    if download_logo(url, save_path):
        secure_url = get_secure_url(filename)
        return url, secure_url
    
    return None, None

def process_loadbalancer_json(input_file, output_file=None, limit=None, num_workers=MAX_WORKERS):
    """Process loadbalancer.json file, replace insecure logo URLs with secure ones"""
    # Create directory for logos if it doesn't exist
    ensure_dir_exists(LOGOS_DIR)
    
    # Load the loadbalancer.json file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Dictionary to track used filenames
    used_names = {}
    
    # Dictionary to store original URL to secure URL mapping
    url_mapping = {}
    
    # Count for batch commits
    urls_processed = 0
    urls_to_process = 0
    
    # Count total URLs to process
    for category, items in data.items():
        for item in items:
            if 'logo' in item and item['logo'] and not item['logo'].startswith(GITHUB_RAW_URL):
                urls_to_process += 1
    
    print(f"Found {urls_to_process} logo URLs to process")
    
    # Process each category in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_item = {}
        
        # Submit tasks for each logo URL
        for category, items in data.items():
            # Apply limit if specified
            if limit and limit > 0:
                items = items[:limit]
            
            for item in items:
                if 'logo' in item and item['logo'] and not item['logo'].startswith(GITHUB_RAW_URL):
                    future = executor.submit(process_logo_item, item, used_names)
                    future_to_item[future] = (category, item)
        
        # Process completed tasks
        for future in concurrent.futures.as_completed(future_to_item):
            category, item = future_to_item[future]
            try:
                original_url, secure_url = future.result()
                if original_url and secure_url:
                    url_mapping[original_url] = secure_url
                    item['logo'] = secure_url  # Update the URL in the data
                    urls_processed += 1
                    
                    print(f"Processed {urls_processed}/{urls_to_process}: {item.get('name', '')} ({original_url} -> {secure_url})")
                    
                    # Commit every 20 files to avoid large commits
                    if urls_processed % 20 == 0:
                        commit_and_push_changes(f"Add {urls_processed} logos")
                        print(f"Committed and pushed {urls_processed} logos")
            except Exception as e:
                print(f"Error processing {item.get('name', '')}: {e}")
    
    # Final commit for any remaining files
    if urls_processed % 20 != 0:
        commit_and_push_changes(f"Add remaining logos, total: {urls_processed}")
    
    # Save updated loadbalancer.json
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save URL mapping to output file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(url_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"Processed {urls_processed} URLs successfully")
    print(f"Updated loadbalancer.json with secure URLs")
    return url_mapping

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download logos from insecure URLs, upload to GitHub, and update loadbalancer.json')
    parser.add_argument('--input', '-i', default='loadbalancer.json', help='Input JSON file (default: loadbalancer.json)')
    parser.add_argument('--output', '-o', help='Output file to save URL mapping (original -> secure)')
    parser.add_argument('--limit', '-l', type=int, help='Limit the number of URLs to process per category')
    parser.add_argument('--threads', '-t', type=int, default=MAX_WORKERS, help=f'Number of threads to use (default: {MAX_WORKERS})')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        sys.exit(1)
    
    # Process the loadbalancer.json file with the specified number of threads
    process_loadbalancer_json(args.input, args.output, args.limit, args.threads)

if __name__ == "__main__":
    main() 