const https = require('https');
const fs = require('fs');
const path = require('path');

const characterId = 'bdbc632a-3392-40e4-bd60-6e5bc94bfb2a';
const backgroundJobId = '89195bd0-4b91-4b88-b81c-78c3c2292466';
const apiToken = '1a51fb7c-3213-488b-b7e0-c98dfdbafc8b';
const outputDir = 'C:\\frontier\\sprites\\frontiersman-128x128';

const directions = [
  'south', 'north', 'east', 'west',
  'south-east', 'north-east', 'north-west', 'south-west'
];

function makeRequest(url) {
  return new Promise((resolve, reject) => {
    https.get(url, {
      headers: {
        'Authorization': `Bearer ${apiToken}`
      }
    }, (response) => {
      let data = '';
      response.on('data', chunk => data += chunk);
      response.on('end', () => {
        if (response.statusCode === 200) {
          resolve(JSON.parse(data));
        } else {
          reject(new Error(`HTTP ${response.statusCode}: ${data}`));
        }
      });
    }).on('error', reject);
  });
}

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

async function pollJob() {
  console.log('Polling background job...');
  const maxAttempts = 40; // 40 * 15 seconds = 10 minutes max

  for (let i = 0; i < maxAttempts; i++) {
    try {
      const jobStatus = await makeRequest(
        `https://api.pixellab.ai/v2/background-jobs/${backgroundJobId}`
      );

      console.log(`Attempt ${i + 1}/${maxAttempts}: Status = ${jobStatus.status}`);

      if (jobStatus.status === 'completed') {
        console.log('✅ Job completed!');
        return true;
      } else if (jobStatus.status === 'failed') {
        console.error('❌ Job failed:', jobStatus.error);
        return false;
      }

      // Wait 15 seconds before next poll
      await new Promise(resolve => setTimeout(resolve, 15000));
    } catch (error) {
      console.error(`Error polling job:`, error.message);
      await new Promise(resolve => setTimeout(resolve, 15000));
    }
  }

  console.error('❌ Timeout: Job did not complete within 10 minutes');
  return false;
}

async function downloadSprites() {
  console.log('\nFetching character data...');
  const character = await makeRequest(
    `https://api.pixellab.ai/v2/characters/${characterId}`
  );

  console.log(`Character: ${character.name}`);
  console.log(`Size: ${character.size.width}x${character.size.height}`);

  // Create output directory
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log('\nDownloading sprites...');
  for (const direction of directions) {
    const url = character.rotation_urls[direction];
    const outputPath = path.join(outputDir, `${direction}.png`);

    try {
      await downloadFile(url, outputPath);
      console.log(`✅ Saved: ${direction}.png`);
    } catch (error) {
      console.error(`❌ Failed to download ${direction}:`, error.message);
    }
  }

  console.log('\n✅ All sprites downloaded successfully!');
  console.log(`Location: ${outputDir}`);
}

async function main() {
  console.log('🎨 PixelLab Frontiersman Character Generator\n');
  console.log(`Character ID: ${characterId}`);
  console.log(`Job ID: ${backgroundJobId}\n`);

  const success = await pollJob();

  if (success) {
    await downloadSprites();
  } else {
    console.error('\n❌ Failed to generate character');
    process.exit(1);
  }
}

main().catch(console.error);
