# AGENTS.md

## Project

家庭记账系统 (Family Finance Tracker) — B/S web app for household expense tracking.
Full spec: `readme.html` (technical design document v1.0, in Chinese).

## Tech Stack

**Backend**: Python 3.11+ / FastAPI 0.110+ / SQLAlchemy 2.0+ (async) / Alembic / PostgreSQL 15+ / Redis 7+
**Frontend**: Vue 3.4+ / TypeScript 5.3+ / Vite 5+ / Element Plus 2.5+ / Pinia 2.1+ / Axios / ECharts 5.5+
**Infra**: Docker Compose / Nginx (static + API proxy) / Let's Encrypt SSL

## Directory Layout

```
backend/          # FastAPI app (entrypoint: app/main.py, uvicorn)
  app/
    models/       # SQLAlchemy ORM models (UUID PKs, TIMESTAMPTZ timestamps)
    schemas/      # Pydantic request/response models
    routers/      # API route handlers (prefix /api/v1/)
    services/     # Business logic layer
    utils/        # Pagination, file upload, CSV handlers
  alembic/        # DB migration scripts (alembic upgrade head)
frontend/         # Vue 3 SPA (entrypoint: src/main.ts)
  src/
    api/          # Axios wrappers per module (do NOT call axios directly in components)
    stores/       # Pinia stores (auth, family, category, app)
    views/        # Page components
    components/   # Reusable components
    composables/  # Vue composables
    types/        # TypeScript interfaces for API responses
nginx/nginx.conf  # Proxies /api/* → backend:8000, serves frontend dist
```

## Commands

```bash
# Backend
cd backend && pip install -r requirements.txt
alembic upgrade head                    # Run migrations
uvicorn app.main:app --reload           # Dev server
black .                                 # Format
ruff check .                            # Lint
pytest                                  # Test (pytest-asyncio for async tests)

# Frontend
cd frontend && npm ci                   # Install deps
npm run dev                             # Dev server (Vite)
npm run build                           # Production build → dist/
npx eslint . --ext .vue,.ts,.tsx        # Lint
npx prettier --check .                  # Format check

# Full stack
docker-compose up -d                    # Start all services (db, redis, backend, frontend, nginx)
```

## Architecture Notes

- **API base path**: All endpoints under `/api/v1/` (e.g. `/api/v1/auth/login`, `/api/v1/transactions`)
- **Auth**: JWT access_token (30min) + refresh_token (7d). Access token in `Authorization: Bearer` header. Refresh token stored as SHA256 hash in DB.
- **Data isolation**: Every query filters by `family_id` — injected via FastAPI `Depends(get_current_family_id)`. Never query across families.
- **Soft delete**: `transactions` uses `is_deleted` boolean — never physically delete transaction rows.
- **Registration side effects**: Creating a user auto-creates a family + copies system default categories (where `family_id=NULL, is_system=TRUE`) into the new family.
- **Response format**: All API responses use `{ "code": 0, "message": "success", "data": ... }`. Business error codes: 4xxxx (40001-50001). Lists include pagination: `{ items, total, page, page_size, total_pages }`.
- **Docker entrypoint**: Backend container runs `alembic upgrade head` before `uvicorn` — migrations must be ready before deploy.

## Database Conventions

- All tables: UUID PK (`gen_random_uuid()`), `created_at`, `updated_at` (TIMESTAMPTZ)
- Amounts: `DECIMAL(12,2)`, always positive
- Table names: plural (`users`, `transactions`). Column names: `snake_case`
- Schema changes: Alembic migrations only — never modify DB manually
- 10 tables: users, families, family_members, categories, sub_categories, transactions, budgets, payment_methods, fund_sources, refresh_tokens, operation_logs

## Frontend Conventions

- Vue 3 Composition API with `<script setup>` exclusively
- Component files: PascalCase (`TransactionForm.vue`), matching component name
- Each API module gets its own file in `src/api/` — never call axios from views directly
- Axios interceptors handle token injection + 401 auto-refresh (see readme.html §8.3)
- Mobile-first: core transaction form targets 375px width. Breakpoints: <768 (mobile), 768-1024 (tablet), >1024 (desktop)

## Backend Conventions

- Layer pattern: Router → Service → Model. Routers contain no business logic.
- All functions must have type annotations. Pydantic models are the interface contract.
- Custom `HTTPException` subclasses with business error codes (see readme.html §6.3)
- Structured JSON logging via Python `logging`

## Git

- Commit format: `type(scope): message` (e.g. `feat(transaction): add batch import`)
- Branches: `main` (production) → `develop` → `feature/*`
- `.gitignore` must include: `.env`, `uploads/`, `node_modules/`, `__pycache__/`, `dist/`
