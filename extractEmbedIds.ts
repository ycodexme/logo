import fs from 'fs';
import path from 'path';
import { channels } from '../src/data/channels';

interface Channel {
  name: string;
  source_url: string;
  logo: string;
}

interface ChannelWithEmbed {
  name: string;
  embed_url: string;
  category: string;
}

const extractEmbedIds = () => {
  const channelsWithEmbeds: ChannelWithEmbed[] = [];

  // Parcourir toutes les catégories
  Object.entries(channels).forEach(([category, categoryChannels]) => {
    categoryChannels.forEach((channel: Channel) => {
      const url = channel.source_url;
      const match = url.match(/\/(\d+)\.ts$/);
      
      if (match) {
        const embedId = match[1];
        const embedUrl = `https://player.deepvidflow.xyz/embed/${embedId}`;
        
        channelsWithEmbeds.push({
          name: channel.name,
          embed_url: embedUrl,
          category: category
        });
      }
    });
  });

  // Créer le dossier data s'il n'existe pas
  const dataDir = path.join(__dirname, '../src/data');
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  // Écrire dans le fichier JSON
  const outputPath = path.join(dataDir, 'embedUrls.json');
  fs.writeFileSync(outputPath, JSON.stringify(channelsWithEmbeds, null, 2));
  console.log(`Fichier JSON créé avec succès à ${outputPath}`);
};

extractEmbedIds(); 