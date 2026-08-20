# Lingap

## Setup
1. `docker compose up -d` — starts PostGIS
2. `cd backend && python3 -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. `uvicorn app.main:app --reload`
6. `cd frontend && npm install && npm run dev`

## Branch naming
- `feat/<short-description>` — features
- `data/<short-description>` — data pipeline / import work
