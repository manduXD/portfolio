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

module.exports = async (req, res) => {
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
