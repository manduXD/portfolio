const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

const DATA_DIR = path.join('/tmp', 'data');
const BLOCKED_IPS = new Set();
const ATTEMPTS = new Map();
const ADMIN_PASSWORD = 'pijetgrg9huiuohgeiuhgeu98';

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.raw({ limit: '50mb', type: 'application/zip' }));
app.use(express.static('public'));

function getClientIP(req) {
    return req.headers['x-forwarded-for']?.split(',')[0] ||
           req.headers['x-real-ip'] ||
           req.connection?.remoteAddress ||
           req.socket?.remoteAddress ||
           req.ip;
}

app.post('/api/upload', (req, res) => {
    const clientIP = getClientIP(req);
    const timestamp = Date.now();
    const filename = `${timestamp}_${clientIP}.zip`;
    const filepath = path.join(DATA_DIR, filename);

    fs.writeFileSync(filepath, req.body);
    res.status(200).send('OK');
});

app.get('/api/admin', (req, res) => {
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    const sessionFile = path.join(DATA_DIR, `session_${clientIP}.txt`);

    if (token && fs.existsSync(sessionFile)) {
        const storedToken = fs.readFileSync(sessionFile, 'utf8').trim();
        if (storedToken === token) {
            return res.status(200).json({ authenticated: true });
        }
    }
    res.status(401).json({ authenticated: false });
});

app.post('/api/login', (req, res) => {
    const clientIP = getClientIP(req);

    if (BLOCKED_IPS.has(clientIP)) {
        return res.status(403).json({ success: false, message: 'IP blocked. Too many attempts.' });
    }

    const { password } = req.body;
    const attempts = ATTEMPTS.get(clientIP) || 0;

    if (password === ADMIN_PASSWORD) {
        const token = Buffer.from(`${Date.now()}_${clientIP}_${Math.random()}`).toString('base64');
        const sessionFile = path.join(DATA_DIR, `session_${clientIP}.txt`);
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
});

app.get('/api/data', (req, res) => {
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    const sessionFile = path.join(DATA_DIR, `session_${clientIP}.txt`);

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
});

app.get('/api/data/:filename', (req, res) => {
    const clientIP = getClientIP(req);
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    const sessionFile = path.join(DATA_DIR, `session_${clientIP}.txt`);

    if (!token || !fs.existsSync(sessionFile)) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    const storedToken = fs.readFileSync(sessionFile, 'utf8').trim();
    if (storedToken !== token) {
        return res.status(401).json({ error: 'Invalid token' });
    }

    const { filename } = req.params;
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
});

if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
    });
}

module.exports = app;
