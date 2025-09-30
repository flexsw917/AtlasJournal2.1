from datetime import date
from typing import List

from pydantic import BaseModel


class MetricsSummary(BaseModel):
    realized_pl: float
    win_rate: float
    expectancy: float
    profit_factor: float


class EquityPoint(BaseModel):
    date: date
    equity: float


class EquityCurveResponse(BaseModel):
    points: List[EquityPoint]
