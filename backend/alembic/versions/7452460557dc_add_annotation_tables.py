"""add_annotation_tables

Revision ID: 7452460557dc
Revises: a8e107ea9d96
Create Date: 2025-11-15 10:58:17.236342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7452460557dc'
down_revision: Union[str, Sequence[str], None] = 'a8e107ea9d96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create annotation_tasks table
    op.create_table(
        'annotation_tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=False, comment='任务名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='任务描述'),
        sa.Column('label_studio_project_id', sa.Integer(), nullable=True, comment='Label Studio 项目 ID'),
        sa.Column('label_studio_project_url', sa.String(length=500), nullable=True, comment='Label Studio 项目 URL'),
        sa.Column('dataset_id', sa.Integer(), nullable=True, comment='关联的数据集 ID'),
        sa.Column('detection_history_id', sa.Integer(), nullable=True, comment='关联的检测记录 ID'),
        sa.Column('labeling_config', sa.Text(), nullable=True, comment='标注配置（XML）'),
        sa.Column('class_labels', sa.JSON(), nullable=True, comment='类别标签列表'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='任务状态'),
        sa.Column('total_tasks', sa.Integer(), nullable=False, server_default='0', comment='总任务数'),
        sa.Column('completed_tasks', sa.Integer(), nullable=False, server_default='0', comment='已完成任务数'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0', comment='完成进度（百分比）'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false', comment='是否已发布'),
        sa.Column('requires_review', sa.Boolean(), nullable=False, server_default='false', comment='是否需要审核'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='创建者'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['detection_history_id'], ['detection_history.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for annotation_tasks
    op.create_index('ix_annotation_tasks_status', 'annotation_tasks', ['status'])
    op.create_index('ix_annotation_tasks_dataset_id', 'annotation_tasks', ['dataset_id'])
    op.create_index('ix_annotation_tasks_created_by', 'annotation_tasks', ['created_by'])

    # Create annotations table
    op.create_table(
        'annotations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer(), nullable=False, comment='所属标注任务 ID'),
        sa.Column('label_studio_task_id', sa.Integer(), nullable=True, comment='Label Studio 任务 ID'),
        sa.Column('label_studio_annotation_id', sa.Integer(), nullable=True, comment='Label Studio 标注 ID'),
        sa.Column('image_path', sa.String(length=500), nullable=False, comment='图片路径'),
        sa.Column('image_name', sa.String(length=255), nullable=True, comment='图片名称'),
        sa.Column('image_width', sa.Integer(), nullable=True, comment='图片宽度'),
        sa.Column('image_height', sa.Integer(), nullable=True, comment='图片高度'),
        sa.Column('annotations_data', sa.JSON(), nullable=True, comment='标注数据（Label Studio 格式）'),
        sa.Column('predictions_data', sa.JSON(), nullable=True, comment='预标注数据（来自检测结果）'),
        sa.Column('object_count', sa.Integer(), nullable=False, server_default='0', comment='标注目标数量'),
        sa.Column('annotation_time_seconds', sa.Integer(), nullable=True, comment='标注耗时（秒）'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='状态'),
        sa.Column('quality_score', sa.Integer(), nullable=True, comment='标注质量评分 (0-100)'),
        sa.Column('is_difficult', sa.Boolean(), nullable=False, server_default='false', comment='是否为困难样本'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false', comment='是否已审核'),
        sa.Column('annotated_by', sa.Integer(), nullable=True, comment='标注者'),
        sa.Column('verified_by', sa.Integer(), nullable=True, comment='审核者'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('annotated_at', sa.DateTime(timezone=True), nullable=True, comment='标注完成时间'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True, comment='审核时间'),
        sa.ForeignKeyConstraint(['task_id'], ['annotation_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['annotated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for annotations
    op.create_index('ix_annotations_task_id', 'annotations', ['task_id'])
    op.create_index('ix_annotations_status', 'annotations', ['status'])
    op.create_index('ix_annotations_annotated_by', 'annotations', ['annotated_by'])

    # Create annotation_exports table
    op.create_table(
        'annotation_exports',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer(), nullable=False, comment='标注任务 ID'),
        sa.Column('export_format', sa.String(length=50), nullable=False, comment='导出格式'),
        sa.Column('export_options', sa.JSON(), nullable=True, comment='导出选项'),
        sa.Column('file_path', sa.String(length=500), nullable=True, comment='导出文件路径'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True, comment='文件大小（字节）'),
        sa.Column('exported_count', sa.Integer(), nullable=True, comment='导出的标注数量'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending', comment='导出状态'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息（如果失败）'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='导出创建者'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True, comment='完成时间'),
        sa.ForeignKeyConstraint(['task_id'], ['annotation_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for annotation_exports
    op.create_index('ix_annotation_exports_task_id', 'annotation_exports', ['task_id'])
    op.create_index('ix_annotation_exports_status', 'annotation_exports', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes and tables in reverse order
    op.drop_index('ix_annotation_exports_status', table_name='annotation_exports')
    op.drop_index('ix_annotation_exports_task_id', table_name='annotation_exports')
    op.drop_table('annotation_exports')

    op.drop_index('ix_annotations_annotated_by', table_name='annotations')
    op.drop_index('ix_annotations_status', table_name='annotations')
    op.drop_index('ix_annotations_task_id', table_name='annotations')
    op.drop_table('annotations')

    op.drop_index('ix_annotation_tasks_created_by', table_name='annotation_tasks')
    op.drop_index('ix_annotation_tasks_dataset_id', table_name='annotation_tasks')
    op.drop_index('ix_annotation_tasks_status', table_name='annotation_tasks')
    op.drop_table('annotation_tasks')
