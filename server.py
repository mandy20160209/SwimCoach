#!/usr/bin/env python3
import json, os, pathlib, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = pathlib.Path(__file__).parent
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-6-luna')

def load_env():
    path = ROOT / '.env'
    if not path.exists(): return {}
    values = {}
    for line in path.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1); values[key.strip()] = value.strip().strip('"').strip("'")
    return values

def extract_text(payload):
    if isinstance(payload.get('output_text'), str): return payload['output_text']
    parts = []
    for item in payload.get('output', []):
        for content in item.get('content', []):
            if content.get('type') == 'output_text': parts.append(content.get('text', ''))
    return '\n'.join(parts).strip()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): return
    def send_json(self, code, body):
        data = json.dumps(body).encode('utf-8'); self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path == '/health': self.send_json(200, {'ok': True}); return
        requested = self.path.split('?', 1)[0]
        if requested == '/': requested = '/index.html'
        file_path = (ROOT / requested.lstrip('/')).resolve()
        if ROOT not in file_path.parents or not file_path.is_file() or file_path.name == '.env': self.send_error(404); return
        types = {'html':'text/html; charset=utf-8','css':'text/css; charset=utf-8','js':'application/javascript; charset=utf-8'}
        data = file_path.read_bytes(); self.send_response(200); self.send_header('Content-Type', types.get(file_path.suffix.lstrip('.'), 'text/plain; charset=utf-8')); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        if self.path != '/api/coach': self.send_json(404, {'error':'That page is not part of SwimCoach.'}); return
        try:
            length = int(self.headers.get('Content-Length', '0')); body = json.loads(self.rfile.read(length).decode('utf-8')); question = str(body.get('question', '')).strip()
            if not question: self.send_json(400, {'error':'Please ask a swimming question.'}); return
            api_key = load_env().get('OPENAI_API_KEY', '')
            if not api_key or api_key == 'paste-your-key-here': self.send_json(503, {'error':'I cannot answer yet. Please check the OpenAI key in your local .env file.'}); return
            context = {'level': body.get('level', 'not chosen'), 'reflections': body.get('reflections', [])}
            request_body = {'model': MODEL, 'instructions': (ROOT/'BRIEF.md').read_text(encoding='utf-8'), 'input': [{'role':'user','content':'Swimmer context: '+json.dumps(context)+'\n\nQuestion: '+question}], 'max_output_tokens':500}
            request = urllib.request.Request('https://api.openai.com/v1/responses', data=json.dumps(request_body).encode('utf-8'), headers={'Authorization':'Bearer '+api_key,'Content-Type':'application/json'}, method='POST')
            with urllib.request.urlopen(request, timeout=45) as response: answer = extract_text(json.loads(response.read().decode('utf-8')))
            self.send_json(200, {'answer': answer or 'I could not find an answer. Please try a shorter question or ask your coach.'})
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError): self.send_json(502, {'error':'I cannot answer right now. Please check the OpenAI key and internet connection.'})
        except Exception: self.send_json(500, {'error':'Something went wrong. Please try again or ask a coach.'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000')); print('SwimCoach running at http://localhost:%d' % port); ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
