"""Document routes."""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from partner_os_v2.api.deps import get_current_user
from partner_os_v2.api.errors import error_responses
from partner_os_v2.db import get_db
from partner_os_v2.models import Document, User
from partner_os_v2.schemas import DocumentImportRequest, DocumentOut
from partner_os_v2.services.audit import log_event

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post(
    "/import",
    response_model=DocumentOut,
    responses=error_responses(401),
)
def import_document(
    payload: DocumentImportRequest = Body(
        ...,
        openapi_examples={
            "default": {
                "summary": "Link document to entity",
                "value": {
                    "entity_type": "deal",
                    "entity_id": "9ea9cb4b-b133-4a35-9378-567f92fdddb2",
                    "file_name": "psa_form_21.pdf",
                    "file_path": "/data/deals/psa_form_21.pdf",
                    "checksum": "sha256:abc123",
                },
            }
        },
    ),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DocumentOut:
    document = Document(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        file_name=payload.file_name,
        file_path=payload.file_path,
        checksum=payload.checksum,
        created_by=user.user_id,
    )
    db.add(document)
    db.flush()
    log_event(
        db,
        event_type="document_imported",
        actor_type="user",
        actor_id=user.user_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        payload={"document_id": document.document_id, "file_name": payload.file_name},
    )
    db.commit()
    db.refresh(document)
    return DocumentOut.model_validate(document, from_attributes=True)
