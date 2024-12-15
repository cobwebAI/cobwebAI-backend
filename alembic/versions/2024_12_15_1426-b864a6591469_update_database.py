"""Update database

Revision ID: b864a6591469
Revises: b03aabdbf581
Create Date: 2024-12-15 14:26:47.929139+03:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b864a6591469'
down_revision: Union[str, None] = 'b03aabdbf581'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    message_role = postgresql.ENUM('USER', 'ASSISTANT', name='message_role_enum')
    message_role.create(op.get_bind(), checkfirst=True)
    op.add_column('messages', sa.Column('role', message_role, nullable=False))
    op.add_column('messages', sa.Column('attachments', sa.Text(), nullable=True))
    op.add_column('questions', sa.Column('text', sa.Text(), nullable=False))
    op.add_column('questions', sa.Column('answers', postgresql.JSONB(astext_type=sa.Text()), nullable=False))
    op.add_column('questions', sa.Column('correct_answer', sa.Text(), nullable=False))
    op.add_column('questions', sa.Column('explanation', sa.Text(), nullable=True))
    op.create_unique_constraint(None, 'questions', ['test_id', 'order_number'])
    op.drop_column('questions', 'content')
    op.alter_column('tests', 'best_score',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               type_=sa.Integer(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tests', 'best_score',
               existing_type=sa.Integer(),
               type_=sa.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.add_column('questions', sa.Column('content', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'questions', type_='unique')
    op.drop_column('questions', 'explanation')
    op.drop_column('questions', 'correct_answer')
    op.drop_column('questions', 'answers')
    op.drop_column('questions', 'text')
    op.drop_column('messages', 'attachments')
    op.drop_column('messages', 'role')
    # ### end Alembic commands ###
