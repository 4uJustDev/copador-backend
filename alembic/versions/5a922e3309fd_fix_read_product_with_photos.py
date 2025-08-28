"""fix read product with photos

Revision ID: 5a922e3309fd
Revises: 7f124268a8bc
Create Date: 2025-08-28 13:29:52.595580

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a922e3309fd"
down_revision: Union[str, Sequence[str], None] = "7f124268a8bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
