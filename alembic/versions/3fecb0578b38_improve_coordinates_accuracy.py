"""improve coordinates accuracy

Revision ID: 3fecb0578b38
Revises: 24f2412c8447
Create Date: 2024-11-23 02:43:58.018458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3fecb0578b38'
down_revision: Union[str, None] = '24f2412c8447'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('place', 'latitude',
               existing_type=sa.NUMERIC(precision=10, scale=9),
               type_=sa.DECIMAL(precision=30, scale=20),
               existing_nullable=False)
    op.alter_column('place', 'longitude',
               existing_type=sa.NUMERIC(precision=10, scale=9),
               type_=sa.DECIMAL(precision=30, scale=20),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('place', 'longitude',
               existing_type=sa.DECIMAL(precision=30, scale=20),
               type_=sa.NUMERIC(precision=10, scale=9),
               existing_nullable=False)
    op.alter_column('place', 'latitude',
               existing_type=sa.DECIMAL(precision=30, scale=20),
               type_=sa.NUMERIC(precision=10, scale=9),
               existing_nullable=False)
    # ### end Alembic commands ###
