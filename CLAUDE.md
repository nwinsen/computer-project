# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack League of Legends stats/analytics application:
- **Frontend**: Next.js 14 + React 18 (TypeScript) with Material-UI, Emotion styling, React Query
- **Backend**: FastAPI + SQLAlchemy/SQLModel with PostgreSQL
- **Authentication**: JWT-based with access/refresh tokens
- **Database**: PostgreSQL with Alembic for migrations

## Development Setup

### Prerequisites
- Node.js/npm (for frontend)
- Python 3.10+ with virtual environment (for backend)
- PostgreSQL database running locally

### Frontend Setup
```bash
cd frontend
npm install
npm run dev           # Start development server (http://localhost:3000)
npm run build         # Production build
npm run lint          # Run ESLint
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables in .env:
# POSTGRES_STRING=postgresql://user:password@localhost/dbname
# SECRET_ACCESS_KEY=your_secret_key
# SECRET_REFRESH_KEY=your_refresh_key
# API_KEY=riot_api_key_if_needed
# ALEMBIC_PATH=./alembic

# Run migrations
alembic upgrade head

# Start server (uses uvicorn)
python -m uvicorn app.main:app --reload
```

## Project Structure

### Backend (`backend/app/`)
- **`main.py`**: FastAPI application initialization with CORS middleware
- **`api/`**: API router organization
  - `api.py`: Main router combining all endpoints
  - `endpoints/auth.py`: Authentication endpoints (login, register, token refresh)
  - `endpoints/riot.py`: Riot API integration endpoints
- **`models/`**: SQLModel database models (user, player, game, champion, stats, token)
- **`schemas/`**: Pydantic schemas for request/response validation
- **`crud/`**: CRUD operations (currently user CRUD)
- **`db/`**: Database connection management (`session.py` exports `SessionDep` for FastAPI dependency injection)
- **`config/`**: Configuration (environment variables via `vars.py`)
- **`services/`**: Business logic layer
- **`utils/`**: Utilities (e.g., `crypt.py` for password hashing)

### Frontend (`frontend/app/`)
- **App Router structure** (Next.js 13+ app directory)
- **`(api)/`**: API integration utilities
  - `riot/`: Riot API client code
  - `auth.ts`: Authentication utilities
- **`providers/authProvider.tsx`**: Context provider for auth state
- **Route segments**:
  - `/`: Home page
  - `/login`: Login page
  - `/register`: Registration page
  - `/protected`: Protected route example
  - `/champions`: Champions listing
  - `/players/[username]/[tag]`: Dynamic player profile page

### Database Migrations
- Alembic configuration in `backend/alembic.ini`
- Migration scripts in `backend/alembic/versions/`
- **Key commands**:
  ```bash
  alembic revision --autogenerate -m "description"  # Create migration
  alembic upgrade head                               # Apply migrations
  alembic downgrade -1                               # Rollback one migration
  ```

## Key Architecture Patterns

### API Design
- Endpoints prefixed with `/api` (see `backend/app/api/api.py`)
- Routers tagged by functionality (Riot, Auth)
- CORS middleware configured to allow requests from `http://localhost:3000`

### Authentication Flow
- JWT tokens with separate access/refresh token secrets
- Tokens configured with 2-minute access and 1-day refresh expiry (in `config/vars.py`)
- Token validation handled by auth endpoints

### Database Access
- **SessionDep**: FastAPI dependency for database sessions (from `db/session.py`)
- Use `SessionDep` as function parameter in endpoints for automatic session injection
- SQLModel for ORM (hybrid SQLAlchemy + Pydantic)
- Alembic-managed migrations (not auto-create tables)

### Frontend State Management
- React Query (`@tanstack/react-query`) for server state
- Context API for authentication state (`authProvider`)
- Axios for HTTP requests

## Configuration & Environment

Backend environment variables (required in `.env`):
- `POSTGRES_STRING`: Database connection string
- `SECRET_ACCESS_KEY`: JWT access token signing key
- `SECRET_REFRESH_KEY`: JWT refresh token signing key
- `API_KEY`: Riot API key (if needed)
- `ALEMBIC_PATH`: Path to alembic migrations

Token expiry times are hardcoded in `backend/app/config/vars.py`:
- Access tokens: 120 seconds
- Refresh tokens: 86400 seconds (1 day)

## Common Development Tasks

### Running both frontend and backend
```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Database workflow
```bash
# After changing models, auto-generate migration
alembic revision --autogenerate -m "add_new_field_to_user"

# Apply migration
alembic upgrade head

# If migration fails, inspect and edit backend/alembic/versions/xxx_*.py
```

### API Testing
- FastAPI auto-generates OpenAPI docs at `http://localhost:8000/docs`
- Use Swagger UI for testing endpoints with authentication headers

## Notes

- PYTHONPATH issue documented in `backend/README.md`: custom virtual environment `.pth` file may be needed if imports fail
- Password hashing uses bcrypt (`backend/app/utils/crypt.py`)
- Frontend uses Material-UI 6.x and Emotion for styling
- Alembic startup sometimes freezes (see `backend/README.md`)
