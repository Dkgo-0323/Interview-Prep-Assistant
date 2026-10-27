"""SSE wire format shared by anonymous and account workflows."""
import json


def _sse(step: str, message: str, data: dict = None) -> str:
    payload = {"step": step, "message": message}
    if data is not None:
        payload["data"] = data
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
