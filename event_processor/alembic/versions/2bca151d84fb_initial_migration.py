"""Initial migration

Revision ID: 2bca151d84fb
Revises:
Create Date: 2025-02-24 19:05:04.608573

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2bca151d84fb"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sensor_id", sa.String(length=100), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("humidity", sa.Float(), nullable=False),
        sa.Column("noise_level", sa.Float(), nullable=False),
        sa.Column("air_quality_index", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("event")
