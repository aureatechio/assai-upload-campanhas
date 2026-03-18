export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const supabaseBucket = process.env.NEXT_PUBLIC_SUPABASE_BUCKET || process.env.SUPABASE_BUCKET || '';
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
  const bubbleConfigured = !!process.env.BUBBLE_API_TOKEN;
  const bubbleBaseUrl = process.env.BUBBLE_BASE_URL || '';
  const ajusteCampanhaId = process.env.AJUSTE_CAMPANHA_ID || '';

  return res.json({
    supabase: {
      url: supabaseUrl,
      bucket: supabaseBucket,
      anonKey: supabaseAnonKey,
      configured: !!(supabaseUrl && supabaseBucket),
    },
    bubble: {
      configured: bubbleConfigured,
      baseUrl: bubbleBaseUrl,
      ajusteCampanhaId,
    },
  });
}
