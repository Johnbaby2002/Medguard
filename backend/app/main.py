from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
from app.routers import auth, caregiver, dashboard, medications, organizations, profile, reminders, reports, safety, supplements
from app.rule_engine.seed_rules import seed_interaction_rules


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        seed_interaction_rules(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        description=(
            "Backend API for MedGuard. Handles authentication, profiles, medications, "
            "reminders, dose logs, caregiver sharing, doctor reports, and AI safety-check handoff records."
        ),
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["health"])
    def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "status": "ok",
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1",
        }

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name, "environment": settings.environment}

    routers = [
        auth.router,
        dashboard.router,
        profile.router,
        medications.router,
        supplements.router,
        safety.router,
        reminders.router,
        reports.router,
        caregiver.router,
        organizations.router,
    ]
    for router in routers:
        app.include_router(router)
        app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
