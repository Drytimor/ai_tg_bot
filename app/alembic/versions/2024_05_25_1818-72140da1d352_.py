"""

Revision ID: 72140da1d352
Revises: 0b63caf22a96
Create Date: 2024-05-25 18:18:22.504481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72140da1d352'
down_revision: Union[str, None] = '0b63caf22a96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_profile', 'balance',
               existing_type=sa.NUMERIC(precision=10, scale=2),
               type_=sa.Numeric(precision=20, scale=10),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_profile', 'balance',
               existing_type=sa.Numeric(precision=20, scale=10),
               type_=sa.NUMERIC(precision=10, scale=2),
               existing_nullable=False)
    # ### end Alembic commands ###
