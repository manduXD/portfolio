const path = require('path');
const fs = require('fs');

const DATA_DIR = path.join('/tmp', 'data');
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

module.exports = async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    try {
        const body = req.body;
        const data = Buffer.isBuffer(body) ? body : Buffer.from(String(body || ''));
        const timestamp = Date.now();
        const filename = timestamp + '.zip';
        const filepath = path.join(DATA_DIR, filename);
        fs.writeFileSync(filepath, data);
        res.status(200).json({ success: true, filename });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
};
