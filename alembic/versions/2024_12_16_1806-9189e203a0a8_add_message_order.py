"""Add message order

Revision ID: 9189e203a0a8
Revises: 50b6a388d945
Create Date: 2024-12-16 18:06:15.699165+03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9189e203a0a8'
down_revision: Union[str, None] = '50b6a388d945'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('order_number', sa.Integer(), nullable=False))
    op.create_unique_constraint('unique_chat_order_number', 'messages', ['chat_id', 'order_number'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_chat_order_number', 'messages', type_='unique')
    op.drop_column('messages', 'order_number')
    # ### end Alembic commands ###