# Justfile for qwixx
# Run `just --list` to see available commands

# Start docker services in detached mode
docker-up:
    docker compose up -d

# Stop docker services
docker-down:
    docker compose down

# Build docker services
docker-build:
    docker compose build

# Run backend tests
test-backend:
    docker compose run --rm backend pytest

# Scan logs for errors
scan-logs:
    @echo "--- Checking application logs ---"
    @grep -riE "ERROR|CRITICAL|Exception|Traceback" logs/ || echo "No errors found in application logs."
