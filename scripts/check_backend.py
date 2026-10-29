"""Run the reviewed offline regression suite without reading local credentials."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import sys
import tempfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
# Explicit allowlist: several other tests in tests/ call the real provider.
OFFLINE_TESTS = (
    "tests/test_backup_history.py",
    "tests/test_parser_factory.py",
    "tests/test_pdf_parser.py",
    "tests/test_docx_parser.py",
    "tests/test_qwen_provider.py",
    "tests/test_api_workflow.py",
    "tests/test_api_smoke.py",
    "tests/test_api_sessions.py",
    "tests/test_auth.py",
    "tests/test_history_api.py",
    "tests/test_record_workflow.py",
)


def check_loopback() -> None:
    """Fail before TestClient hangs in Windows asyncio socketpair creation."""
    previous_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(3)
        left, right = socket.socketpair()
        with left, right:
            left.sendall(b"ok")
            if right.recv(2) != b"ok":
                raise OSError("loopback socketpair did not transfer data")
    finally:
        socket.setdefaulttimeout(previous_timeout)


def main() -> int:
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    # These settings apply to this check process only, never the user's .env.
    os.environ.update(
        DEBUG="true",
        DASHSCOPE_API_KEY="offline-test-key",
        LLM_BASE_URL="https://offline.invalid/v1",
        LLM_DEFAULT_MODEL="qwen3.7-plus",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTEST_ADDOPTS="",
        PYTEST_PLUGINS="",
        GITHUB_AUTH_ENABLED="false",
    )
    sys.dont_write_bytecode = True
    try:
        check_loopback()
    except OSError as exc:
        print(
            f"ENVIRONMENT BLOCKED: local socketpair failed: {exc}. "
            "FastAPI TestClient needs local loopback access. "
            "Use a permitted terminal/environment; no business tests have run.",
            file=sys.stderr,
        )
        return 2

    original_connect = socket.socket.connect
    original_connect_ex = socket.socket.connect_ex

    def guard_connection(original):
        def connect(sock, address):
            if sock.family in (socket.AF_INET, socket.AF_INET6):
                if address[0] not in ("127.0.0.1", "::1"):
                    raise RuntimeError(
                        f"Offline regression blocked an external connection: {address[0]}"
                    )
            return original(sock, address)

        return connect

    import pytest

    # Use a fresh, owned temporary directory; do not delete/reuse user outputs.
    # Mock dotenv before config is imported, so local .env is never loaded.
    with (
        tempfile.TemporaryDirectory(prefix="interview-prep-check-") as temp_dir,
        patch("dotenv.load_dotenv", return_value=False),
        patch.object(socket.socket, "connect", guard_connection(original_connect)),
        patch.object(socket.socket, "connect_ex", guard_connection(original_connect_ex)),
    ):
        print(f"Offline suite: {len(OFFLINE_TESTS)} files; Python {sys.version.split()[0]}", flush=True)
        return int(
            pytest.main(
                [
                    *OFFLINE_TESTS,
                    "-q",
                    "-rs",
                    "--tb=short",
                    "-p", "no:cacheprovider",
                    "-o", "faulthandler_timeout=30",
                    f"--basetemp={Path(temp_dir) / 'pytest'}",
                ]
            )
        )


if __name__ == "__main__":
    raise SystemExit(main())
