#!/bin/bash

# Script pour automatiser le processus complet de téléchargement et mise à jour des logos
# Utilisation: ./process_channels.sh [fichier_embed_channels.json] [output_file]

set -e  # Arrêter le script en cas d'erreur

# Vérifier les dépendances
check_dependencies() {
    echo "Vérification des dépendances..."
    
    # Vérifier Python et pip
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 n'est pas installé. Veuillez l'installer."
        exit 1
    fi
    
    # Vérifier git
    if ! command -v git &> /dev/null; then
        echo "Git n'est pas installé. Veuillez l'installer."
        exit 1
    fi
    
    # Vérifier les packages Python requis
    python3 -c "import requests" 2>/dev/null || {
        echo "Le package 'requests' n'est pas installé."
        echo "Veuillez l'installer avec: pip install requests"
        exit 1
    }
    
    echo "Toutes les dépendances sont installées."
}

# Paramètres
CHANNELS_FILE=${1:-"embed-channels.json"}
OUTPUT_FILE=${2:-"embed-channels-secure.json"}
LOGOS_DATA="logos_data.json"
MAPPING_FILE="logo_mapping.json"
LOGOS_DIR="logos"
LIMIT=${3:-0}  # Nombre d'URLs à traiter (0 = toutes)

# Vérifier que le fichier source existe
if [ ! -f "$CHANNELS_FILE" ]; then
    echo "Erreur: Le fichier $CHANNELS_FILE n'existe pas."
    exit 1
fi

# Vérifier les dépendances
check_dependencies

# Créer le répertoire des logos s'il n'existe pas
mkdir -p "$LOGOS_DIR"

echo "=== Démarrage du processus de sécurisation des logos ==="
echo "Fichier source: $CHANNELS_FILE"
echo "Fichier de sortie: $OUTPUT_FILE"
if [ "$LIMIT" -gt 0 ]; then
    echo "Limite: $LIMIT logos"
fi
echo

# Étape 1: Extraire les URLs des logos HTTP
echo "1. Extraction des URLs des logos non sécurisés..."
python3 extract_logos.py "$CHANNELS_FILE" "$LOGOS_DATA"
echo

# Vérifier si des URLs ont été trouvées
if [ ! -s "$LOGOS_DATA" ]; then
    echo "Aucune URL HTTP trouvée. Rien à faire."
    exit 0
fi

# Étape 2: Télécharger les logos et créer les URLs sécurisées
echo "2. Téléchargement des logos et création des URLs sécurisées..."
if [ "$LIMIT" -gt 0 ]; then
    python3 download_and_upload_logos.py "$LOGOS_DATA" --output "$MAPPING_FILE" --limit "$LIMIT"
else
    python3 download_and_upload_logos.py "$LOGOS_DATA" --output "$MAPPING_FILE"
fi
echo

# Vérifier si le téléchargement a réussi
if [ ! -f "$MAPPING_FILE" ]; then
    echo "Erreur: Le téléchargement des logos a échoué."
    exit 1
fi

# Étape 3: Mettre à jour le fichier JSON avec les nouvelles URLs
echo "3. Mise à jour du fichier JSON avec les URLs sécurisées..."
python3 update_channel_logos.py "$CHANNELS_FILE" "$MAPPING_FILE" --output "$OUTPUT_FILE"
echo

echo "=== Processus terminé ==="
echo "Le fichier $OUTPUT_FILE contient maintenant les URLs sécurisées des logos."
echo

exit 0 