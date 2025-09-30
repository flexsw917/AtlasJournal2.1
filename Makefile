.PHONY: seed dev-api dev-web

seed:
python -m apps.api.app.seed

dev-api:
PYTHONPATH=apps uvicorn app.main:app --reload --app-dir apps/api/app --host 0.0.0.0 --port 8000

dev-web:
cd apps/web && npm run dev
