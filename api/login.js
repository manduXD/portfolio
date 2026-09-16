const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');
const BLOCKED_IPS = new Map();
const ATTEMPTS = new Map();
const ADMIN_PASSWORD = 'pijetgrg9huiuohgeiuhgeu98';

function getClientIP(req) {
    return req.headers['x-forwarded-for']?.split(',')[0] || 
           req.headers['x-real-ip'] || 
           req.socket?.remoteAddress ||
           req.ip;
}

module.exports = async (req, res) => {
    const clientIP = getClientIP(req);
    
    if (BLOCKED_IPS.has(clientIP)) {
        return res.status(403).json({ success: false, message: 'IP blocked. Too many attempts.' });
    }
    
    let data = {};
    try {
        data = JSON.parse(req.body);
    } catch (e) {}
    
    const { password } = data;
    const attempts = ATTEMPTS.get(clientIP) || 0;
    
    if (password === ADMIN_PASSWORD) {
        const token = Buffer.from(`${Date.now()}_${clientIP}_${Math.random()}`).toString('base64');
        const sessionFile = path.join(DATA_DIR, `session_${clientIP.replace(/\./g, '_')}.txt`);
        fs.writeFileSync(sessionFile, token);
        
        ATTEMPTS.delete(clientIP);
        res.status(200).json({ success: true, token });
    } else {
        ATTEMPTS.set(clientIP, attempts + 1);
        
        if (ATTEMPTS.get(clientIP) >= 2) {
            BLOCKED_IPS.add(clientIP);
            res.status(403).json({ success: false, message: 'IP blocked. Too many attempts.' });
        } else {
            res.status(401).json({ success: false, message: 'Invalid password' });
        }
    }
};
