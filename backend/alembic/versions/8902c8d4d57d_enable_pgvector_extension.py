"""enable pgvector extension

Revision ID: 8902c8d4d57d
Revises: 757ea67689dd
Create Date: 2026-10-15 23:04:02.858541

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8902c8d4d57d'
down_revision: Union[str, Sequence[str], None] = '757ea67689dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # Intentionally preserve the extension during rollback.
    # Future tables may depend on the vector type.
    pass
