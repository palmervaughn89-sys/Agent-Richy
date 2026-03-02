"""Agent Richy v2 — FastAPI Backend Entry Point."""

import sys
import os
import logging

# Add parent directory so imports of video_data, agent_richy work
# Use append (not insert) to avoid shadowing this module's own main.py
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, keystroke, profile, kids, calculators, coupons
from routers.trading import router as trading_router
from core.config import AGENTS, COLORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent Richy API",
    description="AI-powered financial coaching platform — backend API",
    version="2.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(chat.router)
app.include_router(keystroke.router)
app.include_router(profile.router)
app.include_router(kids.router)
app.include_router(calculators.router)
app.include_router(coupons.router)
app.include_router(trading_router)


@app.get("/")
async def root():
    return {
        "app": "Agent Richy",
        "version": "2.0.0",
        "status": "running",
        "agents": list(AGENTS.keys()),
    }


@app.get("/api/agents")
async def list_agents():
    """Return all available AI agents."""
    return {"agents": AGENTS}


@app.get("/api/health")
async def health():
    """Health check."""
    from core.config import OPENAI_API_KEY, GOOGLE_API_KEY
    return {
        "status": "healthy",
        "llm_configured": bool(OPENAI_API_KEY or GOOGLE_API_KEY),
        "agents_available": len(AGENTS),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
