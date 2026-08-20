"""add source tracking columns

Revision ID: 87d54598d7ec
Revises: dd43f0b26b76
Create Date: 2026-08-20 20:46:51.854271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87d54598d7ec'
down_revision: Union[str, None] = 'dd43f0b26b76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("barangays", sa.Column("source", sa.Text(), nullable=True))
    op.add_column("facilities", sa.Column("source", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("facilities", "source")
    op.drop_column("barangays", "source")
