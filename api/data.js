const path = require('path');
const fs = require('fs');
const os = require('os');

const DATA_DIR = path.join(os.tmpdir(), 'data');

function getClientIP(req) {
    return req.headers['x-forwarded-for']?.split(',')[0] ||
           req.headers['x-real-ip'] ||
           (req.socket && req.socket.remoteAddress) ||
           (req.connection && req.connection.remoteAddress) ||
           'unknown';
}

module.exports = async function handler(req, res) {
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    const sessionFile = path.join(DATA_DIR, 'session_' + clientIP.replace(/[^a-zA-Z0-9]/g, '_') + '.txt');
    
    if (!token || !fs.existsSync(sessionFile)) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    const storedToken = fs.readFileSync(sessionFile, 'utf8').trim();
    if (storedToken !== token) {
        return res.status(401).json({ error: 'Invalid token' });
    }
    
    const files = fs.readdirSync(DATA_DIR)
        .filter(f => f.endsWith('.zip'))
        .sort()
        .reverse()
        .map(file => {
            const stats = fs.statSync(path.join(DATA_DIR, file));
            return {
                filename: file,
                size: stats.size,
                date: stats.birthtime,
                ip: file.split('_')[1].replace('.zip', '')
            };
        });
    
    res.status(200).json({ files });
};
