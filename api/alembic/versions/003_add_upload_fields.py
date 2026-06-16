"""Add upload fields to files, upload_sessions, and users

Revision ID: 003
Revises: 002
Create Date: 2026-06-15

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "files",
        sa.Column("user_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "files",
        sa.Column("classification", sa.String(20), nullable=True),
    )
    op.add_column(
        "files",
        sa.Column("mime_type", sa.String(50), nullable=True),
    )
    op.add_column(
        "files",
        sa.Column("status", sa.String(20), nullable=True),
    )
    op.add_column(
        "files",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_index(
        op.f("ix_files_user_id"), "files", ["user_id"]
    )
    op.create_foreign_key(
        "fk_files_user_id", "files", "users", ["user_id"], ["id"]
    )
    op.add_column(
        "upload_sessions",
        sa.Column(
            "file_count", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "files_uploaded", sa.Integer(), nullable=False, server_default="0"
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "files_uploaded")
    op.drop_column("upload_sessions", "file_count")
    op.drop_constraint("fk_files_user_id", "files", type_="foreignkey")
    op.drop_index(op.f("ix_files_user_id"), table_name="files")
    op.drop_column("files", "updated_at")
    op.drop_column("files", "status")
    op.drop_column("files", "mime_type")
    op.drop_column("files", "classification")
    op.drop_column("files", "user_id")
