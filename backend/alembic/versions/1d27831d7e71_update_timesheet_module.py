"""Update Timesheet Module

Revision ID: 1d27831d7e71
Revises: ed0e09fe9e69
Create Date: 2026-07-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1d27831d7e71"
down_revision: Union[str, Sequence[str], None] = "ed0e09fe9e69"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -----------------------------
    # Create ENUM types
    # -----------------------------
    priority_enum = sa.Enum(
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        name="priority",
    )

    verification_enum = sa.Enum(
        "PENDING",
        "VERIFIED",
        "REWORK_REQUIRED",
        name="verificationstatus",
    )

    hitmiss_enum = sa.Enum(
        "HIT",
        "MISS",
        "BLOCKED",
        name="hitmiss",
    )

    status_enum = sa.Enum(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="timesheetstatus",
    )

    bind = op.get_bind()

    priority_enum.create(bind, checkfirst=True)
    verification_enum.create(bind, checkfirst=True)
    hitmiss_enum.create(bind, checkfirst=True)
    status_enum.create(bind, checkfirst=True)

    # -----------------------------
    # New Columns
    # -----------------------------

    op.add_column(
        "timesheets",
        sa.Column("shared_task_id", sa.String(100), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("deliverable", sa.Text(), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("priority", priority_enum, nullable=True),
    )

    # planned_hours
    op.add_column(
        "timesheets",
        sa.Column(
            "planned_hours",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "timesheets",
        "planned_hours",
        server_default=None,
    )

    # actual_hours
    op.add_column(
        "timesheets",
        sa.Column(
            "actual_hours",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "timesheets",
        "actual_hours",
        server_default=None,
    )

    op.add_column(
        "timesheets",
        sa.Column("due_date", sa.Date(), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column(
            "actual_completion_date",
            sa.Date(),
            nullable=True,
        ),
    )

    # verification
    op.add_column(
        "timesheets",
        sa.Column(
            "verification",
            verification_enum,
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.alter_column(
        "timesheets",
        "verification",
        server_default=None,
    )

    op.add_column(
        "timesheets",
        sa.Column(
            "hit_or_miss",
            hitmiss_enum,
            nullable=True,
        ),
    )

    op.add_column(
        "timesheets",
        sa.Column("manager_rating", sa.Integer(), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("result_output", sa.Text(), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("evidence_link", sa.Text(), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("blocker_type", sa.String(100), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("blocker_reason", sa.Text(), nullable=True),
    )

    op.add_column(
        "timesheets",
        sa.Column("next_action", sa.Text(), nullable=True),
    )

    # -----------------------------
    # Change status column to ENUM
    # -----------------------------
    op.alter_column(
        "timesheets",
        "status",
        existing_type=sa.VARCHAR(length=20),
        type_=status_enum,
        existing_nullable=False,
        postgresql_using="status::timesheetstatus",
    )

    # -----------------------------
    # Remove old column
    # -----------------------------
    op.drop_column("timesheets", "hours")

    # IMPORTANT:
    # Remove this if existing users don't all have department_id.
    # Uncomment only when every row has department_id.
    #
    # op.alter_column(
    #     "users",
    #     "department_id",
    #     existing_type=sa.UUID(),
    #     nullable=False,
    # )


def downgrade() -> None:

    op.add_column(
        "timesheets",
        sa.Column("hours", sa.Float(), nullable=False),
    )

    op.alter_column(
        "timesheets",
        "status",
        existing_type=sa.Enum(
            "PENDING",
            "APPROVED",
            "REJECTED",
            name="timesheetstatus",
        ),
        type_=sa.String(20),
        existing_nullable=False,
    )

    op.drop_column("timesheets", "next_action")
    op.drop_column("timesheets", "blocker_reason")
    op.drop_column("timesheets", "blocker_type")
    op.drop_column("timesheets", "evidence_link")
    op.drop_column("timesheets", "result_output")
    op.drop_column("timesheets", "manager_rating")
    op.drop_column("timesheets", "hit_or_miss")
    op.drop_column("timesheets", "verification")
    op.drop_column("timesheets", "actual_completion_date")
    op.drop_column("timesheets", "due_date")
    op.drop_column("timesheets", "actual_hours")
    op.drop_column("timesheets", "planned_hours")
    op.drop_column("timesheets", "priority")
    op.drop_column("timesheets", "deliverable")
    op.drop_column("timesheets", "shared_task_id")

    bind = op.get_bind()

    sa.Enum(name="priority").drop(bind, checkfirst=True)
    sa.Enum(name="verificationstatus").drop(bind, checkfirst=True)
    sa.Enum(name="hitmiss").drop(bind, checkfirst=True)
    sa.Enum(name="timesheetstatus").drop(bind, checkfirst=True)