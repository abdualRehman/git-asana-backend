import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routes import git
from app.routes import asana
from app.routes import analytics
from app.asana.task_fetcher import fetch_tasks
from app.services.git_reloader import reload_git_repos


# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Initialize FastAPI app
app = FastAPI(
    title="Git-Asana Integration API",
    description="API for integrating Git commit history with Asana tasks",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
try:
    app.include_router(git.router, prefix="/api")
    app.include_router(asana.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    # app.include_router(reload_all.router)

except ImportError as e:
    print(f"Warning: Could not import git router - {e}")

# Test endpoint
@app.get("/")
async def read_root():
    return {
        "message": "Welcome to Git-Asana Integration API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "reload_all": "/reload_all",
            "git_report": "/api/git/report",
            "reload_repos": "/api/git/reload",
            "asana_summary": "/api/asana/summary",
            "analytics": "/api/analytics",
            "estimate_time_per_task": "/api/asana/efforts"
        }
    }
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reload_all")
def reload_all():
    asana_tasks = fetch_tasks(force_refresh=True)
    git_result = reload_git_repos()
    return {
        "asana_reloaded": len(asana_tasks),
        "git_result": git_result
    }