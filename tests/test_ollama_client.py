import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from maestro.providers.ollama import OllamaClient

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/tags":
            body = json.dumps({"models":[{"name":"tiny:latest","size":123,"digest":"abc","details":{"family":"tiny","parameter_size":"0.6B","quantization_level":"Q4","context_length":4096,"embedding_length":1024},"capabilities":["completion","thinking"]}]}).encode()
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        length = int(self.headers.get("Content-Length","0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/generate":
            body = json.dumps({"model":payload["model"],"response":"OK","done":True,"done_reason":"stop","total_duration":3_000_000_000,"load_duration":1_000_000_000,"prompt_eval_count":10,"eval_count":50,"eval_duration":1_000_000_000,"thinking":"DO NOT PERSIST","context":[1,2,3]}).encode()
        elif self.path == "/api/embed":
            body = json.dumps({"model":payload["model"],"embeddings":[[0.1,0.2,0.3]],"total_duration":1_000_000_000,"load_duration":500_000_000,"prompt_eval_count":3}).encode()
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(body)
    def log_message(self, *args): pass

class OllamaClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1",0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
    def test_tags_generate_embed(self):
        c = OllamaClient(self.url)
        self.assertEqual(c.tags()["models"][0]["name"], "tiny:latest")
        self.assertEqual(c.generate(model="tiny:latest", prompt="x")["response"], "OK")
        self.assertEqual(len(c.embed(model="embed", input_text="x")["embeddings"][0]), 3)

if __name__ == "__main__":
    unittest.main()
