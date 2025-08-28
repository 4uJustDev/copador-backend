"""add timestamps to categories

Revision ID: f498b2ba7564
Revises: f2124d3601e8
Create Date: 2025-08-28 12:41:55.906966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f498b2ba7564'
down_revision: Union[str, Sequence[str], None] = 'f2124d3601e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
