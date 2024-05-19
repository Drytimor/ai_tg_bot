"""

Revision ID: 7deafdd2fb32
Revises: 49c887ce2292
Create Date: 2024-05-16 13:37:17.499586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7deafdd2fb32'
down_revision: Union[str, None] = '49c887ce2292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user_models", "id")
    op.create_primary_key(
        constraint_name=op.f("pk_user_models_user_tg_id_model_id"),
        table_name="user_models",
        columns=["model_id", "user_tg_id"]
    )


def downgrade() -> None:
    pass
