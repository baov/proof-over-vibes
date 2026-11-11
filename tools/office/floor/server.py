"""Serve the page, the snapshot and a live event stream. Read-only, loopback only."""

from __future__ import annotations

import json
import mimetypes
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from .decisions import decisions_for
from .snapshot import build_snapshot, read_report

WEB = Path(__file__).resolve().parents[1] / "web"
PING_SECONDS = 15.0

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("text/javascript", ".mjs")


class _Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler, root: Path, poll_seconds: float):
        super().__init__(address, handler)
        self.root = root
        self.poll_seconds = poll_seconds


class _Handler(BaseHTTPRequestHandler):
    server: _Server

    def log_message(self, format, *args):  # keep the terminal quiet
        pass

    def _host_allowed(self) -> bool:
        # A page on another site that rebinds its DNS name to 127.0.0.1 must not read the reports.
        port = self.server.server_address[1]
        allowed = {f"127.0.0.1:{port}", f"localhost:{port}", "127.0.0.1", "localhost"}
        return self.headers.get("Host", "") in allowed

    def _report(self, query: dict):
        run, role, raw = query.get("run", [None])[0], query.get("role", [None])[0], query.get("i", [None])[0]
        if not run or not role:
            self._send(400, "text/plain", b"run and role are required")
            return
        try:
            index = None if raw is None else int(raw)
        except ValueError:
            self._send(400, "text/plain", b"i must be an integer")
            return
        found = read_report(self.server.root, run, role, index)
        if found is None:
            self._send(404, "text/plain", b"not found")
        else:
            self._send(200, "application/json", json.dumps(found).encode())

    def do_GET(self):
        if not self._host_allowed():
            self._send(403, "text/plain", b"forbidden host")
            return
        parts = urlsplit(self.path)
        path = parts.path
        if path == "/api/report":
            self._report(parse_qs(parts.query))
        elif path == "/api/decisions":
            run = parse_qs(parts.query).get("run", [None])[0]
            self._send(200, "application/json", json.dumps(decisions_for(self.server.root, run)).encode())
        elif path == "/":
            self._file(WEB / "index.html")
        elif path == "/api/snapshot":
            self._send(200, "application/json", json.dumps(build_snapshot(self.server.root)).encode())
        elif path == "/events":
            self._events()
        elif path.startswith("/web/"):
            target = (WEB / unquote(path[len("/web/"):])).resolve()
            if WEB.resolve() in target.parents:
                self._file(target)
            else:
                self._send(404, "text/plain", b"not found")
        else:
            self._send(404, "text/plain", b"not found")

    def _send(self, status: int, content_type: str, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path: Path):
        if not path.is_file():
            self._send(404, "text/plain", b"not found")
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self._send(200, content_type, path.read_bytes())

    def _events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        last_key, last_ping = None, time.monotonic()
        try:
            while True:
                snapshot = build_snapshot(self.server.root)
                key = json.dumps(snapshot["runs"], sort_keys=True)
                if key != last_key:
                    last_key = key
                    self.wfile.write(f"data: {json.dumps(snapshot)}\n\n".encode())
                    self.wfile.flush()
                elif time.monotonic() - last_ping > PING_SECONDS:
                    last_ping = time.monotonic()
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                time.sleep(self.server.poll_seconds)
        except (BrokenPipeError, ConnectionResetError, OSError):
            return


def make_server(root: Path, host: str = "127.0.0.1", port: int = 0, poll_seconds: float = 1.0) -> ThreadingHTTPServer:
    return _Server((host, port), _Handler, Path(root), poll_seconds)
