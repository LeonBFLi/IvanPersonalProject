from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs
import json
import mimetypes

ROOT = Path(__file__).parent
TEMPLATE_PATH = ROOT / "templates" / "index.html"
STATIC_ROOT = ROOT / "static"
LOG_DIR = Path("/var/ivanproject/logs")
LOG_FILE = LOG_DIR / "comments.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def append_comment(name: str, message: str) -> None:
    timestamp = datetime.utcnow().isoformat(timespec="seconds")
    log_entry = f"[{timestamp} UTC] {name}: {message}\n"
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(log_entry)


class ResumeHandler(BaseHTTPRequestHandler):
    def _send_headers(self, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):  # noqa: N802
        if self.path in {"/", "/index.html"}:
            content = TEMPLATE_PATH.read_bytes()
            self._send_headers(200, "text/html; charset=utf-8")
            self.wfile.write(content)
            return

        if self.path.startswith("/static/"):
            target = STATIC_ROOT / self.path.replace("/static/", "", 1)
            if target.exists() and target.is_file():
                mime, _ = mimetypes.guess_type(target.name)
                self._send_headers(200, mime or "application/octet-stream")
                self.wfile.write(target.read_bytes())
            else:
                self._send_headers(404, "text/plain; charset=utf-8")
                self.wfile.write(b"Not Found")
            return

        self._send_headers(404, "text/plain; charset=utf-8")
        self.wfile.write(b"Not Found")

    def do_POST(self):  # noqa: N802
        if self.path != "/comment":
            self._send_headers(404, "application/json")
            self.wfile.write(json.dumps({"status": "error", "message": "Not Found"}).encode())
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode()
        data = parse_qs(body)
        name = (data.get("name", ["Anonymous"])[0] or "Anonymous").strip() or "Anonymous"
        message = (data.get("message", [""])[0]).strip()

        if not message:
            self._send_headers(400, "application/json")
            self.wfile.write(json.dumps({"status": "error", "message": "留言内容不能为空。"}).encode())
            return

        append_comment(name, message)
        self._send_headers(200, "application/json")
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args) -> None:  # noqa: A003, D401
        """Silence default stdout logging to keep runtime lightweight."""
        return


def main() -> None:
    server = HTTPServer(("0.0.0.0", 1888), ResumeHandler)
    print("Serving resume site on http://0.0.0.0:1888")
    server.serve_forever()


if __name__ == "__main__":
    main()
