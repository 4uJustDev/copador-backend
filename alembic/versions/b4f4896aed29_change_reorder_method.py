"""change reorder method

Revision ID: b4f4896aed29
Revises: 5a922e3309fd
Create Date: 2025-08-28 14:48:32.509149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4f4896aed29'
down_revision: Union[str, Sequence[str], None] = '5a922e3309fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
