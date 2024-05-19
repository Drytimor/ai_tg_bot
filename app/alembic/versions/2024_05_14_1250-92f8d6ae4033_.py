"""

Revision ID: 92f8d6ae4033
Revises: c2ca1e44dc77
Create Date: 2024-05-14 12:50:49.634728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92f8d6ae4033'
down_revision: Union[str, None] = 'c2ca1e44dc77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("user_bots", "user_models")


def downgrade() -> None:
    pass
