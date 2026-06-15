"""Lokalny serwer testowy dla builda pygbag (assets w build/web).
Ustawia nagłówki cross-origin isolation oraz poprawny mimetype dla .wasm.
Uruchom: python serve_web.py [port]
"""
import http.server
import os
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
DIRECTORY = "build/web"


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".wasm": "application/wasm",
        ".js": "application/javascript",
        ".apk": "application/octet-stream",
    }

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIRECTORY, **kw)

    def end_headers(self):
        # COISO=1 włącza cross-origin isolation (potrzebne tylko jeśli runtime
        # używa SharedArrayBuffer/wątków). Przy self-hostingu (wszystko
        # same-origin) zwykle NIE jest potrzebne - testujemy oba warianty.
        if os.environ.get("COISO") == "1":
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


with Server(("0.0.0.0", PORT), Handler) as httpd:
    print(f"serving build/web at http://127.0.0.1:{PORT}/  (Ctrl-C to stop)")
    httpd.serve_forever()
