"""initial schema

Revision ID: dd43f0b26b76
Revises: 
Create Date: 2026-08-20 15:08:25.386974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd43f0b26b76'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    op.execute("""
    CREATE TABLE lgus (
      lgu_id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      province TEXT,
      region TEXT,
      income_classification TEXT
    );
    """)

    op.execute("""
    CREATE TABLE barangays (
      barangay_id SERIAL PRIMARY KEY,
      lgu_id INT REFERENCES lgus(lgu_id),
      name TEXT NOT NULL,
      psgc_code TEXT,
      geom GEOMETRY(MultiPolygon, 4326)
    );
    """)

    op.execute("""
    CREATE TABLE demographics (
      barangay_id INT REFERENCES barangays(barangay_id) PRIMARY KEY,
      population_total INT,
      population_0_14 INT,
      population_15_59 INT,
      population_60_plus INT,
      poverty_incidence_pct NUMERIC(5,2),
      source TEXT,
      updated_at TIMESTAMP DEFAULT now()
    );
    """)

    op.execute("""
    CREATE TABLE facilities (
      facility_id SERIAL PRIMARY KEY,
      barangay_id INT REFERENCES barangays(barangay_id),
      facility_name TEXT NOT NULL,
      facility_type TEXT CHECK (facility_type IN ('health','school')),
      capacity INT,
      geom GEOMETRY(Point, 4326)
    );
    """)

    op.execute("""
    CREATE TABLE users (
      user_id SERIAL PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT CHECK (role IN ('admin','planning_officer','executive','viewer')),
      lgu_id INT REFERENCES lgus(lgu_id)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS users;")
    op.execute("DROP TABLE IF EXISTS facilities;")
    op.execute("DROP TABLE IF EXISTS demographics;")
    op.execute("DROP TABLE IF EXISTS barangays;")
    op.execute("DROP TABLE IF EXISTS lgus;")
