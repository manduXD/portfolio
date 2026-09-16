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
    
    const filename = req.query.filename || req.path.split('/').pop();
    const filepath = path.join(DATA_DIR, filename);
    
    if (!fs.existsSync(filepath)) {
        return res.status(404).json({ error: 'File not found' });
    }
    
    const zipContent = fs.readFileSync(filepath);
    const zipText = Buffer.from(zipContent).toString('utf8');
    
    try {
        const jsonMatch = zipText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const data = JSON.parse(jsonMatch[0]);
            res.status(200).json({ data });
        }
    } catch (e) {
        res.status(200).json({ raw: zipText });
    }
};
