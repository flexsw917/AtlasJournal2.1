from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from app.models import AssetType, ExecutionSide, TradeDirection, TradeStatus


class InstrumentRef(BaseModel):
    symbol: str
    asset_type: AssetType = AssetType.equity


class ExecutionCreate(BaseModel):
    side: ExecutionSide
    qty: float = Field(gt=0)
    price: float = Field(gt=0)
    timestamp: datetime


class ExecutionRead(ExecutionCreate):
    id: int

    class Config:
        from_attributes = True


class TradeBase(BaseModel):
    direction: TradeDirection
    strategy: Optional[str] = None
    opened_at: datetime
    closed_at: Optional[datetime] = None
    status: TradeStatus = TradeStatus.open
    fees: float = 0.0
    notes: Optional[str] = None


class TradeCreate(TradeBase):
    instrument: InstrumentRef
    executions: List[ExecutionCreate]
    dry_run: bool = False


class TradeUpdate(BaseModel):
    strategy: Optional[str] = None
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    status: Optional[TradeStatus] = None
    fees: Optional[float] = None
    notes: Optional[str] = None


class TagRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class AttachmentRead(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class JournalEntryRead(BaseModel):
    id: int
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class TradeRead(BaseModel):
    id: int
    direction: TradeDirection
    strategy: Optional[str]
    opened_at: datetime
    closed_at: Optional[datetime]
    status: TradeStatus
    net_pl: float
    fees: float
    notes: Optional[str]
    created_at: datetime
    instrument: InstrumentRef
    executions: List[ExecutionRead]
    tags: List[TagRead]
    journal_entries: List[JournalEntryRead]
    attachments: List[AttachmentRead]

    class Config:
        from_attributes = True


class TradeListResponse(BaseModel):
    items: List[TradeRead]
    total: int
