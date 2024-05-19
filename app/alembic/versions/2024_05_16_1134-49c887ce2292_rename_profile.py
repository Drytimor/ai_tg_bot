"""rename profile

Revision ID: 49c887ce2292
Revises: 30c4643caa94
Create Date: 2024-05-16 11:34:58.883826

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49c887ce2292'
down_revision: Union[str, None] = '30c4643caa94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("user_models", "user_prof_id", new_column_name="user_tg_id")
    op.alter_column("user_profile", "user_prof_id", new_column_name="user_tg_id")


def downgrade() -> None:
    pass
