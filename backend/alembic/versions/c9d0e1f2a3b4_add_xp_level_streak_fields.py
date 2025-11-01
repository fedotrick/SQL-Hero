"""add xp level streak fields

Revision ID: c9d0e1f2a3b4
Revises: a8af3e20bfe3
Create Date: 2025-10-31 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c9d0e1f2a3b4'
down_revision = 'a8af3e20bfe3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add XP, level, and streak fields to users table
    op.add_column('users', sa.Column('xp', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('level', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('total_queries', sa.Integer(), nullable=False, server_default='0'))
    
    # Add first_try and xp_earned fields to user_progress table
    op.add_column('user_progress', sa.Column('first_try', sa.Boolean(), nullable=True))
    op.add_column('user_progress', sa.Column('xp_earned', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Drop user_progress columns
    op.drop_column('user_progress', 'xp_earned')
    op.drop_column('user_progress', 'first_try')
    
    # Drop user columns
    op.drop_column('users', 'total_queries')
    op.drop_column('users', 'longest_streak')
    op.drop_column('users', 'current_streak')
    op.drop_column('users', 'level')
    op.drop_column('users', 'xp')
