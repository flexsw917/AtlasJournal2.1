from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models import Attachment, User
from app.schemas.trade import AttachmentRead
from app.services.trade_service import delete_attachment, list_attachments, save_attachment

router = APIRouter()


@router.post("/trades/{trade_id}/attachments", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    trade_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttachmentRead:
    contents = file.file.read(settings.max_upload_size + 1)
    if len(contents) > settings.max_upload_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large")
    file.file.seek(0)
    attachment = save_attachment(session, current_user, trade_id, file, str(settings.uploads_dir))
    return AttachmentRead.model_validate(attachment)


@router.get("/trades/{trade_id}/attachments", response_model=list[AttachmentRead])
def get_attachments(
    trade_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AttachmentRead]:
    attachments = list_attachments(session, current_user, trade_id)
    return [AttachmentRead.model_validate(a) for a in attachments]


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_attachment(
    attachment_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_attachment(session, current_user, attachment_id)
