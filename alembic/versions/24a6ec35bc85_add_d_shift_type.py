"""Add D shift type

Revision ID: 24a6ec35bc85
Revises: c4d353d4f834
Create Date: 2024-09-03 12:54:08.304317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '24a6ec35bc85'
down_revision: Union[str, None] = 'c4d353d4f834'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
