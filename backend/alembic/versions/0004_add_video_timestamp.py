"""add video timestamp to session progress

Revision ID: 0004_add_video_timestamp
Revises: 0003_add_source_url
Create Date: 2026-11-18
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_video_timestamp"
down_revision = "0003_add_source_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "session_progress",
        sa.Column("video_timestamp_seconds", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    with op.batch_alter_table("session_progress") as batch_op:
        batch_op.drop_column("video_timestamp_seconds")
