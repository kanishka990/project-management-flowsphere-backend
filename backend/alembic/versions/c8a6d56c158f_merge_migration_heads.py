"""Merge migration heads

Revision ID: c8a6d56c158f
Revises: 61f8041eec11, 8460693edbd4
Create Date: 2026-07-29 14:36:07.324097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8a6d56c158f'
down_revision: Union[str, Sequence[str], None] = ('61f8041eec11', '8460693edbd4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
