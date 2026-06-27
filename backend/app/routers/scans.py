from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import MedicationScan, ScanStatus, ScanType, User
from app.schemas import BarcodeScanRequest, MedicationDraftOut, MedicationScanOut, PrescriptionOCRDraftRequest
from app.services.audit import log_audit

router = APIRouter(prefix="/scans", tags=["scan intake"])


def build_medication_draft(
    name: str | None,
    active_ingredient: str | None,
    dosage: str | None,
    notes: str | None,
    is_prescription: bool = True,
) -> MedicationDraftOut:
    resolved_name = name or "Unknown medication"
    return MedicationDraftOut(
        name=resolved_name,
        active_ingredient=active_ingredient or resolved_name,
        dosage=dosage or "confirm with package or prescription",
        frequency="confirm with label",
        medication_category=None,
        is_prescription=is_prescription,
        notes=notes,
    )


@router.post("/barcode", response_model=MedicationScanOut, status_code=status.HTTP_201_CREATED)
def create_barcode_scan(
    payload: BarcodeScanRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationScan:
    draft = build_medication_draft(
        payload.product_name,
        payload.active_ingredient,
        payload.dosage,
        payload.notes or f"Barcode captured: {payload.barcode}",
        is_prescription=False,
    )
    scan = MedicationScan(
        user_id=current_user.id,
        scan_type=ScanType.barcode,
        raw_value=payload.barcode,
        status=ScanStatus.matched if payload.product_name else ScanStatus.needs_review,
        confidence=70 if payload.product_name else 20,
        medication_draft=draft.model_dump(mode="json"),
    )
    db.add(scan)
    db.flush()
    log_audit(db, current_user, "create_barcode_scan", "medication_scan", scan.id)
    db.commit()
    db.refresh(scan)
    return scan


@router.post("/prescription-ocr", response_model=MedicationScanOut, status_code=status.HTTP_201_CREATED)
def create_prescription_ocr_draft(
    payload: PrescriptionOCRDraftRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MedicationScan:
    lines = [line.strip() for line in payload.ocr_text.splitlines() if line.strip()]
    first_line = lines[0] if lines else "Unknown prescription"
    second_line = lines[1] if len(lines) > 1 else None
    draft = build_medication_draft(
        first_line,
        first_line,
        second_line,
        "Draft created from OCR text. Review all fields before saving as a medication.",
        is_prescription=True,
    )
    scan = MedicationScan(
        user_id=current_user.id,
        scan_type=ScanType.prescription_ocr,
        raw_value=payload.ocr_text,
        status=ScanStatus.draft,
        confidence=35,
        medication_draft=draft.model_dump(mode="json"),
    )
    db.add(scan)
    db.flush()
    log_audit(
        db,
        current_user,
        "create_prescription_ocr_draft",
        "medication_scan",
        scan.id,
        {"image_reference": payload.image_reference},
    )
    db.commit()
    db.refresh(scan)
    return scan


@router.get("", response_model=list[MedicationScanOut])
def list_scans(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[MedicationScan]:
    return list(
        db.scalars(
            select(MedicationScan)
            .where(MedicationScan.user_id == current_user.id)
            .order_by(MedicationScan.created_at.desc())
        )
    )
