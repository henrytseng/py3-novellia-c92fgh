"""initial

Revision ID: 001
Revises:
Create Date: 2026-04-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "records",
        sa.Column("id", sa.String(255), primary_key=True, unique=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("code", sa.String(255), nullable=False),
        sa.Column("resource_type", sa.String(255), nullable=False),
        sa.Column("effective_date_time", sa.String(255), nullable=True),
        sa.Column("performed_date_time", sa.String(255), nullable=True),
        sa.Column("dosage_instruction", sa.String(255), nullable=True),
        sa.Column("value_quantity", sa.String(255), nullable=True),
        sa.Column("status", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_records_scr"),
        "records",
        ["subject", "code", "resource_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_records_cr"),
        "records",
        ["code", "resource_type"],
        unique=False,
    )

    op.create_table(
        "imported_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("raw_body", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "validation_errors", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column(
            "record_id",
            sa.String(),
            sa.ForeignKey("records.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_imported_resources_created_at"),
        "imported_resources",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("imported_resources")
    op.drop_table("records")
