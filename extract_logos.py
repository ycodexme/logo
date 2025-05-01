#!/usr/bin/env python3
import json
import os
import sys
import re

def clean_filename(name):
    """Convertit un nom de chaîne en nom de fichier valide"""
    # Remplacer les caractères spéciaux et espaces par des tirets
    clean_name = re.sub(r'[^\w\s-]', '', name)
    clean_name = re.sub(r'[\s]+', '-', clean_name)
    return clean_name.lower()

def extract_http_logos(input_file, output_file):
    """
    Extraire les URLs de logos non sécurisées (HTTP) du fichier embed-channels.json
    et les écrire dans un fichier texte avec les noms des chaînes.
    """
    try:
        # Charger le fichier JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Collecter les URLs HTTP et les noms des chaînes
        http_urls_with_names = []
        
        # Parcourir toutes les chaînes
        for country_code, channels in data.items():
            for channel in channels:
                if 'logo' in channel and channel['logo'].startswith('http://') and 'name' in channel:
                    http_urls_with_names.append({
                        'url': channel['logo'],
                        'name': channel['name']
                    })
        
        # Écrire les URLs et les noms dans un fichier JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(http_urls_with_names, f, indent=2, ensure_ascii=False)
        
        print(f"Extraction terminée. {len(http_urls_with_names)} URLs de logos HTTP trouvées.")
        print(f"Les données ont été écrites dans {output_file}")
        
        return len(http_urls_with_names)
    
    except Exception as e:
        print(f"Erreur lors de l'extraction des logos: {e}")
        return 0

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_logos.py embed-channels.json logos_data.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Le fichier {input_file} n'existe pas.")
        sys.exit(1)
    
    extract_http_logos(input_file, output_file)

if __name__ == "__main__":
    main() 