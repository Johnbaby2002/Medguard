from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, is_org_admin
from app.database import get_db
from app.models import IntegrationConnection, User
from app.schemas import IntegrationConnectionCreate, IntegrationConnectionOut, SupportedLanguageOut
from app.services.audit import log_audit

router = APIRouter(tags=["integrations"])


@router.post("/integrations", response_model=IntegrationConnectionOut, status_code=status.HTTP_201_CREATED)
def create_integration_connection(
    payload: IntegrationConnectionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> IntegrationConnection:
    if payload.organization_id and not is_org_admin(db, current_user, payload.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization admin access required")
    connection = IntegrationConnection(
        user_id=None if payload.organization_id else current_user.id,
        organization_id=payload.organization_id,
        integration_type=payload.integration_type,
        status=payload.status,
        provider_name=payload.provider_name,
        external_reference=payload.external_reference,
        metadata_json=payload.metadata_json,
    )
    db.add(connection)
    db.flush()
    log_audit(db, current_user, "create_integration_connection", "integration_connection", connection.id)
    db.commit()
    db.refresh(connection)
    return connection


@router.get("/integrations", response_model=list[IntegrationConnectionOut])
def list_integration_connections(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[IntegrationConnection]:
    return list(
        db.scalars(
            select(IntegrationConnection)
            .where(IntegrationConnection.user_id == current_user.id)
            .order_by(IntegrationConnection.created_at.desc())
        )
    )


@router.get("/localization/languages", response_model=list[SupportedLanguageOut])
def supported_languages() -> list[SupportedLanguageOut]:
    return [
        SupportedLanguageOut(code="en", name="English", status="available"),
        SupportedLanguageOut(code="de", name="German", status="planned"),
        SupportedLanguageOut(code="es", name="Spanish", status="planned"),
        SupportedLanguageOut(code="fr", name="French", status="planned"),
    ]
