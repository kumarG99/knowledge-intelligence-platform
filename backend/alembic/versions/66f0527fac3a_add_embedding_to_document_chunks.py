"""Add embedding to document chunks.

Revision ID: 66f0527fac3a
Revises: 8902c8d4d57d
"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR

from alembic import op

# Revision identifiers used by Alembic.
revision: str = "66f0527fac3a"
down_revision: str | None = "8902c8d4d57d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add a nullable 384-dimensional embedding column."""
    op.add_column(
        "document_chunks",
        sa.Column(
            "embedding",
            VECTOR(384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove the embedding column."""
    op.drop_column("document_chunks", "embedding")
