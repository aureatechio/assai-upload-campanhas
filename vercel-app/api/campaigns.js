export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Admin-Password');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const serviceRole = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_ROLE || '';

  if (!supabaseUrl || !serviceRole) {
    return res.status(400).json({ error: 'Supabase nao configurado.' });
  }

  const restBase = `${supabaseUrl}/rest/v1/campaign_uploads`;
  const headers = {
    'apikey': serviceRole,
    'Authorization': `Bearer ${serviceRole}`,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
  };

  // GET — list campaigns, optionally filtered by status
  if (req.method === 'GET') {
    const { status } = req.query || {};
    let url = restBase + '?order=created_at.desc';
    if (status) url += `&status=eq.${encodeURIComponent(status)}`;

    try {
      const r = await fetch(url, { headers });
      const data = await r.json();
      if (!r.ok) return res.status(r.status).json({ error: data });
      return res.json(data);
    } catch (err) {
      return res.status(500).json({ error: err.message });
    }
  }

  // POST — save campaign payloads (batch insert)
  if (req.method === 'POST') {
    const { records } = req.body || {};
    if (!records || !Array.isArray(records) || records.length === 0) {
      return res.status(400).json({ error: 'records (array) obrigatorio.' });
    }

    try {
      const r = await fetch(restBase, {
        method: 'POST',
        headers,
        body: JSON.stringify(records),
      });
      const data = await r.json();
      if (!r.ok) return res.status(r.status).json({ error: data });
      return res.json({ success: true, inserted: data.length });
    } catch (err) {
      return res.status(500).json({ error: err.message });
    }
  }

  // PATCH — update status
  // user_approved: user can set (pending → user_approved), no admin password needed
  // published/rejected: admin only (user_approved → published/rejected)
  if (req.method === 'PATCH') {
    const { campaign_slug, status: newStatus, record_ids } = req.body || {};
    if (!newStatus) {
      return res.status(400).json({ error: 'status obrigatorio.' });
    }
    if (!campaign_slug && (!record_ids || !Array.isArray(record_ids) || record_ids.length === 0)) {
      return res.status(400).json({ error: 'campaign_slug ou record_ids obrigatorio.' });
    }

    const allowed = ['user_approved', 'published', 'rejected', 'pending'];
    if (!allowed.includes(newStatus)) {
      return res.status(400).json({ error: `Status invalido. Use: ${allowed.join(', ')}` });
    }

    // Admin password required for published/rejected transitions
    if (newStatus === 'published' || newStatus === 'rejected') {
      const adminPassword = process.env.ADMIN_PASSWORD || '';
      const provided = req.headers['x-admin-password'] || '';
      if (!adminPassword || provided !== adminPassword) {
        return res.status(403).json({ error: 'Senha de admin invalida.' });
      }
    }

    // Determine which source status to filter
    let fromStatus;
    if (newStatus === 'user_approved') fromStatus = 'pending';
    else if (newStatus === 'published' || newStatus === 'rejected') fromStatus = 'user_approved';
    else if (newStatus === 'pending') fromStatus = 'user_approved'; // user can revert to re-test

    const updateBody = { status: newStatus };
    if (newStatus === 'user_approved') {
      updateBody.user_approved_at = new Date().toISOString();
    }
    if (newStatus === 'published') {
      updateBody.approved_at = new Date().toISOString();
    }

    let url;
    if (record_ids && Array.isArray(record_ids) && record_ids.length > 0) {
      const ids = record_ids.map(id => encodeURIComponent(id)).join(',');
      url = `${restBase}?id=in.(${ids})&status=eq.${fromStatus}`;
    } else {
      url = `${restBase}?campaign_slug=eq.${encodeURIComponent(campaign_slug)}&status=eq.${fromStatus}`;
    }

    try {
      const r = await fetch(url, {
        method: 'PATCH',
        headers,
        body: JSON.stringify(updateBody),
      });
      const data = await r.json();
      if (!r.ok) return res.status(r.status).json({ error: data });
      return res.json({ success: true, updated: data.length });
    } catch (err) {
      return res.status(500).json({ error: err.message });
    }
  }

  // DELETE — remove campaign records
  // Admin can delete any status; non-admin can only delete pending (for re-upload)
  if (req.method === 'DELETE') {
    const { campaign_slug, status_filter } = req.body || {};
    if (!campaign_slug) {
      return res.status(400).json({ error: 'campaign_slug obrigatorio.' });
    }

    const adminPassword = process.env.ADMIN_PASSWORD || '';
    const provided = req.headers['x-admin-password'] || '';
    const isAdmin = adminPassword && provided === adminPassword;

    // Non-admin can only delete pending records
    const filterStatus = isAdmin ? (status_filter || null) : 'pending';

    let url = `${restBase}?campaign_slug=eq.${encodeURIComponent(campaign_slug)}`;
    if (filterStatus) {
      url += `&status=eq.${encodeURIComponent(filterStatus)}`;
    }

    try {
      const r = await fetch(url, {
        method: 'DELETE',
        headers,
      });
      if (!r.ok) {
        const data = await r.json();
        return res.status(r.status).json({ error: data });
      }
      return res.json({ success: true });
    } catch (err) {
      return res.status(500).json({ error: err.message });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
