"""Rectifies menu, submenu and permissions

Revision ID: 90a7b43cf05f
Revises: 17762c1aae8c
Create Date: 2026-07-14 13:11:54.554691

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "90a7b43cf05f"
down_revision: Union[str, Sequence[str], None] = "17762c1aae8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # -----------------------------
    # Menus
    # -----------------------------
    op.add_column(
        "menus",
        sa.Column("path", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "menus",
        sa.Column("icon", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "menus",
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "menus",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.alter_column(
        "menus",
        "code",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=100),
        existing_nullable=False,
    )

    op.create_index(
        op.f("ix_menus_is_active"),
        "menus",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        op.f("ix_menus_sort_order"),
        "menus",
        ["sort_order"],
        unique=False,
    )

    # Remove temporary defaults
    op.alter_column(
        "menus",
        "sort_order",
        server_default=None,
    )

    op.alter_column(
        "menus",
        "is_active",
        server_default=None,
    )

    # -----------------------------
    # Submenus
    # -----------------------------
    op.add_column(
        "submenus",
        sa.Column("path", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "submenus",
        sa.Column("icon", sa.String(length=100), nullable=True),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "created_by",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "updated_by",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "submenus",
        sa.Column(
            "deleted_by",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.alter_column(
        "submenus",
        "code",
        existing_type=sa.VARCHAR(length=20),
        type_=sa.String(length=100),
        existing_nullable=False,
    )

    op.create_index(
        op.f("ix_submenus_created_by"),
        "submenus",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        op.f("ix_submenus_is_active"),
        "submenus",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        op.f("ix_submenus_is_deleted"),
        "submenus",
        ["is_deleted"],
        unique=False,
    )

    op.create_index(
        op.f("ix_submenus_sort_order"),
        "submenus",
        ["sort_order"],
        unique=False,
    )

    op.create_index(
        op.f("ix_submenus_updated_by"),
        "submenus",
        ["updated_by"],
        unique=False,
    )

    # Remove temporary defaults
    op.alter_column(
        "submenus",
        "sort_order",
        server_default=None,
    )

    op.alter_column(
        "submenus",
        "is_active",
        server_default=None,
    )

    op.alter_column(
        "submenus",
        "is_deleted",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f("ix_submenus_updated_by"), table_name="submenus")
    op.drop_index(op.f("ix_submenus_sort_order"), table_name="submenus")
    op.drop_index(op.f("ix_submenus_is_deleted"), table_name="submenus")
    op.drop_index(op.f("ix_submenus_is_active"), table_name="submenus")
    op.drop_index(op.f("ix_submenus_created_by"), table_name="submenus")

    op.alter_column(
        "submenus",
        "code",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
    )

    op.drop_column("submenus", "deleted_by")
    op.drop_column("submenus", "deleted_at")
    op.drop_column("submenus", "is_deleted")
    op.drop_column("submenus", "updated_by")
    op.drop_column("submenus", "created_by")
    op.drop_column("submenus", "updated_at")
    op.drop_column("submenus", "created_at")
    op.drop_column("submenus", "is_active")
    op.drop_column("submenus", "sort_order")
    op.drop_column("submenus", "icon")
    op.drop_column("submenus", "path")

    op.drop_index(op.f("ix_menus_sort_order"), table_name="menus")
    op.drop_index(op.f("ix_menus_is_active"), table_name="menus")

    op.alter_column(
        "menus",
        "code",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(length=20),
        existing_nullable=False,
    )

    op.drop_column("menus", "is_active")
    op.drop_column("menus", "sort_order")
    op.drop_column("menus", "icon")
    op.drop_column("menus", "path")