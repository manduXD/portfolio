const path = require('path');
const fs = require('fs');

const DATA_DIR = path.join('/tmp', 'data');

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
        const safeIP = String(clientIP).replace(/[^a-zA-Z0-9]/g, '_');
        const filename = timestamp + '_' + safeIP + '.zip';
        const filepath = path.join(DATA_DIR, filename);

        console.error('Request body type:', typeof req.body, 'isBuffer:', Buffer.isBuffer(req.body), 'content-type:', req.headers['content-type']);
        const body = req.body;
        let data;
        if (Buffer.isBuffer(body)) {
            data = body;
        } else if (typeof body === 'string') {
            data = Buffer.from(body);
        } else if (body && body.data && Buffer.isBuffer(body.data)) {
            data = body.data;
        } else if (body && typeof body === 'object') {
            data = Buffer.from(JSON.stringify(body));
        } else {
            data = Buffer.from('');
        }

        fs.writeFileSync(filepath, data);
        res.status(200).json({ success: true, filename });
    } catch (e) {
        console.error('Upload error:', e.message, e.stack);
        res.status(500).json({ error: e.message });
    }
};

module.exports.config = { api: { bodyParser: false } };
