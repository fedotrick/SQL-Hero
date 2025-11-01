from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import achievements, activity, auth, courses, leaderboard, progress, sandbox

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(progress.router)
app.include_router(achievements.router)
app.include_router(leaderboard.router)
app.include_router(activity.router)
app.include_router(sandbox.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
