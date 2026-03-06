const https = require('https');
const fs = require('fs');
const path = require('path');

const characterId = 'd0b6e12d-9c4e-4568-8748-38fb0fafff41';
const outputDir = 'C:\\frontier\\sprites\\warrior-64x64';

const directions = [
  'south', 'north', 'east', 'west',
  'south-east', 'north-east', 'north-west', 'south-west'
];

const urls = {
  "south": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/south.png?t=1772062893797",
  "west": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/west.png?t=1772062893797",
  "east": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/east.png?t=1772062893797",
  "north": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/north.png?t=1772062893797",
  "south-east": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/south-east.png?t=1772062893797",
  "north-east": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/north-east.png?t=1772062893797",
  "north-west": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/north-west.png?t=1772062893797",
  "south-west": "https://backblaze.pixellab.ai/file/pixellab-characters/231b37ee-f022-4ac6-bae0-c6f1ec5245aa/d0b6e12d-9c4e-4568-8748-38fb0fafff41/rotations/south-west.png?t=1772062893797"
};

function downloadFile(url, outputPath) {
  return new Promise((resolve, reject) => {
    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      const fileStream = fs.createWriteStream(outputPath);
      response.pipe(fileStream);

      fileStream.on('finish', () => {
        fileStream.close();
        resolve();
      });

      fileStream.on('error', (err) => {
        fs.unlink(outputPath, () => {});
        reject(err);
      });
    }).on('error', reject);
  });
}

async function downloadAllSprites() {
  for (const direction of directions) {
    const url = urls[direction];
    const outputPath = path.join(outputDir, `${direction}.png`);

    try {
      await downloadFile(url, outputPath);
      console.log(`Saved: ${outputPath}`);
    } catch (error) {
      console.error(`Failed to download ${direction}:`, error.message);
    }
  }
}

downloadAllSprites().catch(console.error);
