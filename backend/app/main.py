"""
Resume Optimizer — FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api import auth, resumes, jobs, matches, optimization, export, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    print(f">> {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    yield
    # Shutdown
    print(f">> {settings.APP_NAME} shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Resume Intelligence + Job Requirement Matching + Evidence-Based Optimization Engine",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])
app.include_router(resumes.router, prefix=f"{settings.API_PREFIX}/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix=f"{settings.API_PREFIX}/jobs", tags=["Job Descriptions"])
app.include_router(matches.router, prefix=f"{settings.API_PREFIX}/matches", tags=["Matching"])
app.include_router(optimization.router, prefix=f"{settings.API_PREFIX}/optimization", tags=["Optimization"])
app.include_router(export.router, prefix=f"{settings.API_PREFIX}/export", tags=["Export"])
app.include_router(tasks.router, prefix=f"{settings.API_PREFIX}/tasks", tags=["Tasks"])



@app.get("/")
@app.get(f"{settings.API_PREFIX}/")
@app.get(f"{settings.API_PREFIX}")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
    }


@app.get("/health")
@app.get(f"{settings.API_PREFIX}/health")
async def health():
    return {"status": "healthy"}
