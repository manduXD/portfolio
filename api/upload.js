const path = require('path');
const fs = require('fs');
const os = require('os');

const DATA_DIR = path.join(os.tmpdir(), 'data');

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

function getClientIP(req) {
    return req.headers['x-forwarded-for']?.split(',')[0] ||
           req.headers['x-real-ip'] ||
           (req.socket && req.socket.remoteAddress) ||
           (req.connection && req.connection.remoteAddress) ||
           'unknown';
}

module.exports = async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    try {
        const clientIP = getClientIP(req);
        const timestamp = Date.now();
        const safeIP = clientIP.replace(/[^a-zA-Z0-9]/g, '_');
        const filename = timestamp + '_' + safeIP + '.zip';
        const filepath = path.join(DATA_DIR, filename);
        
        const body = req.body;
        let data;
        if (Buffer.isBuffer(body)) {
            data = body;
        } else if (typeof body === 'string' && body.length > 0) {
            data = Buffer.from(body, 'base64');
        } else {
            data = Buffer.from(String(body || ''));
        }
        fs.writeFileSync(filepath, data);
        res.status(200).json({ success: true, filename });
    } catch (e) {
        console.error('Upload error:', e);
        res.status(500).json({ error: e.message });
    }
};
