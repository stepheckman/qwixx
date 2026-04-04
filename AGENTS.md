# Repository Guidelines

## Project Structure & Module Organization
- `backend/` contains the FastAPI service. Core game logic lives in `backend/app/core/`, API routes live in `backend/app/api/`, and tests live in `backend/tests/`.
- `frontend/` contains the React (Vite) app. UI and API client code live under `frontend/src/`.
- `logs/` is mounted into the backend container for runtime logs.

## Build, Test, and Development Commands
- `just docker-up`: Start backend and frontend services with Docker Compose.
- `just docker-down`: Stop the running services.
- `just docker-build`: Rebuild Docker images for both services.
- `just test-backend`: Run backend tests in the backend container with `pytest`.
- `docker compose up -d`: Docker-only alternative to `just docker-up`.
- `npm run dev` (from `frontend/`): Run the Vite dev server locally without Docker.

## Coding Style & Naming Conventions
- Python: use 4-space indentation; follow PEP 8 conventions for modules and classes.
- JavaScript/React: follow ESLint rules in `frontend/eslint.config.js`.
- File naming: keep Python modules in `snake_case.py`; React components use `PascalCase` in `.jsx` files.
- There is no repo-wide formatter config; keep changes consistent with surrounding code.

## Testing Guidelines
- Backend tests use `pytest` via `just test-backend` and run inside the backend Docker container.
- New tests should be placed in `backend/tests/` and follow the `test_*.py` naming pattern.

## Commit & Pull Request Guidelines
- Commit history shows short, descriptive messages (e.g., “redo front end as web app”); keep messages concise and action-oriented.
- PRs should include a clear summary, note any UI changes with screenshots, and link related issues when applicable.
- If changing API contracts, update both `backend/app/api/` and `frontend/src/api/` in the same PR.

## Configuration & Logs
- Ports: frontend `7003`, backend `7004` via `docker-compose.yml`.
- Frontend API base URL uses `VITE_API_URL` (defaults to `/api` in `frontend/src/api/client.js`).
