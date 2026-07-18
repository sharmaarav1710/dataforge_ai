#!/usr/bin/env bash
set -euo pipefail

echo "Setting up DataForge AI..."

# Python backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Frontend
cd frontend && npm install && cd ..

# Local data dirs
mkdir -p data/uploads data/versions data/exports

# Env file if missing
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — add your OPENAI_API_KEY before using AI features."
fi

echo "Done. Run: make dev (or see README.md)"
