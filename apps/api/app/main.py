from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, metrics, tags, trades, users, attachments, journal, templates
from app.core.config import settings
from app.db.session import init_db

init_db()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(trades.router, prefix="/trades", tags=["trades"])
app.include_router(journal.router, tags=["journal"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(attachments.router, tags=["attachments"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(templates.router, prefix="/templates", tags=["templates"])
