import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
# Project root  → enables `import backend.xyz`
# Backend dir   → enables `import modules.xyz` / `import core.xyz`
#                 (matches how uvicorn main:app resolves inside /backend)
_here = os.path.dirname(os.path.abspath(__file__))   # /api
_root = os.path.dirname(_here)                        # project root
_backend = os.path.join(_root, "backend")             # /backend

for _p in (_root, _backend):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Mount the full backend app ────────────────────────────────────────────────
# Import the app object that already defines ALL routes:
#   GET  /          → banner
#   GET  /health    → health check
#   POST /analyze   → text pipeline
#   POST /analyze/media → multi-modal forensic pipeline
#
# No duplication, no logic changes — just re-exporting the same app.
from backend.main import app  # noqa: E402  (import after sys.path mutation)

__all__ = ["app"]
