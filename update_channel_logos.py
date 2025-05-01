#!/usr/bin/env python3
import json
import os
import sys
import argparse

def update_channel_logos(channels_file, mapping_file, output_file=None):
    """
    Mettre à jour les URLs des logos dans le fichier embed-channels.json
    avec les URLs sécurisées HTTPS provenant du fichier de mapping.
    
    Args:
        channels_file: Chemin vers le fichier embed-channels.json
        mapping_file: Chemin vers le fichier de mapping (URLs HTTP -> HTTPS)
        output_file: Chemin vers le fichier de sortie (si différent de channels_file)
    """
    try:
        # Charger le fichier des chaînes
        with open(channels_file, 'r', encoding='utf-8') as f:
            channels_data = json.load(f)
        
        # Charger le fichier de mapping
        with open(mapping_file, 'r', encoding='utf-8') as f:
            url_mapping = json.load(f)
        
        # Compteurs
        total_urls = 0
        updated_urls = 0
        
        # Mettre à jour les URLs des logos
        for country_code, channels in channels_data.items():
            for channel in channels:
                if 'logo' in channel:
                    total_urls += 1
                    # Si l'URL du logo est dans le mapping, la remplacer
                    if channel['logo'] in url_mapping:
                        channel['logo'] = url_mapping[channel['logo']]
                        updated_urls += 1
        
        # Déterminer le fichier de sortie
        out_file = output_file if output_file else channels_file
        
        # Écrire le fichier mis à jour
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(channels_data, f, indent=2, ensure_ascii=False)
        
        print(f"Mise à jour terminée:")
        print(f"  - Total des logos: {total_urls}")
        print(f"  - Logos mis à jour: {updated_urls}")
        print(f"  - Fichier mis à jour: {out_file}")
        
        return updated_urls
    
    except Exception as e:
        print(f"Erreur lors de la mise à jour des logos: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description='Mettre à jour les URLs des logos dans le fichier embed-channels.json')
    parser.add_argument('channels_file', help='Fichier embed-channels.json à mettre à jour')
    parser.add_argument('mapping_file', help='Fichier de mapping (HTTP -> HTTPS)')
    parser.add_argument('--output', '-o', help='Fichier de sortie (si différent du fichier d\'entrée)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.channels_file):
        print(f"Le fichier {args.channels_file} n'existe pas.")
        sys.exit(1)
    
    if not os.path.exists(args.mapping_file):
        print(f"Le fichier {args.mapping_file} n'existe pas.")
        sys.exit(1)
    
    update_channel_logos(args.channels_file, args.mapping_file, args.output)

if __name__ == "__main__":
    main() 