"""Add lesson fields and achievement code

Revision ID: b3c4d5e6f7a8
Revises: 09a56bd80759
Create Date: 2025-10-31 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b3c4d5e6f7a8'
down_revision = '09a56bd80759'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('lessons', sa.Column('theory', sa.Text(), nullable=True))
    op.add_column('lessons', sa.Column('sql_solution', sa.Text(), nullable=True))
    op.add_column('lessons', sa.Column('expected_result', sa.JSON(), nullable=True))
    
    op.add_column('achievements', sa.Column('code', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_achievements_code'), 'achievements', ['code'], unique=True)
    
    op.execute('UPDATE achievements SET code = CONCAT("achievement_", id) WHERE code IS NULL')
    
    op.alter_column('achievements', 'code', nullable=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_achievements_code'), table_name='achievements')
    op.drop_column('achievements', 'code')
    
    op.drop_column('lessons', 'expected_result')
    op.drop_column('lessons', 'sql_solution')
    op.drop_column('lessons', 'theory')
