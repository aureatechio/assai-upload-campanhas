export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const serviceRole = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_ROLE || '';
  if (!serviceRole) {
    return res.status(400).json({ error: 'SUPABASE_SERVICE_ROLE_KEY nao configurado.' });
  }

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const bucket = process.env.NEXT_PUBLIC_SUPABASE_BUCKET || process.env.SUPABASE_BUCKET || '';

  if (!supabaseUrl || !bucket) {
    return res.status(400).json({ error: 'SUPABASE_URL ou BUCKET nao configurado.' });
  }

  const { objectPath, contentType, method } = req.body || {};

  if (!objectPath) {
    return res.status(400).json({ error: 'objectPath obrigatorio.' });
  }

  // Proxy the upload to Supabase using the service role key
  // Return signed upload URL info
  const encodedPath = objectPath.split('/').map(encodeURIComponent).join('/');
  const uploadMethod = method || 'POST';
  const url = `${supabaseUrl}/storage/v1/object/${bucket}/${encodedPath}`;

  return res.json({
    url,
    headers: {
      'Authorization': `Bearer ${serviceRole}`,
      'apikey': serviceRole,
      'Content-Type': contentType || 'application/octet-stream',
      'x-upsert': 'true',
      'cache-control': '3600',
    },
    method: uploadMethod,
    publicUrl: `${supabaseUrl}/storage/v1/object/public/${bucket}/${encodedPath}`,
  });
}
