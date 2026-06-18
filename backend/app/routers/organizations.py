from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, is_org_admin, require_roles
from app.database import get_db
from app.models import Organization, OrganizationMember, User, UserRole
from app.schemas import OrganizationCreate, OrganizationMemberCreate, OrganizationMemberOut, OrganizationOut
from app.services.audit import log_audit

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate,
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.clinician))],
    db: Annotated[Session, Depends(get_db)],
) -> Organization:
    organization = Organization(**payload.model_dump())
    db.add(organization)
    db.flush()
    db.add(OrganizationMember(organization_id=organization.id, user_id=current_user.id, role=UserRole.admin))
    log_audit(db, current_user, "create_organization", "organization", organization.id)
    db.commit()
    db.refresh(organization)
    return organization


@router.get("", response_model=list[OrganizationOut])
def list_organizations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Organization]:
    if current_user.role == UserRole.admin:
        return list(db.scalars(select(Organization).order_by(Organization.name)))
    memberships = list(
        db.scalars(select(OrganizationMember).where(OrganizationMember.user_id == current_user.id))
    )
    if not memberships:
        return []
    ids = [membership.organization_id for membership in memberships]
    return list(db.scalars(select(Organization).where(Organization.id.in_(ids)).order_by(Organization.name)))


@router.post("/{organization_id}/members", response_model=OrganizationMemberOut, status_code=status.HTTP_201_CREATED)
def add_organization_member(
    organization_id: str,
    payload: OrganizationMemberCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationMember:
    if not is_org_admin(db, current_user, organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization admin access required")
    user = db.scalar(select(User).where(User.email == payload.user_email.lower()))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User must register first")
    member = db.scalar(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user.id,
        )
    )
    if not member:
        member = OrganizationMember(organization_id=organization_id, user_id=user.id, role=payload.role)
        db.add(member)
    else:
        member.role = payload.role
    db.flush()
    log_audit(db, current_user, "upsert_organization_member", "organization_member", member.id)
    db.commit()
    db.refresh(member)
    return member
