#!/bin/bash

# Script pour tester le processus avec un petit nombre de logos
# Utilisation: ./test_process.sh [nombre_de_logos_à_traiter]

# Nombre de logos à traiter
LIMIT=${1:-10}

# Exécuter le script principal avec une limite
./process_channels.sh embed-channels.json embed-channels-secure.json $LIMIT

echo "Test terminé avec $LIMIT logos." 