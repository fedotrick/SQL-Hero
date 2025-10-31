"""add_last_active_date_to_users

Revision ID: a8af3e20bfe3
Revises: b3c4d5e6f7a8
Create Date: 2025-10-31 17:38:09.995425

"""
from alembic import op
import sqlalchemy as sa


revision = 'a8af3e20bfe3'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('last_active_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_active_date')
