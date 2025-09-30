from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import TimestampMixin


class User(TimestampMixin, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)

    trades: List["Trade"] = Relationship(back_populates="user")
    tags: List["Tag"] = Relationship(back_populates="user")
    metric_snapshots: List["MetricSnapshot"] = Relationship(back_populates="user")
