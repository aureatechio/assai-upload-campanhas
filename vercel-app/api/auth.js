export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { role, password } = req.body || {};

  if (role === 'user') {
    const expected = process.env.USER_PASSWORD || '';
    if (!expected) return res.json({ authorized: false, message: 'USER_PASSWORD nao configurado no servidor.' });
    if (password === expected) return res.json({ authorized: true, role: 'user' });
    return res.json({ authorized: false, message: 'Senha incorreta.' });
  }

  if (role === 'admin') {
    const expected = process.env.ADMIN_PASSWORD || '';
    if (!expected) return res.json({ authorized: false, message: 'ADMIN_PASSWORD nao configurado no servidor.' });
    if (password === expected) return res.json({ authorized: true, role: 'admin' });
    return res.json({ authorized: false, message: 'Senha incorreta.' });
  }

  return res.json({ authorized: false, message: 'Role invalido.' });
}
