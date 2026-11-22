"""drop reference_links column

Revision ID: 0002_drop_reference_links
Revises: 0001_initial
Create Date: 2026-11-17
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_drop_reference_links"
down_revision = "b27f49459446"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("session_progress") as batch_op:
        batch_op.drop_column("reference_links")


def downgrade() -> None:
    op.add_column(
        "session_progress",
        sa.Column("reference_links", sa.JSON(), nullable=False),
    )
