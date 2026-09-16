const ADMIN_PASSWORD = 'pijetgrg9huiuohgeiuhgeu98';

module.exports = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).json({ success: false, message: 'Method not allowed' });
    }
    
    let data = {};
    try {
        data = JSON.parse(req.body);
    } catch (e) {
        return res.status(400).json({ success: false, message: 'Invalid JSON' });
    }
    
    const { password } = data;
    
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
