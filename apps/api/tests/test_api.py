from datetime import datetime
from io import BytesIO

import pytest
from httpx import AsyncClient

from app.schemas.trade import ExecutionSide, TradeDirection


async def signup_and_login(
    client: AsyncClient, email: str = "user@example.com", password: str = "Password123"
) -> str:
    await client.post("/auth/signup", json={"email": email, "password": password})
    response = await client.post("/auth/login", json={"email": email, "password": password})
    response.raise_for_status()
    return response.json()["refresh_token"]

@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient) -> None:
    refresh_token = await signup_and_login(client)
    me = await client.get("/me")
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == "user@example.com"

    refresh = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 200

    logout = await client.post("/auth/logout")
    assert logout.status_code == 200


@pytest.mark.asyncio
async def test_trade_crud_and_filters(client: AsyncClient) -> None:
    await signup_and_login(client)
    trade_payload = {
        "instrument": {"symbol": "AAPL", "asset_type": "equity"},
        "direction": TradeDirection.long.value,
        "opened_at": datetime(2024, 1, 1, 14, 30).isoformat(),
        "closed_at": datetime(2024, 1, 1, 15, 30).isoformat(),
        "executions": [
            {
                "side": ExecutionSide.buy.value,
                "qty": 10,
                "price": 100,
                "timestamp": datetime(2024, 1, 1, 14, 30).isoformat(),
            },
            {
                "side": ExecutionSide.sell.value,
                "qty": 10,
                "price": 105,
                "timestamp": datetime(2024, 1, 1, 15, 30).isoformat(),
            },
        ],
        "fees": 2.0,
        "notes": "Test trade",
    }
    response = await client.post("/trades/", json=trade_payload)
    assert response.status_code == 201
    trade = response.json()
    assert trade["net_pl"] == pytest.approx(48.0)

    listing = await client.get("/trades/", params={"symbol": "AAPL"})
    assert listing.status_code == 200
    assert listing.json()["total"] == 1

    metrics = await client.get("/metrics/summary")
    assert metrics.status_code == 200


@pytest.mark.asyncio
async def test_csv_import_and_metrics(client: AsyncClient) -> None:
    await signup_and_login(client)
    csv_content = "date,time,symbol,side,qty,price,fees,trade_id,notes,strategy\n"
    csv_content += "2024-02-01,14:30,MSFT,buy,5,300,1,1,Entry,Strategy\n"
    csv_content += "2024-02-01,15:30,MSFT,sell,5,310,1,1,Exit,Strategy\n"
    file = BytesIO(csv_content.encode("utf-8"))
    files = {"file": ("import.csv", file, "text/csv")}

    dry_run = await client.post("/trades/import", files=files, params={"dry_run": "true"})
    assert dry_run.status_code == 200
    assert dry_run.json()["created"] == 1

    file.seek(0)
    files = {"file": ("import.csv", file, "text/csv")}
    result = await client.post("/trades/import", files=files, params={"dry_run": "false"})
    assert result.status_code == 200
    assert result.json()["created"] == 1

    equity = await client.get("/metrics/equity_curve")
    assert equity.status_code == 200
    assert len(equity.json()["points"]) >= 1
