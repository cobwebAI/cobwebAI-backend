"""Fix correct answer type

Revision ID: 50b6a388d945
Revises: b864a6591469
Create Date: 2024-12-15 16:44:04.011592+03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50b6a388d945'
down_revision: Union[str, None] = 'b864a6591469'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('questions', 'correct_answer')
    op.add_column('questions', sa.Column('correct_answer', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('questions', 'correct_answer')
    op.add_column('questions', sa.Column('correct_answer', sa.Text(), nullable=False))
    # ### end Alembic commands ###
