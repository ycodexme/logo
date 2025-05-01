import json

# Lire le fichier JSON
with open('embed-channels.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Parcourir toutes les catégories et leurs chaînes
for category in data:
    for channel in data[category]:
        # Supprimer la clé "category" si elle existe
        if "category" in channel:
            del channel["category"]

# Sauvegarder le fichier modifié
with open('embed-channels.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("La clé 'category' a été supprimée avec succès de tous les objets.") 