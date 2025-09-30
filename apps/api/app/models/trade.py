import enum
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin


class AssetType(str, enum.Enum):
    equity = "equity"
    future = "future"
    crypto = "crypto"
    fx = "fx"


class TradeDirection(str, enum.Enum):
    long = "long"
    short = "short"


class TradeStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class ExecutionSide(str, enum.Enum):
    buy = "buy"
    sell = "sell"


class Instrument(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, unique=True, nullable=False)
    asset_type: AssetType = Field(default=AssetType.equity, nullable=False)

    trades: List["Trade"] = Relationship(back_populates="instrument")


class Trade(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    instrument_id: int = Field(foreign_key="instrument.id", nullable=False)
    direction: TradeDirection = Field(nullable=False)
    strategy: Optional[str] = None
    opened_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    closed_at: Optional[datetime] = None
    status: TradeStatus = Field(default=TradeStatus.open, nullable=False)
    net_pl: float = Field(default=0.0, nullable=False)
    fees: float = Field(default=0.0, nullable=False)
    notes: Optional[str] = None

    user: "User" = Relationship(back_populates="trades")
    instrument: Instrument = Relationship(back_populates="trades")
    executions: List["Execution"] = Relationship(back_populates="trade", sa_relationship_kwargs={"cascade": "all, delete"})
    journal_entries: List["JournalEntry"] = Relationship(back_populates="trade", sa_relationship_kwargs={"cascade": "all, delete"})
    attachments: List["Attachment"] = Relationship(back_populates="trade", sa_relationship_kwargs={"cascade": "all, delete"})
    trade_tags: List["TradeTag"] = Relationship(back_populates="trade", sa_relationship_kwargs={"cascade": "all, delete"})


class Execution(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trade_id: int = Field(foreign_key="trade.id", nullable=False)
    side: ExecutionSide = Field(nullable=False)
    qty: float = Field(nullable=False)
    price: float = Field(nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    trade: Trade = Relationship(back_populates="executions")


class JournalEntry(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trade_id: int = Field(foreign_key="trade.id", nullable=False)
    body: str = Field(nullable=False)

    trade: Trade = Relationship(back_populates="journal_entries")


class Tag(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    name: str = Field(nullable=False, index=True)

    user: "User" = Relationship(back_populates="tags")
    trade_tags: List["TradeTag"] = Relationship(back_populates="tag", sa_relationship_kwargs={"cascade": "all, delete"})


class TradeTag(SQLModel, table=True):
    trade_id: int = Field(foreign_key="trade.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)

    trade: Trade = Relationship(back_populates="trade_tags")
    tag: Tag = Relationship(back_populates="trade_tags")


class Attachment(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trade_id: int = Field(foreign_key="trade.id", nullable=False)
    filename: str = Field(nullable=False)
    content_type: str = Field(nullable=False)
    path: str = Field(nullable=False)
    size: int = Field(nullable=False)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    trade: Trade = Relationship(back_populates="attachments")


class MetricSnapshot(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    date: datetime = Field(nullable=False)
    realized_pl: float = Field(default=0.0, nullable=False)
    cumulative_pl: float = Field(default=0.0, nullable=False)
    win_rate: float = Field(default=0.0, nullable=False)
    profit_factor: float = Field(default=0.0, nullable=False)
    expectancy: float = Field(default=0.0, nullable=False)

    user: "User" = Relationship(back_populates="metric_snapshots")
