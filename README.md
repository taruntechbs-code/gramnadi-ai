# GramNadi AI

GramNadi AI is an AI-powered Rural Enterprise Resilience Platform designed to help rural micro enterprises understand cash-flow risk and respond proactively. This repository currently contains **Phase 0: the production-oriented project foundation**. Product workflows, domain models, prediction models, dashboards, and business APIs are intentionally not implemented yet.

## Architecture

The repository is a modular monorepo:

- `frontend/` is a React + TypeScript single-page application built with Vite.
- `backend/` is a FastAPI service with versioned API routing, settings management, SQLAlchemy 2.x database plumbing, and Alembic configuration.
- `ml/` is reserved for future model development and inference components.
- `datasets/` is reserved for future data ingestion and processing artifacts.
- `docs/` contains product and technical documentation as it is added.
- `docker/` contains shared container-related assets.
- `scripts/` contains repository automation scripts.

The frontend communicates with the backend through an Axios client. TanStack Query is configured at the application boundary for future server-state workflows. The backend now includes a versioned persistence API for the domain entities, while prediction-related records remain storage-only and do not perform ML inference.

## Tech stack

Frontend: React, TypeScript, Vite, TailwindCSS, React Router, Axios, TanStack Query, ESLint, and Prettier.

Backend: Python 3.12, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.x, Alembic, and Psycopg 3.

Infrastructure: PostgreSQL, Docker, Docker Compose, and GitHub Actions.

## Repository structure

```text
gramnadi-ai/
├── backend/
│   ├── alembic/
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/
│   │   ├── db/
│   │   ├── dependencies/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/{common,layout}/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── types/
│   │   └── utils/
│   └── package.json
├── ml/
├── datasets/
├── docs/
├── docker/
├── scripts/
├── .github/workflows/
├── docker-compose.yml
└── README.md
```

## Installation

### Prerequisites

- Node.js 20.19+ (or 22+)
- Python 3.12+
- PostgreSQL 16+ for a native setup, or Docker Desktop for the containerized setup

Copy the example environment file before running services:

```bash
cp .env.example .env
```

### Run the frontend locally

```bash
cd frontend
npm install
npm run dev
```

The Vite development server runs at `http://localhost:5173`.

### Run the backend locally

From the repository root:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. OpenAPI documentation is available at `/docs`.

### Domain API and migrations

The backend exposes CRUD endpoints under `/api/v1/` for enterprises, financial records, loans, commodity prices, weather snapshots, predictions, prediction explanations, interventions, counterfactual simulations, village graph nodes, and village graph edges. DELETE operations use soft deletion.

Apply the initial schema migration from `backend/` with:

```bash
alembic upgrade head
```

The initial migration creates UUID primary keys, timestamps, soft-delete columns, relational foreign keys, enum types, indexes, uniqueness constraints, and numeric validation constraints.

### Backend quality checks

Run these from `backend/` with the virtual environment active:

```bash
black --check app alembic
isort --check-only app alembic
flake8 app alembic
```

Alembic is configured but has no migrations or tables yet:

```bash
alembic current
```

## Docker setup

Docker Compose starts the frontend, backend, and PostgreSQL services:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Backend health: `http://localhost:8000/api/v1/health`
- PostgreSQL: `localhost:5432`

Stop the services with `docker compose down`. Persistent PostgreSQL data is stored in the named `postgres_data` volume.

## Future roadmap

1. Establish the domain and bounded contexts for rural enterprise resilience.
2. Add authentication and authorization with explicit security boundaries.
3. Introduce the first versioned database migration and repository abstractions.
4. Add validated enterprise, cash-flow, risk, and intervention workflows.
5. Build data ingestion and ML training/inference pipelines under `ml/`.
6. Add explainable predictions, monitoring, and production observability.
7. Expand the frontend from placeholder routes into accessible product workflows.

## Development principles

The codebase follows modular boundaries, dependency inversion where useful, typed contracts, environment-based configuration, small composable modules, and automated quality checks. No production secrets, business data, mock data, or domain assumptions belong in the Phase 0 foundation.
