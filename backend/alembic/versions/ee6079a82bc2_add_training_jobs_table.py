"""add_training_jobs_table

Revision ID: ee6079a82bc2
Revises: 7452460557dc
Create Date: 2025-11-15 11:20:37.709671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee6079a82bc2'
down_revision: Union[str, Sequence[str], None] = '7452460557dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 training_jobs 表
    op.create_table(
        'training_jobs',
        # 主键
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),

        # 关联字段
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('base_model_id', sa.Integer(), nullable=False),
        sa.Column('new_model_id', sa.Integer(), nullable=True),

        # 基本信息
        sa.Column('job_name', sa.String(length=200), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),

        # 训练配置
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('dataset_config', sa.JSON(), nullable=True),

        # 输出文件路径
        sa.Column('log_file_path', sa.String(length=500), nullable=True),
        sa.Column('weights_path', sa.String(length=500), nullable=True),
        sa.Column('results_path', sa.String(length=500), nullable=True),

        # 性能指标
        sa.Column('metrics_json', sa.JSON(), nullable=True),

        # 进度跟踪
        sa.Column('current_epoch', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_epochs', sa.Integer(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=True, server_default='0'),

        # 错误信息
        sa.Column('error_message', sa.Text(), nullable=True),

        # 时间戳
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),

        # 外键约束
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['base_model_id'], ['ml_models.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['new_model_id'], ['ml_models.id'], ondelete='SET NULL'),
    )

    # 创建索引
    op.create_index('ix_training_jobs_admin_id', 'training_jobs', ['admin_id'])
    op.create_index('ix_training_jobs_status', 'training_jobs', ['status'])
    op.create_index('ix_training_jobs_created_at', 'training_jobs', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    # 删除索引
    op.drop_index('ix_training_jobs_created_at', table_name='training_jobs')
    op.drop_index('ix_training_jobs_status', table_name='training_jobs')
    op.drop_index('ix_training_jobs_admin_id', table_name='training_jobs')

    # 删除表
    op.drop_table('training_jobs')
