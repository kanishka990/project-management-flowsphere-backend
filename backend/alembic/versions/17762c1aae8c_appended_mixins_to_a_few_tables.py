"""Appended Mixins to a few tables

Revision ID: 17762c1aae8c
Revises: ed0e09fe9e69
Create Date: 2026-07-13 11:59:37.108418
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17762c1aae8c"
down_revision: Union[str, Sequence[str], None] = "ed0e09fe9e69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------- Departments ----------------

    op.add_column(
        "departments",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "departments",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "departments",
        sa.Column("created_by", sa.Uuid(), nullable=True),
    )

    op.add_column(
        "departments",
        sa.Column("updated_by", sa.Uuid(), nullable=True),
    )

    op.add_column(
        "departments",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.add_column(
        "departments",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "departments",
        sa.Column("deleted_by", sa.Uuid(), nullable=True),
    )

    op.create_index(
        op.f("ix_departments_created_by"),
        "departments",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        op.f("ix_departments_is_deleted"),
        "departments",
        ["is_deleted"],
        unique=False,
    )

    op.create_index(
        op.f("ix_departments_updated_by"),
        "departments",
        ["updated_by"],
        unique=False,
    )

    # ---------------- Menus ----------------

    op.add_column(
        "menus",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "menus",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "menus",
        sa.Column("created_by", sa.Uuid(), nullable=True),
    )

    op.add_column(
        "menus",
        sa.Column("updated_by", sa.Uuid(), nullable=True),
    )

    op.add_column(
        "menus",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.add_column(
        "menus",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.add_column(
        "menus",
        sa.Column("deleted_by", sa.Uuid(), nullable=True),
    )

    op.create_index(
        op.f("ix_menus_created_by"),
        "menus",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        op.f("ix_menus_is_deleted"),
        "menus",
        ["is_deleted"],
        unique=False,
    )

    op.create_index(
        op.f("ix_menus_updated_by"),
        "menus",
        ["updated_by"],
        unique=False,
    )

    # Remove temporary defaults

    op.alter_column(
        "departments",
        "is_deleted",
        server_default=None,
    )

    op.alter_column(
        "menus",
        "is_deleted",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f("ix_menus_updated_by"), table_name="menus")
    op.drop_index(op.f("ix_menus_is_deleted"), table_name="menus")
    op.drop_index(op.f("ix_menus_created_by"), table_name="menus")

    op.drop_column("menus", "deleted_by")
    op.drop_column("menus", "deleted_at")
    op.drop_column("menus", "is_deleted")
    op.drop_column("menus", "updated_by")
    op.drop_column("menus", "created_by")
    op.drop_column("menus", "updated_at")
    op.drop_column("menus", "created_at")

    op.drop_index(op.f("ix_departments_updated_by"), table_name="departments")
    op.drop_index(op.f("ix_departments_is_deleted"), table_name="departments")
    op.drop_index(op.f("ix_departments_created_by"), table_name="departments")

    op.drop_column("departments", "deleted_by")
    op.drop_column("departments", "deleted_at")
    op.drop_column("departments", "is_deleted")
    op.drop_column("departments", "updated_by")
    op.drop_column("departments", "created_by")
    op.drop_column("departments", "updated_at")
    op.drop_column("departments", "created_at")