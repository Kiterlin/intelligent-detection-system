"""add_alert_rules_and_alert_logs_tables

Revision ID: b15491c21938
Revises: 9716392fc1db
Create Date: 2025-11-14 13:09:03.791312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b15491c21938'
down_revision: Union[str, Sequence[str], None] = '9716392fc1db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create alert_rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('conditions', sa.JSON(), nullable=False),
        sa.Column('actions', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for alert_rules
    op.create_index('ix_alert_rules_id', 'alert_rules', ['id'])
    op.create_index('ix_alert_rules_user_id', 'alert_rules', ['user_id'])
    op.create_index('ix_alert_rules_is_active', 'alert_rules', ['is_active'])
    op.create_index('ix_alert_rules_created_at', 'alert_rules', ['created_at'])

    # Create alert_logs table
    op.create_table(
        'alert_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('detection_id', sa.Integer(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('conditions_met', sa.JSON(), nullable=True),
        sa.Column('actions_executed', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='success', nullable=False),
        sa.ForeignKeyConstraint(['rule_id'], ['alert_rules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['detection_id'], ['detection_history.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for alert_logs
    op.create_index('ix_alert_logs_id', 'alert_logs', ['id'])
    op.create_index('ix_alert_logs_rule_id', 'alert_logs', ['rule_id'])
    op.create_index('ix_alert_logs_detection_id', 'alert_logs', ['detection_id'])
    op.create_index('ix_alert_logs_triggered_at', 'alert_logs', ['triggered_at'])
    op.create_index('ix_alert_logs_status', 'alert_logs', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes and tables in reverse order
    op.drop_index('ix_alert_logs_status', 'alert_logs')
    op.drop_index('ix_alert_logs_triggered_at', 'alert_logs')
    op.drop_index('ix_alert_logs_detection_id', 'alert_logs')
    op.drop_index('ix_alert_logs_rule_id', 'alert_logs')
    op.drop_index('ix_alert_logs_id', 'alert_logs')
    op.drop_table('alert_logs')

    op.drop_index('ix_alert_rules_created_at', 'alert_rules')
    op.drop_index('ix_alert_rules_is_active', 'alert_rules')
    op.drop_index('ix_alert_rules_user_id', 'alert_rules')
    op.drop_index('ix_alert_rules_id', 'alert_rules')
    op.drop_table('alert_rules')
