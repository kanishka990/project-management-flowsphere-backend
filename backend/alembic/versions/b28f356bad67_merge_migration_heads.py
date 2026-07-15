"""merge migration heads

Revision ID: b28f356bad67
Revises: 1d27831d7e71, 220ccc00ce32
Create Date: 2026-07-15 12:26:30.815867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b28f356bad67'
down_revision: Union[str, Sequence[str], None] = ('1d27831d7e71', '220ccc00ce32')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
