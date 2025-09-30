from datetime import datetime
from typing import List, Sequence

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlmodel import Session

from app.api.deps import get_current_user, get_db
from app.models import Trade, TradeStatus, User
from app.schemas.tag import AssignTagsRequest
from app.schemas.trade import TradeCreate, TradeListResponse, TradeRead, TradeUpdate
from app.services import trade_service

router = APIRouter()


def _serialize_trade(trade: Trade) -> TradeRead:
    return TradeRead.model_validate(
        {
            "id": trade.id,
            "direction": trade.direction,
            "strategy": trade.strategy,
            "opened_at": trade.opened_at,
            "closed_at": trade.closed_at,
            "status": trade.status,
            "net_pl": trade.net_pl,
            "fees": trade.fees,
            "notes": trade.notes,
            "created_at": trade.created_at,
            "instrument": {
                "symbol": trade.instrument.symbol,
                "asset_type": trade.instrument.asset_type,
            },
            "executions": [
                {
                    "id": execution.id,
                    "side": execution.side,
                    "qty": execution.qty,
                    "price": execution.price,
                    "timestamp": execution.timestamp,
                }
                for execution in trade.executions
            ],
            "tags": [
                {"id": tt.tag.id, "name": tt.tag.name}
                for tt in trade.trade_tags
                if tt.tag is not None
            ],
            "journal_entries": [
                {"id": entry.id, "body": entry.body, "created_at": entry.created_at}
                for entry in trade.journal_entries
            ],
            "attachments": [
                {
                    "id": attachment.id,
                    "filename": attachment.filename,
                    "content_type": attachment.content_type,
                    "size": attachment.size,
                    "uploaded_at": attachment.uploaded_at,
                }
                for attachment in trade.attachments
            ],
        }
    )


@router.get("/", response_model=TradeListResponse)
def list_trades(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    symbol: str | None = None,
    from_: datetime | None = None,
    to: datetime | None = None,
    tags: Sequence[int] | None = None,
    status: TradeStatus | None = None,
    strategy: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TradeListResponse:
    trades, total = trade_service.list_trades(
        session,
        current_user,
        symbol=symbol,
        from_dt=from_,
        to_dt=to,
        tags=tags,
        status_filter=status,
        strategy=strategy,
        page=page,
        page_size=page_size,
    )
    return TradeListResponse(items=[_serialize_trade(trade) for trade in trades], total=total)


@router.post("/", response_model=TradeRead, status_code=status.HTTP_201_CREATED)
def create_trade(
    payload: TradeCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TradeRead:
    if payload.dry_run:
        trade = trade_service.create_trade(session, current_user, payload)
        session.rollback()
        return _serialize_trade(trade)
    trade = trade_service.create_trade(session, current_user, payload)
    return _serialize_trade(trade)


@router.get("/{trade_id}", response_model=TradeRead)
def get_trade(
    trade_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TradeRead:
    trade = trade_service.get_trade(session, current_user, trade_id)
    return _serialize_trade(trade)


@router.patch("/{trade_id}", response_model=TradeRead)
def update_trade(
    trade_id: int,
    payload: TradeUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TradeRead:
    trade = trade_service.update_trade(session, current_user, trade_id, payload)
    return _serialize_trade(trade)


@router.delete("/{trade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trade(
    trade_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    trade_service.delete_trade(session, current_user, trade_id)


@router.post("/{trade_id}/tags", response_model=TradeRead)
def set_trade_tags(
    trade_id: int,
    payload: AssignTagsRequest,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TradeRead:
    trade = trade_service.assign_tags(session, current_user, trade_id, payload.tag_ids)
    return _serialize_trade(trade)


@router.delete("/{trade_id}/tags/{tag_id}", response_model=TradeRead)
def remove_trade_tag(
    trade_id: int,
    tag_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TradeRead:
    trade = trade_service.remove_tag(session, current_user, trade_id, tag_id)
    return _serialize_trade(trade)


@router.post("/import")
def import_trades(
    *,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    dry_run: bool = True,
) -> dict[str, object]:
    return trade_service.import_trades(session, current_user, file, dry_run)
