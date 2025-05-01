import json

# Lire les deux fichiers JSON
with open('embed-cnnels.json', 'r', encoding='utf-8') as file:
    cnnels_data = json.load(file)

with open('embed-channels.json', 'r', encoding='utf-8') as file:
    channels_data = json.load(file)

# Créer un dictionnaire pour faciliter la recherche des URLs
url_mapping = {item['name']: item['embed_url'] for item in cnnels_data}

# Parcourir toutes les catégories et leurs chaînes
for category in channels_data:
    for channel in channels_data[category]:
        # Si le nom de la chaîne existe dans le mapping, mettre à jour l'URL
        if channel['name'] in url_mapping:
            channel['embed_url'] = url_mapping[channel['name']]

# Sauvegarder le fichier modifié
with open('embed-channels.json', 'w', encoding='utf-8') as file:
    json.dump(channels_data, file, indent=2, ensure_ascii=False)

print("Les URLs d'embed ont été mises à jour avec succès dans embed-channels.json") 