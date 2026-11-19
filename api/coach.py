import json
import os
import pathlib
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler
from keygen import KeygenError, clear_key, get_key

ROOT = pathlib.Path(__file__).parent.parent
MODEL = os.environ.get('OPENAI_MODEL', 'gpt-5.6-luna')


def extract_text(payload):
    if isinstance(payload.get('output_text'), str):
        return payload['output_text']
    parts = []
    for item in payload.get('output', []):
        for content in item.get('content', []):
            if content.get('type') == 'output_text':
                parts.append(content.get('text', ''))
    return '\n'.join(parts).strip()


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        return

    def send_json(self, code, body):
        data = json.dumps(body).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.send_json(200, {'ok': True, 'service': 'SwimCoach AI'})

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            question = str(body.get('question', '')).strip()
            if not question:
                self.send_json(400, {'error': 'Please ask a swimming question.'})
                return

            try:
                api_key = get_key()
            except KeygenError as error:
                self.send_json(503, {'error': {'message': error.message, 'fix': error.fix}})
                return

            context = {'level': body.get('level', 'not chosen'), 'posture_description': body.get('postureDescription', '')}
            instructions = (ROOT / 'BRIEF.md').read_text(encoding='utf-8')
            request_body = {
                'model': MODEL,
                'instructions': instructions,
                'input': [{'role': 'user', 'content': 'Swimmer context: ' + json.dumps(context) + '\n\nQuestion: ' + question}],
                'max_output_tokens': 500,
            }
            def ask(key):
                request = urllib.request.Request('https://api.openai.com/v1/responses', data=json.dumps(request_body).encode('utf-8'), headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(request, timeout=45) as response: return extract_text(json.loads(response.read().decode('utf-8')))
            try:
                answer = ask(api_key)
            except urllib.error.HTTPError as error:
                if error.code != 401: raise
                clear_key()
                try: answer = ask(get_key(force_refresh=True))
                except KeygenError as key_error:
                    self.send_json(503, {'error': {'message': key_error.message, 'fix': key_error.fix}})
                    return
            self.send_json(200, {'answer': answer or 'I could not find an answer. Please try a shorter question or ask your coach.'})
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError):
            self.send_json(502, {'error': {'message': 'I cannot answer right now.', 'fix': 'Check the MindDo key service and internet connection.'}})
        except Exception:
            self.send_json(500, {'error': 'Something went wrong. Please try again or ask a coach.'})
