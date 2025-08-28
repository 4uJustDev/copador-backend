"""remove unnecesary files

Revision ID: addf8e859349
Revises: b4f4896aed29
Create Date: 2025-08-28 15:33:02.351551

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "addf8e859349"
down_revision: Union[str, Sequence[str], None] = "b4f4896aed29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
