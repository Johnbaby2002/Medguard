from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import CaregiverAccess, OrganizationMember, User, UserRole

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_roles(*roles: UserRole):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user

    return dependency


def can_access_patient(db: Session, actor: User, patient_id: str, require_manage: bool = False) -> bool:
    if actor.id == patient_id:
        return True
    if actor.role in {UserRole.admin, UserRole.clinician}:
        return True
    access = (
        db.query(CaregiverAccess)
        .filter(CaregiverAccess.patient_id == patient_id, CaregiverAccess.caregiver_id == actor.id)
        .first()
    )
    if not access:
        return False
    return access.can_manage if require_manage else True


def is_org_admin(db: Session, actor: User, organization_id: str) -> bool:
    if actor.role == UserRole.admin:
        return True
    membership = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == actor.id,
            OrganizationMember.role.in_([UserRole.admin, UserRole.clinician]),
        )
        .first()
    )
    return membership is not None
