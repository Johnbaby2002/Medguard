from datetime import timedelta, timezone
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import ShareToken, User, utc_now
from app.routers.reports import medication_summary
from app.schemas import ShareReportLinkCreate, ShareReportLinkOut, SharedReportResponse
from app.services.audit import log_audit

router = APIRouter(prefix="/share", tags=["sharing"])


@router.post("/report-link", response_model=ShareReportLinkOut, status_code=status.HTTP_201_CREATED)
def create_report_link(
    payload: ShareReportLinkCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ShareReportLinkOut:
    raw_token = secrets.token_urlsafe(32)
    share = ShareToken(
        user_id=current_user.id,
        token=raw_token,
        purpose=payload.purpose,
        expires_at=utc_now() + timedelta(hours=payload.expires_in_hours),
    )
    db.add(share)
    db.flush()
    log_audit(db, current_user, "create_share_report_link", "share_token", share.id)
    db.commit()
    db.refresh(share)
    return ShareReportLinkOut(
        id=share.id,
        token=share.token,
        purpose=share.purpose,
        expires_at=share.expires_at,
        url_path=f"/share/report/{share.token}",
        revoked=share.revoked,
    )


@router.get("/report/{token}", response_model=SharedReportResponse)
def get_shared_report(token: str, db: Annotated[Session, Depends(get_db)]) -> SharedReportResponse:
    share = db.scalar(select(ShareToken).where(ShareToken.token == token))
    if not share or share.revoked:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found")
    expires_at = share.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < utc_now():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share link has expired")
    user = db.get(User, share.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared report user not found")
    report = medication_summary(user, db)
    return SharedReportResponse(purpose=share.purpose, expires_at=share.expires_at, report=report)
