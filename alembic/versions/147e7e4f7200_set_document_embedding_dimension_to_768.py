
"""Set document embedding dimension to 768

Revision ID: 147e7e4f7200
Revises: 8d04bf0b0c16
"""

from typing import Sequence, Union

from alembic import op


# Revision identifiers
revision: str = "147e7e4f7200"
down_revision: Union[str, Sequence[str], None] = "8d04bf0b0c16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change embedding column to vector(768)."""

    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding
        TYPE vector(768)
        USING embedding::vector(768);
    """)


def downgrade() -> None:
    """Restore unbounded vector type."""

    op.execute("""
        ALTER TABLE document_chunks
        ALTER COLUMN embedding
        TYPE vector
        USING embedding::vector;
    """)
