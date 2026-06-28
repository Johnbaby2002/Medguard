from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app.routers import (
    adherence,
    ai,
    assistant,
    auth,
    caregiver,
    dashboard,
    emergency,
    integrations,
    medications,
    organizations,
    profile,
    refills,
    reminders,
    reports,
    safety,
    scans,
    share,
    side_effects,
    substances,
    supplements,
    timeline,
)
from app.rule_engine.seed_rules import seed_interaction_rules


def ensure_postgres_enum_values() -> None:
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'scantype') THEN
                        ALTER TYPE scantype ADD VALUE IF NOT EXISTS 'camera';
                        ALTER TYPE scantype ADD VALUE IF NOT EXISTS 'upload';
                    END IF;
                    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'interactiontype') THEN
                        ALTER TYPE interactiontype ADD VALUE IF NOT EXISTS 'lifestyle';
                    END IF;
                    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reminderstatus') THEN
                        ALTER TYPE reminderstatus ADD VALUE IF NOT EXISTS 'late';
                    END IF;
                END $$;
                """
            )
        )


def ensure_existing_database_columns() -> None:
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            user_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(users)")).fetchall()}
            if "phone_number" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(40)"))
            if "terms_accepted_at" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN terms_accepted_at DATETIME"))
            if "medical_disclaimer_accepted_at" not in user_columns:
                connection.execute(text("ALTER TABLE users ADD COLUMN medical_disclaimer_accepted_at DATETIME"))

            profile_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(health_profiles)")).fetchall()}
            if "emergency_contact_name" not in profile_columns:
                connection.execute(text("ALTER TABLE health_profiles ADD COLUMN emergency_contact_name VARCHAR(255)"))
            if "emergency_contact_phone" not in profile_columns:
                connection.execute(text("ALTER TABLE health_profiles ADD COLUMN emergency_contact_phone VARCHAR(40)"))

            medication_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(medications)")).fetchall()}
            if "pills_remaining" not in medication_columns:
                connection.execute(text("ALTER TABLE medications ADD COLUMN pills_remaining INTEGER"))
            if "pills_per_dose" not in medication_columns:
                connection.execute(text("ALTER TABLE medications ADD COLUMN pills_per_dose INTEGER"))
            if "refill_threshold" not in medication_columns:
                connection.execute(text("ALTER TABLE medications ADD COLUMN refill_threshold INTEGER"))
            if "pharmacy_name" not in medication_columns:
                connection.execute(text("ALTER TABLE medications ADD COLUMN pharmacy_name VARCHAR(255)"))
    elif engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(40)"))
            connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS terms_accepted_at TIMESTAMP WITH TIME ZONE"))
            connection.execute(
                text("ALTER TABLE users ADD COLUMN IF NOT EXISTS medical_disclaimer_accepted_at TIMESTAMP WITH TIME ZONE")
            )
            connection.execute(text("ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(255)"))
            connection.execute(text("ALTER TABLE health_profiles ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(40)"))
            connection.execute(text("ALTER TABLE medications ADD COLUMN IF NOT EXISTS pills_remaining INTEGER"))
            connection.execute(text("ALTER TABLE medications ADD COLUMN IF NOT EXISTS pills_per_dose INTEGER"))
            connection.execute(text("ALTER TABLE medications ADD COLUMN IF NOT EXISTS refill_threshold INTEGER"))
            connection.execute(text("ALTER TABLE medications ADD COLUMN IF NOT EXISTS pharmacy_name VARCHAR(255)"))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ensure_postgres_enum_values()
    Base.metadata.create_all(bind=engine)
    ensure_existing_database_columns()
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
            "scan intake, reminders, dose logs, caregiver sharing, doctor reports, AI handoff, "
            "integration starters, and rule-based medication safety checks."
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
        refills.router,
        scans.router,
        supplements.router,
        substances.router,
        safety.router,
        assistant.router,
        ai.router,
        timeline.router,
        adherence.router,
        reminders.router,
        side_effects.router,
        reports.router,
        emergency.router,
        caregiver.router,
        share.router,
        organizations.router,
        integrations.router,
    ]
    for router in routers:
        app.include_router(router)
        app.include_router(router, prefix="/api/v1")
    return app


app = create_app()
