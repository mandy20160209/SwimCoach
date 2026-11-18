let cached = null;

function keyError(message, fix) {
  const error = new Error(message);
  error.fix = fix;
  return error;
}

export async function getKey(forceRefresh = false) {
  if (!forceRefresh && cached && cached.expiresAt > Date.now() + 5000) return cached.apiKey;
  const url = process.env.KEYGEN_URL;
  const token = process.env.KEYGEN_TOKEN;
  if (!url || !token || url === 'paste-here' || token === 'paste-here') {
    throw keyError('The AI key service is not configured.', 'Add KEYGEN_URL and KEYGEN_TOKEN to the server environment.');
  }
  let response;
  try {
    response = await fetch(url.replace(/\/$/, '') + '/api/lookup-key', { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
  } catch {
    throw keyError('The AI key service could not be reached.', 'Check KEYGEN_URL and the server internet connection.');
  }
  let data = {};
  try { data = await response.json(); } catch { /* handled below */ }
  if (!response.ok || typeof data.apiKey !== 'string' || !data.apiKey || !data.expiresAt) {
    throw keyError('The AI key service did not return a usable key.', 'Check the MindDo URL, token, and key service response.');
  }
  const expiresAt = new Date(data.expiresAt).getTime();
  if (!Number.isFinite(expiresAt) || expiresAt <= Date.now()) {
    throw keyError('The AI key service returned an expired key.', 'Check the MindDo key expiration and try again.');
  }
  cached = { apiKey: data.apiKey, expiresAt };
  return cached.apiKey;
}

export function clearKey() { cached = null; }
