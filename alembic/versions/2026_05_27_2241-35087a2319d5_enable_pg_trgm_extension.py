"""enable pg_trgm extension

Revision ID: 35087a2319d5
Revises: 1ef90d2c9418
Create Date: 2026-05-27 22:41:03.111718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35087a2319d5'
down_revision: Union[str, Sequence[str], None] = '1ef90d2c9418'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_name_trgm
        ON products
        USING gin (name gin_trgm_ops)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_products_name_trgm")
