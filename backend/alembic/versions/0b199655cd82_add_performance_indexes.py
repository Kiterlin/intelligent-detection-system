"""add_performance_indexes

Revision ID: 0b199655cd82
Revises: b1285a3f607a
Create Date: 2025-11-12 18:59:53.807490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b199655cd82'
down_revision: Union[str, Sequence[str], None] = 'b1285a3f607a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add performance indexes."""

    # Users table indexes
    op.create_index('ix_users_role', 'users', ['role'])

    # ML Models table indexes
    op.create_index('ix_ml_models_status', 'ml_models', ['status'])
    op.create_index('ix_ml_models_uploaded_by', 'ml_models', ['uploaded_by'])
    op.create_index('ix_ml_models_created_at', 'ml_models', ['created_at'])
    op.create_index('ix_ml_models_status_created_at', 'ml_models', ['status', 'created_at'])

    # Detection History table indexes
    op.create_index('ix_detection_history_created_at', 'detection_history', ['created_at'])
    op.create_index('ix_detection_history_user_id_status', 'detection_history', ['user_id', 'status'])
    op.create_index('ix_detection_history_user_id_created_at', 'detection_history', ['user_id', 'created_at'])
    op.create_index('ix_detection_history_input_type', 'detection_history', ['input_type'])


def downgrade() -> None:
    """Downgrade schema - Remove performance indexes."""

    # Detection History table indexes
    op.drop_index('ix_detection_history_input_type', table_name='detection_history')
    op.drop_index('ix_detection_history_user_id_created_at', table_name='detection_history')
    op.drop_index('ix_detection_history_user_id_status', table_name='detection_history')
    op.drop_index('ix_detection_history_created_at', table_name='detection_history')

    # ML Models table indexes
    op.drop_index('ix_ml_models_status_created_at', table_name='ml_models')
    op.drop_index('ix_ml_models_created_at', table_name='ml_models')
    op.drop_index('ix_ml_models_uploaded_by', table_name='ml_models')
    op.drop_index('ix_ml_models_status', table_name='ml_models')

    # Users table indexes
    op.drop_index('ix_users_role', table_name='users')
