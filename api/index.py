import sys
import os

# ── Path resolution ────────────────────────────────────────────────────────────
# _root   → enables `import backend.xyz`
# _backend → enables `import modules.xyz` and `import core.xyz`
#             (matches how uvicorn main:app resolves from inside /backend)
_here    = os.path.dirname(os.path.abspath(__file__))
_root    = os.path.dirname(_here)
_backend = os.path.join(_root, "backend")

for _p in (_root, _backend):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Imports ────────────────────────────────────────────────────────────────────
from fastapi import FastAPI                                   # noqa: E402
from fastapi.middleware.cors import CORSMiddleware            # noqa: E402
from fastapi.responses import JSONResponse                    # noqa: E402
from backend.main import app as _backend_app                 # noqa: E402

# ── Outer wrapper app ──────────────────────────────────────────────────────────
# Vercel routes /api/* to this file with the FULL path intact.
# e.g. browser requests /api/analyze → Vercel sends /api/analyze to this app.
# We mount the backend app at /api so it strips the prefix:
#   /api/analyze      → backend sees /analyze      ✓
#   /api/analyze/media → backend sees /analyze/media ✓
#   /api/health       → backend sees /health        ✓
#
# Same behaviour in local dev when vite proxy does NOT rewrite paths.

app = FastAPI(title="DPIS API Gateway")

# CORS — allow all origins for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Generic error handler — ensures JSON is always returned, never HTML
@app.exception_handler(Exception)
async def _unhandled(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Mount the real backend under /api
app.mount("/api", _backend_app)
