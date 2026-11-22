
"""Add HNSW cosine embedding index

Revision ID: 7ed135eb675b
Revises: 147e7e4f7200
"""

from typing import Sequence, Union
from alembic import op

revision: str = "7ed135eb675b"
down_revision: Union[str, Sequence[str], None] = "147e7e4f7200"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WHERE embedding IS NOT NULL;
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw;
    """)
