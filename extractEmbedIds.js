"use strict";
import fs from 'fs';
import path from 'path';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import channelsData from '../src/data/cdn.json' with { type: 'json' };

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Fonction pour générer un ID unique à partir du nom de la chaîne
const generateChannelId = (name) => {
  return name
    .toLowerCase()
    .replace(/[\s&+]+/g, '-')  // Remplace les espaces, & et + par des tirets
    .replace(/[^a-z0-9-]/g, '') // Supprime les caractères non alphanumériques
    .replace(/-{2,}/g, '-')     // Remplace les tirets multiples par un seul
    .replace(/^-|-$/g, '');     // Supprime les tirets au début et à la fin
};

const extractEmbedIds = () => {
    // Créer un objet qui conserve la même structure que cdn.json
    const embedChannels = {};
    
    // Parcourir toutes les catégories
    Object.entries(channelsData).forEach(([category, categoryChannels]) => {
        // Initialiser la catégorie si elle n'existe pas encore
        if (!embedChannels[category]) {
            embedChannels[category] = [];
        }
        
        // Transformer chaque chaîne
        categoryChannels.forEach(channel => {
            // Générer l'ID pour l'URL d'embed
            const channelId = generateChannelId(channel.name);
            
            // Créer une nouvelle entrée qui conserve la structure originale
            embedChannels[category].push({
                name: channel.name,
                logo: channel.logo,
                embed_url: `https://frenchtv.fun/embed/${channelId}`
            });
        });
    });
    
    // Créer le dossier data s'il n'existe pas
    const dataDir = path.join(__dirname, '../src/data');
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
    }
    
    // Écrire dans le fichier JSON
    const outputPath = path.join(dataDir, 'embedUrls.json');
    fs.writeFileSync(outputPath, JSON.stringify(embedChannels, null, 2));
    
    // Calculer le nombre total de chaînes
    const totalChannels = Object.values(embedChannels).reduce(
        (total, channels) => total + channels.length, 0
    );
    
    console.log(`Fichier JSON créé avec succès à ${outputPath}`);
    console.log(`Nombre total de chaînes traitées: ${totalChannels}`);
};

extractEmbedIds();
