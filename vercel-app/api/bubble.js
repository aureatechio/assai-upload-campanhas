export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Password');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const token = process.env.BUBBLE_API_TOKEN || '';
  if (!token) {
    return res.status(400).json({ error: 'BUBBLE_API_TOKEN nao configurado.' });
  }

  const { table, payload, env } = req.body || {};

  if (!table || !payload) {
    return res.status(400).json({ error: 'table e payload obrigatorios.' });
  }

  // Protect PROD uploads
  if (env === 'prod') {
    const adminPassword = process.env.ADMIN_PASSWORD || '';
    const provided = req.headers['x-admin-password'] || '';
    if (!adminPassword || provided !== adminPassword) {
      return res.status(403).json({ error: 'Acesso negado. Senha de admin invalida para Bubble PROD.' });
    }
  }

  // Build Bubble API URL
  const baseUrl = process.env.BUBBLE_BASE_URL || 'https://assai.geofast.ai/version-test/api/1.1/obj';
  let url;
  if (env === 'prod') {
    url = baseUrl.replace('/version-test/', '/') + '/' + encodeURIComponent(table);
  } else {
    url = baseUrl + '/' + encodeURIComponent(table);
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const text = await response.text();

    if (!response.ok) {
      return res.status(response.status).json({
        error: `Bubble HTTP ${response.status}: ${text}`,
      });
    }

    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }

    return res.json({ success: true, data });
  } catch (err) {
    return res.status(500).json({ error: `Erro ao enviar para Bubble: ${err.message}` });
  }
}
