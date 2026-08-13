"""Dropped Columns is_verified, middle_name and last_name and added full_name

Revision ID: df08970df514
Revises: 05924075c978
Create Date: 2026-07-07 16:19:01.491541
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "df08970df514"
down_revision: Union[str, Sequence[str], None] = "05924075c978"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add full_name as nullable
    op.add_column(
        "users",
        sa.Column("full_name", sa.String(), nullable=True),
    )

    # 2. Copy existing names
    op.execute("""
        UPDATE users
        SET full_name = TRIM(
            COALESCE(first_name, '') || ' ' ||
            COALESCE(middle_name, '') || ' ' ||
            COALESCE(last_name, '')
        )
    """)

    # 3. If any row is still empty, give a default value
    op.execute("""
        UPDATE users
        SET full_name = 'Unknown User'
        WHERE full_name IS NULL OR TRIM(full_name) = ''
    """)

    # 4. Make full_name NOT NULL
    op.alter_column(
        "users",
        "full_name",
        nullable=False,
    )

    # 5. Remove old columns
    op.drop_column("users", "first_name")
    op.drop_column("users", "middle_name")
    op.drop_column("users", "last_name")
    op.drop_column("users", "is_verified")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.add_column(
        "users",
        sa.Column("middle_name", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("last_name", sa.String(), nullable=True),
    )

    op.add_column(
        "users",
        sa.Column("first_name", sa.String(), nullable=False, server_default=""),
    )

    op.drop_column("users", "full_name")