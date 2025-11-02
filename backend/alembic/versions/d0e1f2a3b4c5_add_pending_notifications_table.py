"""add pending notifications table

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2025-11-02 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


revision = 'd0e1f2a3b4c5'
down_revision = 'c9d0e1f2a3b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pending_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.Enum('ACHIEVEMENT_UNLOCKED', 'REMINDER', 'STREAK_REMINDER', 'DAILY_CHALLENGE', name='notificationtype'), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'FAILED', name='notificationstatus'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pending_notifications_created_at'), 'pending_notifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_pending_notifications_id'), 'pending_notifications', ['id'], unique=False)
    op.create_index(op.f('ix_pending_notifications_notification_type'), 'pending_notifications', ['notification_type'], unique=False)
    op.create_index(op.f('ix_pending_notifications_status'), 'pending_notifications', ['status'], unique=False)
    op.create_index(op.f('ix_pending_notifications_user_id'), 'pending_notifications', ['user_id'], unique=False)
    op.create_index('idx_status_created', 'pending_notifications', ['status', 'created_at'], unique=False)
    op.create_index('idx_user_type_status', 'pending_notifications', ['user_id', 'notification_type', 'status'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_user_type_status', table_name='pending_notifications')
    op.drop_index('idx_status_created', table_name='pending_notifications')
    op.drop_index(op.f('ix_pending_notifications_user_id'), table_name='pending_notifications')
    op.drop_index(op.f('ix_pending_notifications_status'), table_name='pending_notifications')
    op.drop_index(op.f('ix_pending_notifications_notification_type'), table_name='pending_notifications')
    op.drop_index(op.f('ix_pending_notifications_id'), table_name='pending_notifications')
    op.drop_index(op.f('ix_pending_notifications_created_at'), table_name='pending_notifications')
    op.drop_table('pending_notifications')
