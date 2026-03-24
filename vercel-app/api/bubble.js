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

  const { table, payload, env, action, bubble_id, constraints } = req.body || {};

  if (!table) {
    return res.status(400).json({ error: 'table obrigatorio.' });
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
  let tableUrl;
  if (env === 'prod') {
    tableUrl = baseUrl.replace('/version-test/', '/') + '/' + encodeURIComponent(table);
  } else {
    tableUrl = baseUrl + '/' + encodeURIComponent(table);
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  try {
    // SEARCH: find existing records by constraints
    if (action === 'search') {
      if (!constraints || !Array.isArray(constraints)) {
        return res.status(400).json({ error: 'constraints (array) obrigatorio para search.' });
      }
      const params = new URLSearchParams({
        constraints: JSON.stringify(constraints),
      });
      const searchUrl = `${tableUrl}?${params.toString()}`;

      const response = await fetch(searchUrl, { method: 'GET', headers });
      const text = await response.text();
      if (!response.ok) {
        return res.status(response.status).json({ error: `Bubble HTTP ${response.status}: ${text}` });
      }
      let data;
      try { data = JSON.parse(text); } catch { data = { raw: text }; }
      return res.json({ success: true, data });
    }

    // UPDATE: patch existing record by bubble_id
    if (action === 'update') {
      if (!bubble_id || !payload) {
        return res.status(400).json({ error: 'bubble_id e payload obrigatorios para update.' });
      }
      const patchUrl = `${tableUrl}/${encodeURIComponent(bubble_id)}`;
      const response = await fetch(patchUrl, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(payload),
      });

      if (response.status === 204) {
        return res.json({ success: true, data: { id: bubble_id } });
      }

      const text = await response.text();
      if (!response.ok) {
        return res.status(response.status).json({ error: `Bubble HTTP ${response.status}: ${text}` });
      }
      let data;
      try { data = JSON.parse(text); } catch { data = { raw: text }; }
      return res.json({ success: true, data });
    }

    // CREATE (default): post new record
    if (!payload) {
      return res.status(400).json({ error: 'payload obrigatorio.' });
    }

    const response = await fetch(tableUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });

    const text = await response.text();
    if (!response.ok) {
      return res.status(response.status).json({ error: `Bubble HTTP ${response.status}: ${text}` });
    }

    let data;
    try { data = JSON.parse(text); } catch { data = { raw: text }; }
    return res.json({ success: true, data });
  } catch (err) {
    return res.status(500).json({ error: `Erro ao enviar para Bubble: ${err.message}` });
  }
}
