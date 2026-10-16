"""create document pages table

Revision ID: eb2d76a5afaf
Revises: ac343279c2ea
Create Date: 2026-10-15 22:07:17.061433

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'eb2d76a5afaf'
down_revision: Union[str, Sequence[str], None] = 'ac343279c2ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.create_table(
        "document_pages",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "document_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "page_number",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "document_id",
            "page_number",
            name="uq_document_pages_document_page",
        ),
    )

    op.create_index(
        "ix_document_pages_document_id",
        "document_pages",
        ["document_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_document_pages_document_id",
        table_name="document_pages",
    )

    op.drop_table("document_pages")
