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
    docker compose run --rm -e PYTHONPATH=. backend pytest

# Scan logs for errors
scan-logs:
    @echo "--- Checking application logs ---"
    @grep -riE "ERROR|CRITICAL|Exception|Traceback" logs/ || echo "No errors found in application logs."

# Local Environment Setup
setup:
    pip install -r requirements.txt

# --- RL Training Commands (CLI Based) ---

# Train the RL agent via self-play
train-rl episodes="50000" eval_interval="1000":
    cd backend && python -m app.training.play train --episodes {{episodes}} --eval-interval {{eval_interval}}

# Evaluate the RL agent vs Hard AI
eval-rl games="500":
    cd backend && python -m app.training.play evaluate --games {{games}}

# Watch a single game: RL Agent vs Hard AI
watch-rl:
    cd backend && python -m app.training.play watch
