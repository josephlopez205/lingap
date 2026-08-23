"""create gaps table

Revision ID: 6851d053780c
Revises: 87d54598d7ec
Create Date: 2026-08-24 05:11:01.234778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6851d053780c'
down_revision: Union[str, None] = '87d54598d7ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'gaps',
        sa.Column('gap_id', sa.Integer, primary_key=True),
        sa.Column('lgu_id', sa.Integer, sa.ForeignKey('lgus.lgu_id')),
        sa.Column('barangay_id', sa.Integer, sa.ForeignKey('barangays.barangay_id')),
        sa.Column('sector', sa.Text),
        sa.Column('rule_id', sa.Text, nullable=False),
        sa.Column('severity_score', sa.Numeric(5, 2)),
        sa.Column('affected_population', sa.Integer),
        sa.Column('evidence_data', postgresql.JSONB),
        sa.Column('centroid_lat', sa.Numeric(10, 6)),
        sa.Column('centroid_lng', sa.Numeric(10, 6)),
        sa.Column('status', sa.Text, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now()),
    )
    op.create_check_constraint('gaps_sector_check', 'gaps', "sector IN ('Health', 'Education', 'Infrastructure')")
    op.create_index('idx_gaps_lgu_id', 'gaps', ['lgu_id'])
    op.create_index('idx_gaps_severity', 'gaps', ['severity_score'], postgresql_ops={'severity_score': 'DESC'})

def downgrade():
    op.drop_table('gaps')
