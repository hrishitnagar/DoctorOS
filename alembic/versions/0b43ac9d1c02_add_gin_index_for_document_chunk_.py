"""Add GIN index for document chunk keyword search

Revision ID: 0b43ac9d1c02
Revises: 7ed135eb675b
Create Date: 2026-11-19 20:58:47.661823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b43ac9d1c02'
down_revision: Union[str, Sequence[str], None] = '7ed135eb675b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE INDEX ix_document_chunks_chunk_text_gin
        ON document_chunks
        USING GIN (to_tsvector('simple', chunk_text));
    """)


def downgrade() -> None:
    op.execute("""
        DROP INDEX IF EXISTS ix_document_chunks_chunk_text_gin;
    """)