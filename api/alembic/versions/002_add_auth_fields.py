"""Add auth fields and oauth_identities table

Revision ID: 002
Revises: 001
Create Date: 2026-06-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_hash", sa.String(255), nullable=True
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.create_table(
        "oauth_identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "user_id", sa.Uuid(), nullable=False
        ),
        sa.Column(
            "provider", sa.String(50), nullable=False
        ),
        sa.Column(
            "provider_user_id",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "provider", "provider_user_id",
            name="uq_oauth_provider_user",
        ),
    )
    op.create_index(
        op.f("ix_oauth_identities_user_id"),
        "oauth_identities",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_oauth_identities_user_id"),
        table_name="oauth_identities",
    )
    op.drop_table("oauth_identities")
    op.drop_column("users", "is_active")
    op.drop_column("users", "password_hash")
