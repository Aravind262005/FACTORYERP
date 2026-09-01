"""create schemas

Revision ID: dba36e4f129e
Revises: 
Create Date: 2026-08-25 11:31:26.500903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dba36e4f129e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS manufacturing;")
    op.execute("CREATE SCHEMA IF NOT EXISTS inventory;")
    op.execute("CREATE SCHEMA IF NOT EXISTS procurement;")
    op.execute("CREATE SCHEMA IF NOT EXISTS orders;")
    op.execute("CREATE SCHEMA IF NOT EXISTS application;")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit;")

def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS manufacturing CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS inventory CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS procurement CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS orders CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS application CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS audit CASCADE;")
