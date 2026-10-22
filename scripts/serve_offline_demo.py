"""Local browser acceptance server: real HTTP routes, synthetic LLM only.

Does not read .env, accepts loopback traffic only, and blocks external sockets.
Never use this replacement provider server as a production entry point.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import sys
from urllib.parse import urlparse
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--capacity", type=int, default=100)
    parser.add_argument("--frontend-origin", default="http://127.0.0.1:3168")
    args = parser.parse_args()
    origin = urlparse(args.frontend_origin)
    if origin.scheme != "http" or origin.hostname not in ("localhost", "127.0.0.1"):
        parser.error("frontend-origin must be a loopback HTTP origin")
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    sys.dont_write_bytecode = True
    os.environ.update(DEBUG="true", DASHSCOPE_API_KEY="offline-test-key", LLM_BASE_URL="https://offline.invalid/v1")
    fixtures = json.loads((ROOT / "tests/fixtures/workflow/llm_responses.json").read_text(encoding="utf-8"))

    class SyntheticLLM:
        def call(self, *, response_model, **kwargs):
            return response_model.model_validate(fixtures[response_model.__name__])

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def guard(original):
        def connect(sock, address):
            if sock.family in (socket.AF_INET, socket.AF_INET6) and address[0] not in ("127.0.0.1", "::1"):
                raise RuntimeError("Offline acceptance blocks external sockets")
            return original(sock, address)
        return connect

    with patch("dotenv.load_dotenv", return_value=False):
        import uvicorn
        from api import main as application
        from api.routes import analyze, questions
        from api.session import SessionStore
        application.session_store = SessionStore(capacity=args.capacity)
        for middleware in application.app.user_middleware:
            if middleware.cls is application.CORSMiddleware:
                middleware.kwargs["allow_origins"] = [args.frontend_origin]
        analyze.LLMService = questions.LLMService = SyntheticLLM
        with (patch.object(socket.socket, "connect", guard(original_connect)),
              patch.object(socket.socket, "connect_ex", guard(original_connect_ex))):
            print("SYNTHETIC PROVIDER ONLY; no credentials or real model calls", flush=True)
            uvicorn.run(application.app, host="127.0.0.1", port=args.port, access_log=False)


if __name__ == "__main__":
    main()
