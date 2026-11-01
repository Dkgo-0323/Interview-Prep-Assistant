"""Exercise the shipped nginx template locally; no application or secrets loaded.

Linux CI only. All upstream traffic is synthetic and bound to ephemeral loopback
ports. The temporary certificate is trusted only by this test client.
"""
from __future__ import annotations

from collections import Counter
from contextlib import closing
from http.client import HTTPSConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import threading
import time


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    calls: Counter[str] = Counter()
    release = threading.Event()
    finished = threading.Event()

    class Upstream(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            calls[self.path] += 1
            if self.path == "/api/fail":
                self.connection.shutdown(socket.SHUT_RDWR)
                self.connection.close()
                return
            if self.path == "/api/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                self.wfile.write(b"data: first\n\n")
                self.wfile.flush()
                if release.wait(8):
                    self.wfile.write(b"data: second\n\n")
                    self.wfile.flush()
                finished.set()
                return
            if self.path == "/api/cookie":
                body = self.headers.get("Cookie", "").encode()
                self.send_response(200)
                self.send_header("Set-Cookie", "ipa_test=synthetic; Path=/; HttpOnly; Secure; SameSite=Lax")
            else:
                body = f"{self.path}|{self.headers.get('X-Forwarded-Proto')}|{self.headers.get('Host')}".encode()
                self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    api = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
    web = ThreadingHTTPServer(("127.0.0.1", 0), Upstream)
    threads = [threading.Thread(target=s.serve_forever, daemon=True) for s in (api, web)]
    for thread in threads:
        thread.start()
    process = None
    try:
        with tempfile.TemporaryDirectory(prefix="ipa-proxy-") as directory:
            work = Path(directory)
            cert, key = work / "cert.pem", work / "key.pem"
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-subj", "/CN=localhost", "-addext", "subjectAltName=IP:127.0.0.1", "-keyout", str(key), "-out", str(cert)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            template = (ROOT / "deploy/single-vm/nginx.conf").read_text()
            replacements = {
                "listen 443 ssl;": f"listen 127.0.0.1:{port} ssl;",
                "/etc/interview-prep/tls/fullchain.pem": str(cert),
                "/etc/interview-prep/tls/privkey.pem": str(key),
                "http://127.0.0.1:8000": f"http://127.0.0.1:{api.server_port}",
                "http://127.0.0.1:3000": f"http://127.0.0.1:{web.server_port}",
            }
            for old, new in replacements.items():
                assert old in template, f"template substitution missing: {old}"
                template = template.replace(old, new)
            config = work / "nginx.conf"
            config.write_text(f"pid {work}/nginx.pid;\nerror_log stderr;\nevents {{}}\nhttp {{\n{template}\n}}\n")
            process = subprocess.Popen(["nginx", "-p", f"{work}/", "-c", str(config), "-g", "daemon off;"], stdout=subprocess.DEVNULL)
            context = ssl.create_default_context(cafile=str(cert))

            def connect():
                return closing(HTTPSConnection("127.0.0.1", port, context=context, timeout=4))

            for attempt in range(50):
                try:
                    with connect() as client:
                        client.request("GET", "/history")
                        response = client.getresponse()
                        assert response.status == 200
                        assert response.read() == b"/history|https|127.0.0.1"
                    break
                except OSError:
                    if process.poll() is not None or attempt == 49:
                        raise
                    time.sleep(0.1)
            with connect() as client:
                client.request("GET", "/api/cookie", headers={"Cookie": "ipa_test=synthetic"})
                response = client.getresponse()
                assert response.status == 200
                assert response.getheader("Set-Cookie") == "ipa_test=synthetic; Path=/; HttpOnly; Secure; SameSite=Lax"
                assert response.read() == b"ipa_test=synthetic"
            with connect() as client:
                client.request("GET", "/api/events")
                response = client.getresponse()
                assert response.status == 200
                assert response.getheader("Content-Type") == "text/event-stream"
                # Upstream cannot finish until the client observes the first event.
                # Buffering the whole response therefore fails by client timeout.
                assert response.readline() == b"data: first\n"
                assert response.readline() == b"\n"
                assert not finished.is_set()
                release.set()
                assert response.read() == b"data: second\n\n"
            with connect() as client:
                client.request("GET", "/api/fail")
                response = client.getresponse()
                assert response.status == 502
                response.read()
            assert calls["/api/fail"] == 1
            assert calls["/api/events"] == 1
            print("PASS: HTTPS routing/forwarded headers, Cookie, incremental SSE, failed request once")
    finally:
        release.set()
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        for server in (api, web):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=5)


if __name__ == "__main__":
    main()
