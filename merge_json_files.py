#!/usr/bin/env python3
import json
import os
import sys
import argparse
from pathlib import Path
import re

def fix_source_url(url):
    """
    Ajoute l'extension .ts aux URLs qui n'en ont pas déjà.
    """
    if url and isinstance(url, str) and not url.endswith('.ts'):
        return f"{url}.ts"
    return url

def merge_json_files(file1_path, file2_path, output_path):
    """
    Fusionne deux fichiers JSON tout en préservant leurs catégories.
    Ne vérifie pas les doublons.
    Ajoute l'extension .ts aux URLs qui n'en ont pas.
    
    Args:
        file1_path: Chemin vers le premier fichier JSON
        file2_path: Chemin vers le deuxième fichier JSON
        output_path: Chemin où sauvegarder le fichier fusionné
    """
    print(f"Lecture de {file1_path}...")
    with open(file1_path, 'r', encoding='utf-8') as f1:
        data1 = json.load(f1)
    
    print(f"Lecture de {file2_path}...")
    with open(file2_path, 'r', encoding='utf-8') as f2:
        data2 = json.load(f2)
    
    # Créer un dictionnaire pour stocker les données fusionnées
    merged_data = {}
    
    # Compteurs pour les statistiques
    urls_fixed = 0
    
    # Ajouter les catégories et éléments du premier fichier
    print(f"Traitement des catégories du fichier {file1_path}...")
    for category, items in data1.items():
        if category not in merged_data:
            merged_data[category] = []
        
        # Corriger les URLs source_url
        for item in items:
            if 'source_url' in item:
                original_url = item['source_url']
                fixed_url = fix_source_url(original_url)
                if fixed_url != original_url:
                    item['source_url'] = fixed_url
                    urls_fixed += 1
        
        merged_data[category].extend(items)
        print(f"  - Catégorie '{category}': {len(items)} éléments ajoutés")
    
    # Ajouter les catégories et éléments du deuxième fichier
    print(f"Traitement des catégories du fichier {file2_path}...")
    for category, items in data2.items():
        if category not in merged_data:
            merged_data[category] = []
        
        # Corriger les URLs source_url
        for item in items:
            if 'source_url' in item:
                original_url = item['source_url']
                fixed_url = fix_source_url(original_url)
                if fixed_url != original_url:
                    item['source_url'] = fixed_url
                    urls_fixed += 1
        
        merged_data[category].extend(items)
        print(f"  - Catégorie '{category}': {len(items)} éléments ajoutés")
    
    # Calculer les statistiques
    total_categories = len(merged_data)
    total_items = sum(len(items) for items in merged_data.values())
    
    # Sauvegarder le résultat fusionné
    print(f"Sauvegarde du fichier fusionné vers {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(merged_data, outfile, indent=2, ensure_ascii=False)
    
    print(f"Fusion terminée avec succès!")
    print(f"Statistiques:")
    print(f"  - Nombre total de catégories: {total_categories}")
    print(f"  - Nombre total d'éléments: {total_items}")
    print(f"  - Nombre d'URLs corrigées (ajout de .ts): {urls_fixed}")
    
    # Afficher les détails par catégorie
    print("\nDétails par catégorie:")
    for category, items in merged_data.items():
        print(f"  - {category}: {len(items)} éléments")

def main():
    parser = argparse.ArgumentParser(description='Fusionner deux fichiers JSON en préservant les catégories')
    parser.add_argument('--file1', '-f1', default='cdn.json', help='Premier fichier JSON (par défaut: cdn.json)')
    parser.add_argument('--file2', '-f2', default='loadbalancer.json', help='Deuxième fichier JSON (par défaut: loadbalancer.json)')
    parser.add_argument('--output', '-o', default='merged_output.json', help='Fichier de sortie (par défaut: merged_output.json)')
    
    args = parser.parse_args()
    
    # Vérifier si les fichiers d'entrée existent
    if not os.path.exists(args.file1):
        print(f"Erreur: Le fichier {args.file1} n'existe pas")
        sys.exit(1)
    
    if not os.path.exists(args.file2):
        print(f"Erreur: Le fichier {args.file2} n'existe pas")
        sys.exit(1)
    
    # Créer le répertoire de sortie si nécessaire
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Fusionner les fichiers
    merge_json_files(args.file1, args.file2, args.output)

if __name__ == "__main__":
    main() 