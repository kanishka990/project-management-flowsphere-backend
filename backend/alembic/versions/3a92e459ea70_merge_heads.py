"""merge heads

Revision ID: 3a92e459ea70
Revises: 62262150fc46, fea7664a6dd4
Create Date: 2026-07-27 16:10:59.066052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a92e459ea70'
down_revision: Union[str, Sequence[str], None] = ('62262150fc46', 'fea7664a6dd4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
