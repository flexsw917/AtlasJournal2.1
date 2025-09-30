from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.deps import get_current_user, get_db
from app.schemas.metrics import EquityCurveResponse, MetricsSummary
from app.services.trade_service import equity_curve, metrics_summary
from app.models import User

router = APIRouter()


@router.get("/summary", response_model=MetricsSummary)
def metrics_summary_route(
    from_: datetime | None = None,
    to: datetime | None = None,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MetricsSummary:
    data = metrics_summary(session, current_user, from_, to)
    return MetricsSummary(**data)


@router.get("/equity_curve", response_model=EquityCurveResponse)
def equity_curve_route(
    from_: datetime | None = None,
    to: datetime | None = None,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EquityCurveResponse:
    points = equity_curve(session, current_user, from_, to)
    return EquityCurveResponse(points=points)
