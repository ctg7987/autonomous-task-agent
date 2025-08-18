import os
from typing import Any

# Minimal stub for optional Langfuse initialization

def init_langfuse() -> Any:
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST")
    if not (public and secret and host):
        return None
    try:
        from langfuse import Langfuse  # type: ignore
        return Langfuse(public_key=public, secret_key=secret, host=host)
    except Exception:
        return None
