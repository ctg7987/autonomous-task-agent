# Infra

Docker images to run both services locally via Docker Compose.

Usage:

- cp infra/.env.example .env  # optional, fill keys
- docker compose -f infra/docker-compose.yml up --build

Then open http://localhost:3000
