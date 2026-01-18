# Qwixx Web Application

Refactored version of the Qwixx game from Christmas 2023 with a FastAPI backend and React frontend.

Automatic play is available for two players using the same (not great) strategy.

## Architecture

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React (Vite, MUI)
- **Orchestration**: Docker Compose
- **Task Runner**: [Just](https://github.com/casey/just)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- [Just](https://github.com/casey/just) (optional, but recommended)

### Quick Start

1. Start the services:
   ```bash
   just docker-up
   ```
   Or:
   ```bash
   docker compose up -d
   ```

2. Open your browser and navigate to:
   - Frontend: `http://localhost:7003`
   - Backend API Docs: `http://localhost:7004/docs`

### Development

- **Backend**: Located in `./backend`. The server runs with hot-reload.
- **Frontend**: Located in `./frontend`. The Vite dev server runs with hot-reload.

## Task Management

The project uses `justfile` for common tasks:

- `just docker-up`: Start all services
- `just docker-down`: Stop all services
- `just docker-build`: Build or rebuild services
- `just test-backend`: Run backend unit tests
- `just scan-logs`: Scan application and docker logs for errors
