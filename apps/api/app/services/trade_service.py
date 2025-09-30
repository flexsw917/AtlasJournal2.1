from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO
from typing import Iterable, List, Sequence

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.models import (
    Attachment,
    Execution,
    ExecutionSide,
    Instrument,
    JournalEntry,
    Tag,
    Trade,
    TradeDirection,
    TradeStatus,
    TradeTag,
    User,
)
from app.schemas.trade import ExecutionCreate, InstrumentRef, TradeCreate, TradeUpdate


def _get_or_create_instrument(session: Session, symbol: str) -> Instrument:
    instrument = session.exec(select(Instrument).where(Instrument.symbol == symbol)).first()
    if instrument:
        return instrument
    instrument = Instrument(symbol=symbol)
    session.add(instrument)
    session.commit()
    session.refresh(instrument)
    return instrument


def _compute_trade_status(trade: Trade) -> TradeStatus:
    qty = 0.0
    for exec in trade.executions:
        qty += exec.qty if exec.side == ExecutionSide.buy else -exec.qty
    return TradeStatus.closed if abs(qty) < 1e-6 else TradeStatus.open


def _compute_net_pl(trade: Trade) -> float:
    buys = sum(exec.qty * exec.price for exec in trade.executions if exec.side == ExecutionSide.buy)
    sells = sum(exec.qty * exec.price for exec in trade.executions if exec.side == ExecutionSide.sell)
    return sells - buys - trade.fees


def create_trade(session: Session, user: User, payload: TradeCreate, *, commit: bool = True) -> Trade:
    instrument = _get_or_create_instrument(session, payload.instrument.symbol.upper())
    trade = Trade(
        user_id=user.id,
        instrument_id=instrument.id,
        direction=payload.direction,
        strategy=payload.strategy,
        opened_at=payload.opened_at,
        closed_at=payload.closed_at,
        status=payload.status,
        fees=payload.fees,
        notes=payload.notes,
    )
    session.add(trade)
    session.flush()

    executions: List[Execution] = []
    for execution_data in payload.executions:
        execution = Execution(
            trade_id=trade.id,
            side=execution_data.side,
            qty=execution_data.qty,
            price=execution_data.price,
            timestamp=execution_data.timestamp,
        )
        executions.append(execution)
        session.add(execution)

    session.flush()
    session.refresh(trade)
    trade.status = _compute_trade_status(trade)
    trade.net_pl = _compute_net_pl(trade)
    session.add(trade)
    if commit:
        session.commit()
    else:
        session.flush()
    session.refresh(
        trade,
        attribute_names=[
            "instrument",
            "executions",
            "journal_entries",
            "attachments",
            "trade_tags",
        ],
    )
    return trade


def list_trades(
    session: Session,
    user: User,
    *,
    symbol: str | None = None,
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    tags: Sequence[int] | None = None,
    status_filter: TradeStatus | None = None,
    strategy: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[List[Trade], int]:
    base_query = select(Trade).where(Trade.user_id == user.id)
    if symbol:
        base_query = base_query.join(Instrument).where(func.lower(Instrument.symbol) == symbol.lower())
    if from_dt:
        base_query = base_query.where(Trade.opened_at >= from_dt)
    if to_dt:
        base_query = base_query.where(Trade.opened_at <= to_dt)
    if status_filter:
        base_query = base_query.where(Trade.status == status_filter)
    if strategy:
        base_query = base_query.where(Trade.strategy == strategy)
    if tags:
        base_query = base_query.join(TradeTag).where(TradeTag.tag_id.in_(tags))

    total_query = base_query.with_only_columns(Trade.id).distinct().subquery()
    total = session.exec(select(func.count()).select_from(total_query)).one()

    query = base_query.order_by(Trade.opened_at.desc())
    items = (
        session.exec(query.offset((page - 1) * page_size).limit(page_size))
        .unique()
        .all()
    )
    return items, total


def get_trade(session: Session, user: User, trade_id: int) -> Trade:
    trade = session.get(Trade, trade_id)
    if not trade or trade.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trade not found")
    session.refresh(
        trade,
        attribute_names=[
            "instrument",
            "executions",
            "journal_entries",
            "attachments",
            "trade_tags",
        ],
    )
    return trade


def update_trade(session: Session, user: User, trade_id: int, payload: TradeUpdate) -> Trade:
    trade = get_trade(session, user, trade_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(trade, key, value)
    session.add(trade)
    session.commit()
    session.refresh(
        trade,
        attribute_names=[
            "instrument",
            "executions",
            "journal_entries",
            "attachments",
            "trade_tags",
        ],
    )
    return trade


def delete_trade(session: Session, user: User, trade_id: int) -> None:
    trade = get_trade(session, user, trade_id)
    session.delete(trade)
    session.commit()


def ensure_tags(session: Session, user: User, tag_ids: Iterable[int]) -> List[Tag]:
    tags = session.exec(select(Tag).where(Tag.user_id == user.id, Tag.id.in_(list(tag_ids)))).all()
    missing = set(tag_ids) - {tag.id for tag in tags}
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown tag ids: {missing}")
    return tags


def assign_tags(session: Session, user: User, trade_id: int, tag_ids: Iterable[int]) -> Trade:
    trade = get_trade(session, user, trade_id)
    tags = ensure_tags(session, user, tag_ids)
    trade.trade_tags = [TradeTag(trade_id=trade.id, tag_id=tag.id, tag=tag) for tag in tags]
    session.add(trade)
    session.commit()
    session.refresh(
        trade,
        attribute_names=[
            "instrument",
            "executions",
            "journal_entries",
            "attachments",
            "trade_tags",
        ],
    )
    return trade


def remove_tag(session: Session, user: User, trade_id: int, tag_id: int) -> Trade:
    trade = get_trade(session, user, trade_id)
    trade.trade_tags = [tt for tt in trade.trade_tags if tt.tag_id != tag_id]
    session.add(trade)
    session.commit()
    session.refresh(
        trade,
        attribute_names=[
            "instrument",
            "executions",
            "journal_entries",
            "attachments",
            "trade_tags",
        ],
    )
    return trade


def add_journal_entry(session: Session, user: User, trade_id: int, body: str) -> JournalEntry:
    trade = get_trade(session, user, trade_id)
    entry = JournalEntry(trade_id=trade.id, body=body)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def delete_journal_entry(session: Session, user: User, entry_id: int) -> None:
    entry = session.get(JournalEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    trade = session.get(Trade, entry.trade_id)
    if not trade or trade.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    session.delete(entry)
    session.commit()


def create_tag(session: Session, user: User, name: str) -> Tag:
    existing = session.exec(
        select(Tag).where(Tag.user_id == user.id, func.lower(Tag.name) == name.lower())
    ).first()
    if existing:
        return existing
    tag = Tag(user_id=user.id, name=name)
    session.add(tag)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag exists") from exc
    session.refresh(tag)
    return tag


def list_tags(session: Session, user: User) -> List[Tag]:
    return session.exec(select(Tag).where(Tag.user_id == user.id).order_by(Tag.name)).all()


def save_attachment(session: Session, user: User, trade_id: int, upload: UploadFile, upload_dir: str) -> Attachment:
    trade = get_trade(session, user, trade_id)
    contents = upload.file.read()
    size = len(contents)
    if size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    path = f"{trade.id}_{int(datetime.utcnow().timestamp())}_{upload.filename}"
    file_path = f"{upload_dir}/{path}"
    with open(file_path, "wb") as f:
        f.write(contents)
    attachment = Attachment(
        trade_id=trade.id,
        filename=upload.filename,
        content_type=upload.content_type or "application/octet-stream",
        path=file_path,
        size=size,
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment


def delete_attachment(session: Session, user: User, attachment_id: int) -> None:
    attachment = session.get(Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    trade = session.get(Trade, attachment.trade_id)
    if not trade or trade.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    session.delete(attachment)
    session.commit()


def list_attachments(session: Session, user: User, trade_id: int) -> List[Attachment]:
    trade = get_trade(session, user, trade_id)
    session.refresh(trade, attribute_names=["attachments"])
    return trade.attachments


CSV_COLUMNS = [
    "date",
    "time",
    "symbol",
    "side",
    "qty",
    "price",
    "fees",
    "trade_id",
    "notes",
    "strategy",
]


class ImportReport:
    def __init__(self) -> None:
        self.created: int = 0
        self.errors: List[str] = []
        self.trades: List[int] = []

    def as_dict(self) -> dict[str, object]:
        return {"created": self.created, "errors": self.errors, "trade_ids": self.trades}


def parse_csv(file: UploadFile) -> List[dict[str, str]]:
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    missing = [col for col in CSV_COLUMNS if col not in reader.fieldnames]
    if missing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing columns: {missing}")
    rows: List[dict[str, str]] = []
    for idx, row in enumerate(reader, start=2):
        if not row.get("date"):
            continue
        rows.append(row)
    return rows


def import_trades(session: Session, user: User, file: UploadFile, dry_run: bool) -> dict[str, object]:
    rows = parse_csv(file)
    report = ImportReport()
    trades_by_key: dict[str, List[dict[str, str]]] = {}
    for row in rows:
        trade_key = row.get("trade_id") or f"{row['symbol']}-{row['date']}"
        trades_by_key.setdefault(trade_key, []).append(row)

    for key, trade_rows in trades_by_key.items():
        try:
            executions = []
            for row in trade_rows:
                timestamp_str = f"{row['date']} {row['time']}"
                timestamp = datetime.fromisoformat(timestamp_str)
                executions.append(
                    ExecutionCreate(
                        side=ExecutionSide(row["side"].lower()),
                        qty=float(row["qty"]),
                        price=float(row["price"]),
                        timestamp=timestamp,
                    )
                )
            instrument_symbol = trade_rows[0]["symbol"].upper()
            instrument = _get_or_create_instrument(session, instrument_symbol)
            trade_payload = TradeCreate(
                instrument=InstrumentRef(symbol=instrument.symbol, asset_type=instrument.asset_type),
                direction=TradeDirection.long,
                opened_at=executions[0].timestamp,
                closed_at=executions[-1].timestamp,
                status=TradeStatus.open,
                strategy=trade_rows[0].get("strategy"),
                notes=trade_rows[0].get("notes"),
                fees=float(trade_rows[0].get("fees") or 0),
                executions=executions,
            )
            if dry_run:
                create_trade(session, user, trade_payload, commit=False)
                report.created += 1
                session.rollback()
            else:
                trade = create_trade(session, user, trade_payload)
                report.created += 1
                report.trades.append(trade.id)
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            report.errors.append(f"Trade {key}: {exc}")
    return report.as_dict()


def metrics_summary(session: Session, user: User, start: datetime | None, end: datetime | None) -> dict[str, float]:
    query = select(Trade).where(Trade.user_id == user.id, Trade.status == TradeStatus.closed)
    if start:
        query = query.where(Trade.closed_at >= start)
    if end:
        query = query.where(Trade.closed_at <= end)
    trades = session.exec(query).all()
    realized = sum(trade.net_pl for trade in trades)
    wins = [trade.net_pl for trade in trades if trade.net_pl > 0]
    losses = [trade.net_pl for trade in trades if trade.net_pl < 0]
    total = len(trades)
    win_rate = len(wins) / total if total else 0.0
    expectancy = realized / total if total else 0.0
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss else (gross_profit if gross_profit else 0.0)
    return {
        "realized_pl": round(realized, 2),
        "win_rate": round(win_rate, 4),
        "expectancy": round(expectancy, 2),
        "profit_factor": round(profit_factor, 4),
    }


def equity_curve(session: Session, user: User, start: datetime | None, end: datetime | None) -> List[dict[str, object]]:
    query = select(Trade).where(Trade.user_id == user.id, Trade.status == TradeStatus.closed)
    if start:
        query = query.where(Trade.closed_at >= start)
    if end:
        query = query.where(Trade.closed_at <= end)
    trades = session.exec(query).all()
    sorted_trades = sorted(trades, key=lambda t: t.closed_at or t.opened_at)
    equity = 0.0
    points: List[dict[str, object]] = []
    for trade in sorted_trades:
        equity += trade.net_pl
        points.append({"date": (trade.closed_at or trade.opened_at).date(), "equity": round(equity, 2)})
    return points
