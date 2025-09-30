from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user, get_db
from app.models import User
from app.schemas.tag import TagCreate, TagRead
from app.services.trade_service import create_tag, list_tags

router = APIRouter()


@router.get("/", response_model=list[TagRead])
def get_tags(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TagRead]:
    tags = list_tags(session, current_user)
    return [TagRead.model_validate(tag) for tag in tags]


@router.post("/", response_model=TagRead, status_code=201)
def create_tag_route(
    payload: TagCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TagRead:
    tag = create_tag(session, current_user, payload.name)
    return TagRead.model_validate(tag)
