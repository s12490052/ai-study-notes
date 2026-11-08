"""Loopback-only web UI. GitHub Pages serves the separate static portfolio."""

import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from studynote import StudyNoteError, generate_note

SITE = Path(__file__).resolve().parent / "site"


class Handler(SimpleHTTPRequestHandler):
    model = None
    generation_lock = threading.Lock()

    def send_json(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/health":
            self.send_json(200, {"mode": "local", "model": self.model or "qwen3:1.7b"})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != "/api/analyze":
            self.send_json(404, {"error": "找不到此 API。"})
            return
        expected_host = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != expected_host or self.headers.get("Origin") not in {None, f"http://{expected_host}"}:
            self.send_json(403, {"error": "請從本機頁面使用此功能。"})
            return
        if self.headers.get_content_type() != "application/json":
            self.send_json(415, {"error": "請使用 JSON 格式。"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 40000:
                self.send_json(413, {"error": "請提供 30 至 6000 字的文章。"})
                return
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(body, dict):
                raise ValueError("JSON 必須是物件")
        except (ValueError, UnicodeError):
            self.send_json(400, {"error": "無效的 JSON 請求。"})
            return
        if not self.generation_lock.acquire(blocking=False):
            self.send_json(429, {"error": "模型正在處理另一份筆記，請稍後再試。"})
            return
        try:
            result = generate_note(body.get("text"), model=self.model)
            self.send_json(200, result)
        except StudyNoteError as error:
            self.send_json(400, {"error": str(error)})
        except Exception:
            self.send_json(500, {"error": "產生筆記時發生錯誤，請查看終端機並重試。"})
            raise
        finally:
            self.generation_lock.release()


def serve(port=8000, model=None):
    Handler.model = model
    server = ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(SITE)))
    print(f"拾頁本機介面：http://127.0.0.1:{server.server_port}/app.html", flush=True)
    print("按 Ctrl+C 結束。本機生成內容不會自動寫入檔案或上傳 GitHub。", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
