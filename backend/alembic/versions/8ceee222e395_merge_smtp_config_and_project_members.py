"""Merge SMTP Config and Project Members

Revision ID: 8ceee222e395
Revises: 3f2d533efdf9, 766254bdd392
Create Date: 2026-07-17 12:17:11.179478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ceee222e395'
down_revision: Union[str, Sequence[str], None] = ('3f2d533efdf9', '766254bdd392')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
