const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');

function getClientIP(req) {
    return req.headers['x-forwarded-for']?.split(',')[0] || 
           req.headers['x-real-ip'] || 
           req.socket?.remoteAddress ||
           req.ip;
}

module.exports = async (req, res) => {
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    const sessionFile = path.join(DATA_DIR, `session_${clientIP.replace(/\./g, '_')}.txt`);
    
    if (token && fs.existsSync(sessionFile)) {
        const storedToken = fs.readFileSync(sessionFile, 'utf8').trim();
        if (storedToken === token) {
            return res.status(200).json({ authenticated: true });
        }
    }
    
    res.status(401).json({ authenticated: false });
};
