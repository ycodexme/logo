import json

# Lire le fichier JSON
with open('embed.json', 'r', encoding='utf-8') as file:
    channels = json.load(file)

# Créer un dictionnaire pour stocker les chaînes par catégorie
categories = {}

# Parcourir toutes les chaînes et les regrouper par catégorie
for channel in channels:
    category = channel.get('category', 'UNCATEGORIZED')
    if category not in categories:
        categories[category] = []
    
    # Supprimer la clé category de l'objet channel
    channel_copy = channel.copy()
    if 'category' in channel_copy:
        del channel_copy['category']
    
    categories[category].append(channel_copy)

# Sauvegarder le fichier réorganisé
with open('embed-channels.json', 'w', encoding='utf-8') as file:
    json.dump(categories, file, indent=2, ensure_ascii=False)

print("Les chaînes ont été réorganisées par catégorie avec succès dans embed-channels.json") 