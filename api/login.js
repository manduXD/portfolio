const ADMIN_PASSWORD = 'pijetgrg9huiuohgeiuhgeu98';

module.exports = async (req, res) => {
    let password = '';
    
    try {
        if (req.body && typeof req.body === 'string') {
            const parsed = JSON.parse(req.body);
            password = parsed.password || '';
        } else if (req.body && req.body.password) {
            password = req.body.password;
        }
    } catch (e) {
        return res.status(400).json({ success: false, message: 'Invalid JSON' });
    }
    
    if (!password) {
        return res.status(400).json({ success: false, message: 'Password required' });
    }
    
    if (password === ADMIN_PASSWORD) {
        const token = Buffer.from(`${Date.now()}_${Math.random()}`).toString('base64');
        res.status(200).json({ success: true, token });
    } else {
        res.status(401).json({ success: false, message: 'Invalid password' });
    }
};
