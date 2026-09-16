module.exports = async (req, res) => {
    const authHeader = req.headers.authorization;
    const token = authHeader?.split(' ')[1];
    
    if (token) {
        return res.status(200).json({ authenticated: true });
    }
    
    res.status(401).json({ authenticated: false });
};
