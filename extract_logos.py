#!/usr/bin/env python3
import json
import os
import sys

def extract_http_logos(input_file, output_file):
    """
    Extraire les URLs de logos non sécurisées (HTTP) du fichier embed-channels.json
    et les écrire dans un fichier texte.
    """
    try:
        # Charger le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Collecter les URLs HTTP
        http_urls = []
        
        # Parcourir toutes les chaînes
        for country_code, channels in data.items():
            for channel in channels:
                if 'logo' in channel and channel['logo'].startswith('http://'):
                    http_urls.append(channel['logo'])
        
        # Écrire les URLs dans un fichier texte
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in http_urls:
                f.write(f"{url}\n")
        
        print(f"Extraction terminée. {len(http_urls)} URLs de logos HTTP trouvées.")
        print(f"Les URLs ont été écrites dans {output_file}")
        
        return len(http_urls)
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des logos: {e}")
        return 0

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_logos.py embed-channels.json logos_urls.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Le fichier {input_file} n'existe pas.")
        sys.exit(1)
    
    extract_http_logos(input_file, output_file)

if __name__ == "__main__":
    main() 