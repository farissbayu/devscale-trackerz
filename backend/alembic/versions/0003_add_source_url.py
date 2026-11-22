"""add learning source link per session

Revision ID: 0003_add_source_url
Revises: 0002_drop_reference_links
Create Date: 2026-11-18
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_source_url"
down_revision = "0002_drop_reference_links"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "learning_sessions",
        sa.Column("source_url", sa.String(length=1000), nullable=False, server_default=""),
    )


def downgrade() -> None:
    with op.batch_alter_table("learning_sessions") as batch_op:
        batch_op.drop_column("source_url")
