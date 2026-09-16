const fs = require('fs');
const path = require('path');

const DATA_DIR = path.join(process.cwd(), 'data');

module.exports = async (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Not authenticated' });
    }
    
    const url = req.url;
    const filename = url.replace('/api/data/', '');
    const filepath = path.join(DATA_DIR, filename);
    
    if (!fs.existsSync(filepath)) {
        return res.status(404).json({ error: 'File not found' });
    }
    
    try {
        const zipContent = fs.readFileSync(filepath);
        const zipText = Buffer.from(zipContent).toString('utf8');
        
        const jsonMatch = zipText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const data = JSON.parse(jsonMatch[0]);
            res.status(200).json({ data });
        } else {
            res.status(200).json({ raw: zipText });
        }
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
};
