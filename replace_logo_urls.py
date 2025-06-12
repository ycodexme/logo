#!/usr/bin/env python3
import json
import os
import sys
import argparse
from pathlib import Path

def replace_logo_urls(source_file, target_file, output_file):
    """
    Remplace les URLs des logos dans le fichier cible par celles du fichier source.
    
    Args:
        source_file: Fichier JSON source contenant les nouvelles URLs (merged_output.json)
        target_file: Fichier JSON cible où remplacer les URLs (cdn copy.json)
        output_file: Fichier de sortie
    """
    print(f"Lecture du fichier source {source_file}...")
    with open(source_file, 'r', encoding='utf-8') as f:
        source_data = json.load(f)
    
    print(f"Lecture du fichier cible {target_file}...")
    with open(target_file, 'r', encoding='utf-8') as f:
        target_data = json.load(f)
    
    # Créer un dictionnaire de correspondance nom -> logo URL
    logo_mapping = {}
    urls_count = 0
    
    # Extraire toutes les correspondances nom -> logo URL du fichier source
    print("Création du mapping des logos...")
    for category, items in source_data.items():
        for item in items:
            if 'name' in item and 'logo' in item and item['logo']:
                name = item['name'].strip()
                logo_mapping[name] = item['logo']
                urls_count += 1
    
    print(f"Trouvé {urls_count} URLs de logos dans le fichier source")
    
    # Remplacer les URLs dans le fichier cible
    replacements = 0
    not_found = 0
    
    print("Remplacement des URLs dans le fichier cible...")
    for category, items in target_data.items():
        for item in items:
            if 'name' in item and 'logo' in item:
                name = item['name'].strip()
                if name in logo_mapping:
                    old_url = item['logo']
                    new_url = logo_mapping[name]
                    if old_url != new_url:
                        item['logo'] = new_url
                        replacements += 1
                else:
                    not_found += 1
    
    # Sauvegarder le résultat
    print(f"Sauvegarde du fichier modifié vers {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(target_data, f, indent=2, ensure_ascii=False)
    
    print(f"Remplacement terminé avec succès!")
    print(f"Statistiques:")
    print(f"  - URLs de logos trouvées dans le fichier source: {urls_count}")
    print(f"  - URLs remplacées dans le fichier cible: {replacements}")
    print(f"  - Éléments sans correspondance: {not_found}")

def main():
    parser = argparse.ArgumentParser(description='Remplacer les URLs des logos dans un fichier JSON')
    parser.add_argument('--source', '-s', default='merged_output.json', 
                        help='Fichier JSON source contenant les nouvelles URLs (par défaut: merged_output.json)')
    parser.add_argument('--target', '-t', default='cdn copy.json', 
                        help='Fichier JSON cible où remplacer les URLs (par défaut: cdn copy.json)')
    parser.add_argument('--output', '-o', default='cdn_updated.json', 
                        help='Fichier de sortie (par défaut: cdn_updated.json)')
    
    args = parser.parse_args()
    
    # Vérifier si les fichiers existent
    if not os.path.exists(args.source):
        print(f"Erreur: Le fichier source {args.source} n'existe pas")
        sys.exit(1)
    
    if not os.path.exists(args.target):
        print(f"Erreur: Le fichier cible {args.target} n'existe pas")
        sys.exit(1)
    
    # Créer le répertoire de sortie si nécessaire
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Remplacer les URLs
    replace_logo_urls(args.source, args.target, args.output)

if __name__ == "__main__":
    main() 