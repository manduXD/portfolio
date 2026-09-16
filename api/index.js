const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

function getClientIP(req) {
    return req.headers['x-forwarded-for']?.split(',')[0] || 
           req.headers['x-real-ip'] || 
           req.socket?.remoteAddress ||
           req.ip;
}

exports.upload = async (req, res) => {
    const clientIP = getClientIP(req);
    const timestamp = Date.now();
    const filename = `${timestamp}_${clientIP}.zip`;
    const filepath = path.join(DATA_DIR, filename);
    
    const chunks = [];
    for await (const chunk of req) {
        chunks.push(chunk);
    }
    
    fs.writeFileSync(filepath, Buffer.concat(chunks));
    
    res.status(200).send('OK');
};

exports.admin = async (req, res) => {
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

exports.login = async (req, res) => {
    const BLOCKED_IPS = new Set();
    const ATTEMPTS = new Map();
    const ADMIN_PASSWORD = 'pijetgrg9huiuohgeiuhgeu98';
    
    const clientIP = getClientIP(req);
    
    if (BLOCKED_IPS.has(clientIP)) {
        return res.status(403).json({ success: false, message: 'IP blocked. Too many attempts.' });
    }
    
    const body = await Buffer.from(req).toString('utf8');
    let data = {};
    try {
        data = JSON.parse(body);
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

exports.data = async (req, res) => {
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    const sessionFile = path.join(DATA_DIR, `session_${clientIP.replace(/\./g, '_')}.txt`);
    
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
            const ipMatch = file.match(/_(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\.zip$/);
            return {
                filename: file,
                size: stats.size,
                date: stats.birthtime,
                ip: ipMatch ? ipMatch[1] : 'unknown'
            };
        });
    
    res.status(200).json({ files });
};

exports.dataFile = async (req, res) => {
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    const sessionFile = path.join(DATA_DIR, `session_${clientIP.replace(/\./g, '_')}.txt`);
    
    if (!token || !fs.existsSync(sessionFile)) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const storedToken = fs.readFileSync(sessionFile, 'utf8').trim();
    if (storedToken !== token) {
        return res.status(401).json({ error: 'Invalid token' });
    }
    
    const url = req.url;
    const filename = url.replace('/api/data/', '');
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
