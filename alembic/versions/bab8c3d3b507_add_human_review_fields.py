
"""Add human review fields

Revision ID: bab8c3d3b507
Revises: 3f5075c8e61e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "bab8c3d3b507"
down_revision: Union[str, Sequence[str], None] = "3f5075c8e61e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extracted entities
    op.add_column(
        "extracted_entities",
        sa.Column(
            "review_status",
            sa.String(length=30),
            server_default="pending",
            nullable=False,
        ),
    )

    op.add_column(
        "extracted_entities",
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
    )

    op.add_column(
        "extracted_entities",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_extracted_entities_reviewed_by_users",
        "extracted_entities",
        "users",
        ["reviewed_by"],
        ["id"],
        ondelete="SET NULL",
    )

    # Lab results
    op.add_column(
        "lab_results",
        sa.Column(
            "review_status",
            sa.String(length=30),
            server_default="pending",
            nullable=False,
        ),
    )

    op.add_column(
        "lab_results",
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
    )

    op.add_column(
        "lab_results",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_foreign_key(
        "fk_lab_results_reviewed_by_users",
        "lab_results",
        "users",
        ["reviewed_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_lab_results_reviewed_by_users",
        "lab_results",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_extracted_entities_reviewed_by_users",
        "extracted_entities",
        type_="foreignkey",
    )

    op.drop_column("lab_results", "reviewed_at")
    op.drop_column("lab_results", "reviewed_by")
    op.drop_column("lab_results", "review_status")

    op.drop_column("extracted_entities", "reviewed_at")
    op.drop_column("extracted_entities", "reviewed_by")
    op.drop_column("extracted_entities", "review_status")
