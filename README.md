# Lingap

## Setup
1. Install PostgreSQL 16 + PostGIS locally (see docs/SETUP.md for OS-specific steps)
2. Create the `lingap` DB/user and run `CREATE EXTENSION postgis;`
3. `cd backend && python3 -m venv venv && source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `cp .env.example .env`
6. `uvicorn app.main:app --reload`
7. `cd frontend && npm install && npm run dev`

## Branch naming
- `feat/<short-description>` — features
- `data/<short-description>` — data pipeline / import work
