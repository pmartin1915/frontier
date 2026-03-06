// Download and save PixelLab character sprites
const https = require('https');
const fs = require('fs');
const path = require('path');

const CHARACTER_ID = '02912812-0167-45e0-bbce-f304a5a99a8c';
const API_TOKEN = '1a51fb7c-3213-488b-b7e0-c98dfdbafc8b';
const OUTPUT_DIR = path.join(__dirname, 'sprites', 'warrior-48x48');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// Fetch character data
const options = {
  hostname: 'api.pixellab.ai',
  path: `/v2/background-jobs/b8b802c1-a455-4904-87b0-e11b5449aa08`,
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`
  }
};

https.get(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    const response = JSON.parse(data);
    const images = response.last_response.images;

    // Save each direction
    for (const [direction, imageData] of Object.entries(images)) {
      const buffer = Buffer.from(imageData.base64, 'base64');
      const filename = path.join(OUTPUT_DIR, `${direction}.png`);
      fs.writeFileSync(filename, buffer);
      console.log(`Saved: ${filename}`);
    }

    console.log('\n✅ All sprites saved successfully!');
  });
}).on('error', (err) => {
  console.error('Error:', err);
});
