# Sécurisation des logos pour embed-channels.json

Ce projet contient des scripts pour télécharger les logos non sécurisés (HTTP) depuis le fichier `embed-channels.json`, les uploader sur GitHub et remplacer les URLs par des versions sécurisées (HTTPS).

## Prérequis

- Python 3.6+
- Git
- Packages Python requis:
  - requests
  - gitpython

## Installation

```bash
pip install requests gitpython
```

## Scripts disponibles

### 1. Processus complet automatisé

Pour automatiser tout le processus en une seule commande, utilisez le script `process_channels.sh`:

```bash
./process_channels.sh [fichier_embed_channels.json] [fichier_sortie]
```

Exemple:
```bash
./process_channels.sh embed-channels.json embed-channels-secure.json
```

Ce script effectue automatiquement les étapes suivantes:
1. Extraction des URLs non sécurisées
2. Téléchargement et upload des logos
3. Mise à jour du fichier JSON avec les nouvelles URLs

### 2. Scripts individuels

Si vous préférez exécuter les étapes séparément:

#### a. Extraction des URLs des logos

```bash
python extract_logos.py embed-channels.json logos_urls.txt
```

Ce script extrait toutes les URLs HTTP du fichier `embed-channels.json` et les écrit dans `logos_urls.txt`.

#### b. Téléchargement et upload des logos

```bash
python download_and_upload_logos.py logos_urls.txt --output logo_mapping.json
```

Ce script télécharge les logos depuis les URLs dans `logos_urls.txt`, les uploade sur GitHub et génère un fichier de mapping `logo_mapping.json` contenant les correspondances entre les URLs originales et les nouvelles URLs sécurisées.

#### c. Mise à jour du fichier JSON

```bash
python update_channel_logos.py embed-channels.json logo_mapping.json --output embed-channels-secure.json
```

Ce script met à jour les URLs des logos dans le fichier `embed-channels.json` avec les URLs sécurisées du fichier de mapping et sauvegarde le résultat dans `embed-channels-secure.json`.

## Fonctionnement

1. Les logos sont téléchargés depuis les URLs HTTP
2. Chaque logo est sauvegardé avec un nom basé sur le hash MD5 de son URL
3. Les fichiers sont uploadés sur GitHub
4. Les URLs dans le fichier JSON sont remplacées par des URLs sécurisées pointant vers le repo GitHub
