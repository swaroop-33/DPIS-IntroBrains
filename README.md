🛡️ DPIS — Deepfake Psychological Impact Shield (v3.4)

Multi-modal forensic + psychological intelligence engine for detecting synthetic media, manipulation vectors, and disinformation risk.

🚀 Overview

DPIS (Deepfake Psychological Impact Shield) is an advanced multi-layer intelligence system that analyzes:

Text

Images

Audio

Video

Remote media URLs

It produces structured forensic and psychological risk metrics including:

PPS — Psychological Propaganda Score

SDI — Societal Disruption Index

Emotional amplification metrics

Manipulation & propaganda detection

Virality risk modeling

Credibility erosion index

Adversarial evasion detection

Platform amplification modeling

The system returns a 15-layer structured intelligence schema.

🧠 Architecture
Backend

FastAPI

Modular intelligence pipeline

Media forensic heuristics (image/video/audio)

Fully structured JSON output

Safe error handling (no HTML leakage)

Vercel-compatible API gateway

Frontend

React + Vite

Safe fetch wrapper (never crashes on invalid JSON)

Supports:

Text input

Media upload

Media URL ingestion

Clean separation of API service layer

📊 15-Layer Intelligence Schema

Every analysis returns these layers:

pps — Psychological Propaganda Score

sdi — Societal Disruption Index

forensic — Media authenticity analysis

emotion — Emotional amplification metrics

propaganda — Manipulation detection

virality — Spread modeling

counterfactual — Stability modeling

adversarial — Evasion detection

platform — Amplification profile

credibility_erosion — Legitimacy degradation

calibration — Confidence interval modeling

explanation — Human-readable summary

indices — Internal density metrics

intelligence_summary — Convergence analysis

performance — Execution metrics

📂 Project Structure
IB/
│
├── api/
│   └── index.py               # API gateway (Vercel-compatible)
│
├── backend/
│   ├── main.py                # FastAPI app
│   ├── pipeline.py            # Orchestrator (15-layer engine)
│   ├── core/
│   │   └── media_forensics.py
│   └── modules/
│       ├── deepfake.py
│       ├── emotion.py
│       ├── propaganda.py
│       ├── virality.py
│       ├── pps.py
│       ├── explainability.py
│       ├── adversarial.py
│       ├── calibration.py
│       ├── credibility.py
│       └── platform_amp.py
│
└── frontend/
    ├── src/
    │   └── services/api.js
    └── vite.config.js
⚙️ Running Locally
1️⃣ Backend

Run from project root:

python -m uvicorn api.index:app --reload

Backend will run at:

http://127.0.0.1:8000

API Docs:

http://127.0.0.1:8000/docs
2️⃣ Frontend

Inside frontend folder:

npm install
npm run dev

Runs at:

http://localhost:5175

Vite proxy forwards /api/* → backend automatically.

📡 API Endpoints
Health Check
GET /api/health
Text Analysis
POST /api/analyze
Multi-Modal Media Analysis
POST /api/analyze/media

Supports:

video

audio

image

media_url

text

🔬 Core Capabilities
Deepfake Detection

Text anomaly scoring

Image entropy + variance heuristics

Video frame anomaly detection

Audio spoofing detection (optional libs)

Psychological Manipulation Detection

Urgency exploitation

Authority exploitation

Absolutist framing

Polarization modeling

Emotional Signal Mapping

Fear

Anger

Urgency

Shock

Sadness

Outrage

Virality Estimation

Emotional amplification

Manipulation synergy

Platform multipliers

📈 PPS — Psychological Propaganda Score

Composite metric combining:

Deepfake risk

Emotional amplification

Manipulation intensity

Virality probability

Platform amplification

Score range: 0–100

Severity Levels:

LOW

ELEVATED

HIGH

CRITICAL

🛡️ Security & Stability

Safe JSON parsing (frontend)

Structured error handling (backend)

CORS configured for dev/demo

Modular architecture (no circular imports)

No hardcoded secrets

🌍 Deployment
Vercel (Serverless)

api/index.py acts as entry point

/api/* routes forwarded automatically

Works without path rewrites

Local Dev

Vite proxy strips /api

Same behavior as production

📌 Version

DPIS v3.4.0

Includes:

Platform amplification modeling

Credibility erosion index

Adversarial evasion detection

Calibration confidence intervals

Intelligence convergence modeling

🎯 Use Cases

Media verification systems

Social media moderation tools

Deepfake detection demos

Research projects (psychological impact modeling)

Hackathon AI security tools

👨‍💻 Author

Swaroop
AI & Data Science Developer
Multi-Modal Forensic Intelligence Research
