import json
import os
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body) if body else {}

        role = data.get('role', '')
        password = data.get('password', '')

        if role == 'user':
            expected = os.environ.get('USER_PASSWORD', '')
            if not expected:
                self._respond(200, {'authorized': False, 'message': 'USER_PASSWORD nao configurado no servidor.'})
                return
            if password == expected:
                self._respond(200, {'authorized': True, 'role': 'user'})
            else:
                self._respond(200, {'authorized': False, 'message': 'Senha incorreta.'})

        elif role == 'admin':
            expected = os.environ.get('ADMIN_PASSWORD', '')
            if not expected:
                self._respond(200, {'authorized': False, 'message': 'ADMIN_PASSWORD nao configurado no servidor.'})
                return
            if password == expected:
                self._respond(200, {'authorized': True, 'role': 'admin'})
            else:
                self._respond(200, {'authorized': False, 'message': 'Senha incorreta.'})

        else:
            self._respond(200, {'authorized': False, 'message': 'Role invalido.'})

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
