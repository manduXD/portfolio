const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');

module.exports = async (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    try {
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
    } catch (e) {
        res.status(200).json({ files: [] });
    }
};
