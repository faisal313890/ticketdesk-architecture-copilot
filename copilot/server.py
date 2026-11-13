"""Serve the local web interface and JSON answer endpoint."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .core import Copilot, Snapshot, local_generator, ollama_generator

WEB = Path(__file__).with_name("web")

def make_server(copilot, port):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, content, kind):
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(content)
        def json_reply(self, status, body):
            self.reply(status,json.dumps(body).encode("utf-8"),"application/json")
        def do_GET(self):
            asset = {"/":("index.html","text/html"),"/app.js":("app.js","text/javascript"),
                     "/styles.css":("styles.css","text/css")}.get(self.path)
            if asset is None:
                return self.json_reply(404,{"error":"Not found"})
            filename, kind = asset
            self.reply(200,(WEB/filename).read_bytes(),kind+"; charset=utf-8")
        def do_POST(self):
            if self.path != "/api/ask":
                return self.json_reply(404,{"error":"Not found"})
            try:
                size = int(self.headers.get("Content-Length","0"))
                if not 1 <= size <= 4096:
                    raise ValueError()
                payload = json.loads(self.rfile.read(size))
                question = payload["question"]
                if not isinstance(question,str) or not 1 <= len(question.strip()) <= 500:
                    raise ValueError()
            except (ValueError,KeyError,TypeError):
                return self.json_reply(400,{"error":"Provide a question of 1–500 characters."})
            answer,_ = copilot.ask(question.strip())
            self.json_reply(200,answer)
    return ThreadingHTTPServer(("127.0.0.1",port),Handler)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo",required=True)
    parser.add_argument("--cache", default=".cache/index.sqlite3")
    parser.add_argument("--port",type=int,default=8765)
    parser.add_argument("--ollama-model", help="Optional installed local Ollama chat model")
    args = parser.parse_args()
    generator = ollama_generator(args.ollama_model) if args.ollama_model else local_generator
    with make_server(Copilot(Snapshot(args.repo,args.cache),generator),args.port) as server:
        print(f"Open http://127.0.0.1:{args.port}",flush=True)
        server.serve_forever()
