"""

Revision ID: 2ef2d5796f23
Revises: 92f8d6ae4033
Create Date: 2024-05-14 13:03:31.924072

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ef2d5796f23'
down_revision: Union[str, None] = '92f8d6ae4033'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("user_models", "bot_id", new_column_name="model_id")
    op.alter_column("user_models", "name", new_column_name="model_name")


def downgrade() -> None:
    pass
