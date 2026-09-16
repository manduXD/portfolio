const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

module.exports.config = {
    api: {
        bodyParser: false
    }
};

module.exports = async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    try {
        let data;
        if (Buffer.isBuffer(req.body)) {
            data = req.body;
        } else if (typeof req.body === 'string') {
            data = Buffer.from(req.body);
        } else if (req.body && req.body.buffer) {
            data = Buffer.from(req.body.buffer);
        } else {
            data = Buffer.from(JSON.stringify(req.body));
        }
        
        if (data.length === 0) {
            return res.status(400).json({ error: 'No data received' });
        }
        
        const timestamp = Date.now();
        const filename = timestamp + '.zip';
        const filepath = path.join(DATA_DIR, filename);
        fs.writeFileSync(filepath, data);
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        res.status(200).json({ success: true, filename, size: data.length });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
};
