import sys
import os

# Resolve paths
_here = os.path.dirname(os.path.abspath(__file__))       # /api
_root = os.path.dirname(_here)                            # project root
_backend = os.path.join(_root, "backend")                 # /backend

# Project root  → enables  `import backend.xyz`
# Backend dir   → enables  `import modules.xyz` / `import core.xyz`
#                 (exactly how uvicorn main:app sees it from inside /backend)
for _p in (_root, _backend):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI
from backend.pipeline import run_pipeline

app = FastAPI()


@app.get("/")
def root():
    return {"status": "DPIS API running"}


@app.post("/analyze")
async def analyze(payload: dict):
    text = payload.get("text", "")
    input_type = payload.get("input_type", "text")
    simulated = payload.get("simulated_deepfake_score")
    return run_pipeline(
        text=text,
        input_type=input_type,
        simulated_deepfake_score=simulated,
    )
