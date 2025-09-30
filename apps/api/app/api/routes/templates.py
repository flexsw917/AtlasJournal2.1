from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.services.trade_service import CSV_COLUMNS

router = APIRouter()


@router.get("/trades.csv", response_class=PlainTextResponse)
def download_template() -> str:
    header = ",".join(CSV_COLUMNS)
    example = "2024-01-02,13:30,AAPL,buy,10,150.25,1.5,1,First leg,Opening range"
    return f"{header}\n{example}\n"
