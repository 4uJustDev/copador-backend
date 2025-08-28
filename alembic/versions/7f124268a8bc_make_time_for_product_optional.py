"""make time for product optional

Revision ID: 7f124268a8bc
Revises: f498b2ba7564
Create Date: 2025-08-28 13:04:27.737928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f124268a8bc'
down_revision: Union[str, Sequence[str], None] = 'f498b2ba7564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
