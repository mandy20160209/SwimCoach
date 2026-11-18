import datetime
import json
import os
import time
import urllib.error
import urllib.request

_cached = None


class KeygenError(Exception):
    def __init__(self, message, fix):
        super().__init__(message)
        self.message = message
        self.fix = fix


def clear_key():
    global _cached
    _cached = None


def get_key(force_refresh=False):
    global _cached
    if not force_refresh and _cached and _cached['expires_at'] > time.time() + 5:
        return _cached['api_key']
    url = os.environ.get('KEYGEN_URL', '')
    token = os.environ.get('KEYGEN_TOKEN', '')
    if not url or not token or url == 'paste-here' or token == 'paste-here':
        raise KeygenError('The AI key service is not configured.', 'Add KEYGEN_URL and KEYGEN_TOKEN to the server environment.')
    request = urllib.request.Request(url.rstrip('/') + '/api/lookup-key', data=b'', headers={'Authorization': 'Bearer ' + token}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode('utf-8'))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
        raise KeygenError('The AI key service could not be reached.', 'Check KEYGEN_URL, KEYGEN_TOKEN, and the server internet connection.')
    api_key = data.get('apiKey') if isinstance(data, dict) else None
    expires_at = data.get('expiresAt') if isinstance(data, dict) else None
    if not isinstance(api_key, str) or not api_key or not expires_at:
        raise KeygenError('The AI key service did not return a usable key.', 'Check the MindDo URL, token, and key service response.')
    try:
        expires_epoch = float(expires_at) if isinstance(expires_at, (int, float)) else datetime.datetime.fromisoformat(str(expires_at).replace('Z', '+00:00')).timestamp()
    except (TypeError, ValueError, OverflowError):
        raise KeygenError('The AI key service returned an invalid expiration.', 'Ask MindDo for an expiresAt timestamp in ISO format.')
    if expires_epoch <= time.time():
        raise KeygenError('The AI key service returned an expired key.', 'Check the MindDo key expiration and try again.')
    _cached = {'api_key': api_key, 'expires_at': expires_epoch}
    return api_key
