from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.api.deps import get_current_user, get_db
from app.models import JournalEntry, Trade, User
from app.schemas.journal import JournalCreate
from app.schemas.trade import JournalEntryRead
from app.services.trade_service import add_journal_entry, delete_journal_entry, get_trade

router = APIRouter()


@router.get("/trades/{trade_id}/journal", response_model=list[JournalEntryRead])
def list_journal(
    trade_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[JournalEntryRead]:
    trade = get_trade(session, current_user, trade_id)
    return [JournalEntryRead.model_validate(entry) for entry in trade.journal_entries]


@router.post("/trades/{trade_id}/journal", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
def create_journal_entry(
    trade_id: int,
    payload: JournalCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JournalEntryRead:
    entry = add_journal_entry(session, current_user, trade_id, payload.body)
    return JournalEntryRead.model_validate(entry)


@router.delete("/journal/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_journal_entry(
    entry_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_journal_entry(session, current_user, entry_id)
