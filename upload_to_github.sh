#!/bin/bash

# Script pour préparer et téléverser les logos vers GitHub
# Utilisation: ./upload_to_github.sh [répertoire_des_logos]

LOGO_DIR=${1:-"./logos-new"}
GITHUB_REPO="logo"
GITHUB_BRANCH="main"
GITHUB_FOLDER="logos-new"

# Vérifier que le répertoire existe
if [ ! -d "$LOGO_DIR" ]; then
  echo "Erreur: Le répertoire $LOGO_DIR n'existe pas."
  exit 1
fi

# Compter les logos disponibles
LOGO_COUNT=$(find "$LOGO_DIR" -type f | wc -l)
if [ "$LOGO_COUNT" -eq 0 ]; then
  echo "Aucun logo trouvé dans $LOGO_DIR."
  exit 1
fi

echo "=== Préparation pour téléversement vers GitHub ==="
echo "Répertoire des logos: $LOGO_DIR"
echo "Nombre de logos: $LOGO_COUNT"
echo

# Vérifier si git est disponible
if ! command -v git &> /dev/null; then
  echo "Erreur: git n'est pas installé ou pas disponible."
  exit 1
fi

# Vérifier si GitHub CLI est disponible
if ! command -v gh &> /dev/null; then
  echo "Note: GitHub CLI (gh) n'est pas installé. L'authentification devra être gérée manuellement."
fi

echo "Options pour téléverser les logos vers GitHub:"
echo "1. Cloner le dépôt localement, ajouter les logos et pousser les changements"
echo "2. Créer un script pour téléverser les logos via l'API GitHub"
echo "3. Préparer les logos pour un téléversement manuel via l'interface GitHub"
echo

read -p "Choisissez une option (1-3): " CHOICE

case $CHOICE in
  1)
    echo "=== Option 1: Cloner et pousser via Git ==="
    
    read -p "Entrez l'URL du dépôt GitHub (ex: https://github.com/username/logo.git): " REPO_URL
    
    # Créer un répertoire temporaire
    TEMP_DIR=$(mktemp -d)
    echo "Clonage du dépôt dans $TEMP_DIR..."
    
    # Cloner le dépôt
    git clone "$REPO_URL" "$TEMP_DIR" || { echo "Erreur lors du clonage"; exit 1; }
    
    # Créer le dossier de destination s'il n'existe pas
    mkdir -p "$TEMP_DIR/$GITHUB_FOLDER"
    
    # Copier les logos
    echo "Copie des logos..."
    cp "$LOGO_DIR"/* "$TEMP_DIR/$GITHUB_FOLDER/"
    
    # Ajouter, commiter et pousser
    cd "$TEMP_DIR" || exit 1
    git add "$GITHUB_FOLDER"/*
    git commit -m "Add new channel logos"
    
    echo "Pousser les changements vers GitHub..."
    git push
    
    echo "Nettoyage..."
    rm -rf "$TEMP_DIR"
    
    echo "Téléversement terminé avec succès!"
    ;;
    
  2)
    echo "=== Option 2: Téléversement via l'API GitHub ==="
    
    read -p "Entrez votre nom d'utilisateur GitHub: " GITHUB_USER
    read -p "Entrez le nom du dépôt: " GITHUB_REPO
    
    echo "Pour utiliser cette option, vous devez avoir un token d'accès GitHub."
    echo "Vous pouvez créer un token d'accès à https://github.com/settings/tokens"
    read -p "Entrez votre token d'accès GitHub: " GITHUB_TOKEN
    
    echo "Création d'un script pour téléverser les logos..."
    
    # Créer un script pour téléverser les logos
    UPLOAD_SCRIPT="upload_logos.py"
    cat > "$UPLOAD_SCRIPT" << EOF
#!/usr/bin/env python3
import os
import base64
import requests
import time
import sys

# Configuration
github_user = "$GITHUB_USER"
github_repo = "$GITHUB_REPO"
github_token = "$GITHUB_TOKEN"
github_branch = "$GITHUB_BRANCH"
github_folder = "$GITHUB_FOLDER"
logos_dir = "$LOGO_DIR"

# Configuration de l'API GitHub
api_url = f"https://api.github.com/repos/{github_user}/{github_repo}/contents/{github_folder}"
headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

def upload_file(file_path, file_name):
    """Téléverse un fichier vers GitHub"""
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        
        # Encoder le contenu en base64
        content_encoded = base64.b64encode(content).decode('utf-8')
        
        # Préparer les données pour l'API
        data = {
            "message": f"Add logo: {file_name}",
            "content": content_encoded,
            "branch": github_branch
        }
        
        # Téléverser le fichier
        target_url = f"{api_url}/{file_name}"
        response = requests.put(target_url, json=data, headers=headers)
        
        if response.status_code == 201:
            print(f"✓ {file_name} téléversé avec succès")
            return True
        elif response.status_code == 422:
            print(f"! {file_name} existe déjà, mise à jour...")
            
            # Récupérer le SHA du fichier existant
            get_response = requests.get(target_url, headers=headers)
            if get_response.status_code == 200:
                sha = get_response.json()['sha']
                data['sha'] = sha
                
                # Réessayer avec le SHA
                update_response = requests.put(target_url, json=data, headers=headers)
                if update_response.status_code in [200, 201]:
                    print(f"✓ {file_name} mis à jour avec succès")
                    return True
                else:
                    print(f"✗ Échec de mise à jour de {file_name}: {update_response.status_code}")
                    return False
            else:
                print(f"✗ Impossible de récupérer le SHA pour {file_name}")
                return False
        else:
            print(f"✗ Échec de téléversement de {file_name}: {response.status_code} - {response.text}")
            return False
    
    except Exception as e:
        print(f"✗ Erreur lors du téléversement de {file_name}: {e}")
        return False

# Téléverser tous les logos
logo_files = [f for f in os.listdir(logos_dir) if os.path.isfile(os.path.join(logos_dir, f))]
total_files = len(logo_files)
success_count = 0
fail_count = 0

print(f"Téléversement de {total_files} logos vers GitHub...")

for i, logo_file in enumerate(logo_files):
    file_path = os.path.join(logos_dir, logo_file)
    
    # Afficher la progression
    progress = (i + 1) / total_files * 100
    print(f"[{progress:.1f}%] Téléversement de {logo_file}...")
    
    if upload_file(file_path, logo_file):
        success_count += 1
    else:
        fail_count += 1
    
    # Pause pour éviter les limites de l'API
    time.sleep(0.5)

print(f"\nTéléversement terminé:")
print(f"  - Total: {total_files}")
print(f"  - Réussis: {success_count}")
print(f"  - Échecs: {fail_count}")
EOF
    
    chmod +x "$UPLOAD_SCRIPT"
    
    echo "Script créé: $UPLOAD_SCRIPT"
    echo "Pour téléverser les logos, exécutez: python3 $UPLOAD_SCRIPT"
    ;;
    
  3)
    echo "=== Option 3: Préparation pour téléversement manuel ==="
    
    # Créer une archive des logos
    ARCHIVE_NAME="logos_for_github.zip"
    
    if command -v zip &> /dev/null; then
      echo "Création de l'archive $ARCHIVE_NAME..."
      zip -r "$ARCHIVE_NAME" "$LOGO_DIR"/*
      echo "Archive créée: $ARCHIVE_NAME"
      echo
      echo "Instructions pour le téléversement manuel:"
      echo "1. Connectez-vous à votre compte GitHub"
      echo "2. Accédez à votre dépôt \"$GITHUB_REPO\""
      echo "3. Naviguez vers le dossier \"$GITHUB_FOLDER\""
      echo "4. Cliquez sur \"Add file\" puis \"Upload files\""
      echo "5. Décompressez l'archive localement et téléversez les fichiers"
      echo "6. Ajoutez un message de commit et confirmez"
    else
      echo "La commande 'zip' n'est pas disponible."
      echo "Veuillez téléverser manuellement les fichiers depuis le dossier $LOGO_DIR"
    fi
    ;;
    
  *)
    echo "Option invalide."
    exit 1
    ;;
esac

exit 0 