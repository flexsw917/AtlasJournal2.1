from datetime import datetime, timedelta

from sqlmodel import Session

from app.core.security import hash_password
from app.db.session import engine, init_db
from app.models import Execution, ExecutionSide, Instrument, Tag, Trade, TradeDirection, TradeStatus, User


def seed() -> None:
    init_db()
    with Session(engine) as session:
        user = session.query(User).filter(User.email == "demo@zellalite.com").first()
        if not user:
            user = User(email="demo@zellalite.com", password_hash=hash_password("DemoPass123"))
            session.add(user)
            session.commit()
            session.refresh(user)

        instrument = session.query(Instrument).filter(Instrument.symbol == "AAPL").first()
        if not instrument:
            instrument = Instrument(symbol="AAPL")
            session.add(instrument)
            session.commit()
            session.refresh(instrument)

        trade = session.query(Trade).filter(Trade.user_id == user.id).first()
        if not trade:
            trade = Trade(
                user_id=user.id,
                instrument_id=instrument.id,
                direction=TradeDirection.long,
                strategy="Breakout",
                opened_at=datetime.utcnow() - timedelta(days=5),
                closed_at=datetime.utcnow() - timedelta(days=4, hours=22),
                status=TradeStatus.closed,
                fees=4.5,
                notes="Seed trade",
            )
            session.add(trade)
            session.flush()
            entry = Execution(
                trade_id=trade.id,
                side=ExecutionSide.buy,
                qty=10,
                price=100.0,
                timestamp=trade.opened_at,
            )
            exit_exec = Execution(
                trade_id=trade.id,
                side=ExecutionSide.sell,
                qty=10,
                price=110.0,
                timestamp=trade.closed_at,
            )
            session.add(entry)
            session.add(exit_exec)
            session.flush()
            trade.net_pl = (exit_exec.qty * exit_exec.price) - (entry.qty * entry.price) - trade.fees
            session.add(trade)

        if not session.query(Tag).filter(Tag.user_id == user.id, Tag.name == "Momentum").first():
            session.add(Tag(user_id=user.id, name="Momentum"))

        session.commit()


if __name__ == "__main__":
    seed()
