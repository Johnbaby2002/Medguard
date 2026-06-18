from fastapi import APIRouter

from app.api.routes import auth, caregivers, dashboard, dose_logs, medications, reports, safety

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(medications.router, tags=["medications"])
api_router.include_router(dose_logs.router, prefix="/dose-logs", tags=["dose logs"])
api_router.include_router(safety.router, prefix="/safety", tags=["safety checks"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(caregivers.router, prefix="/caregivers", tags=["caregivers"])
