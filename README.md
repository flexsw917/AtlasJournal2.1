# ZellaLite — Trade Journal MVP

ZellaLite is a full-stack trade journal that helps discretionary traders capture executions, annotate journal entries, and review performance with actionable metrics.

## Monorepo structure

```
apps/
  api/    # FastAPI + SQLModel backend
  web/    # Next.js 14 dashboard
packages/
  (optional shared packages)
```

## Getting started

1. **Install dependencies**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cd apps/web && npm install && cd ../..
   ```

2. **Bootstrap the database**
   ```bash
   cp .env.example .env
   make seed
   ```

3. **Run the stack**
   ```bash
   docker-compose up --build
   ```
   * API available at http://localhost:8000 (OpenAPI docs at `/docs`).
   * Web app available at http://localhost:3000.

4. **Run locally without Docker**
   ```bash
   # API (from repo root)
   uvicorn app.main:app --reload --app-dir apps/api/app --host 0.0.0.0 --port 8000

   # Web (in another terminal)
   cd apps/web
   npm run dev
   ```

## Testing

```bash
# Backend unit tests
pytest

# Frontend e2e tests (requires API + web running on :8000 and :3000)
cd apps/web
npx playwright install
npm run test
```

## Tooling

- `make seed` seeds a demo user (`demo@zellalite.com / DemoPass123`) and sample trade.
- `ruff` and `black` enforce backend code style; `eslint` covers the Next.js app.
- Pre-commit hooks are defined in `.pre-commit-config.yaml`.

## Key features

- Email/password authentication with JWT cookies.
- Trade CRUD with executions, notes, tags, attachments, and CSV import.
- Metrics endpoints for summary KPIs and equity curve.
- Responsive dashboard UI with trade filtering, journal editing, and import workflows.
