import http.server, os, sys, urllib.parse
ROOT = os.path.dirname(os.path.abspath(__file__))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        n = int(self.headers['Content-Length'])
        name = os.path.basename(q['name'][0])
        os.makedirs(os.path.join(ROOT, 'frames'), exist_ok=True)
        with open(os.path.join(ROOT, 'frames', name), 'wb') as f: f.write(self.rfile.read(n))
        self.send_response(204); self.end_headers()
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
