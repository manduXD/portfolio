const path = require('path');
const fs = require('fs');
const os = require('os');

const DATA_DIR = path.join(os.tmpdir(), 'data');
const ADMIN_PASSWORD = 'pijetgrg9huiuohgeiuhgeu98';
const BLOCKED_IPS = new Set();
const ATTEMPTS = new Map();

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
    const clientIP = getClientIP(req);
    const body = req.body;
    const password = typeof body === 'string' ? body : JSON.stringify(body);
    const parsed = JSON.parse(password);
    const { password: pwd } = parsed || {};
    const attempts = ATTEMPTS.get(clientIP) || 0;
    
    if (BLOCKED_IPS.has(clientIP)) {
        return res.status(403).json({ success: false, message: 'IP blocked.' });
    }
    
    if (pwd === ADMIN_PASSWORD) {
        const token = Buffer.from(Date.now() + '_' + clientIP + '_' + Math.random()).toString('base64');
        const sessionFile = path.join(DATA_DIR, 'session_' + clientIP.replace(/[^a-zA-Z0-9]/g, '_') + '.txt');
        fs.writeFileSync(sessionFile, token);
        ATTEMPTS.delete(clientIP);
        res.status(200).json({ success: true, token });
    } else {
        ATTEMPTS.set(clientIP, attempts + 1);
        if (ATTEMPTS.get(clientIP) >= 2) {
            BLOCKED_IPS.add(clientIP);
            res.status(403).json({ success: false, message: 'IP blocked.' });
        } else {
            res.status(401).json({ success: false, message: 'Invalid password' });
        }
    }
};
