"""
标注相关数据库模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AnnotationTask(Base):
    """标注任务表"""
    __tablename__ = "annotation_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="任务名称")
    description = Column(Text, comment="任务描述")

    # Label Studio 集成
    label_studio_project_id = Column(Integer, comment="Label Studio 项目 ID")
    label_studio_project_url = Column(String(500), comment="Label Studio 项目 URL")

    # 关联数据
    dataset_id = Column(
        Integer,
        ForeignKey("datasets.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联的数据集 ID"
    )
    detection_history_id = Column(
        Integer,
        ForeignKey("detection_history.id", ondelete="SET NULL"),
        nullable=True,
        comment="关联的检测记录 ID"
    )

    # 任务配置
    labeling_config = Column(Text, comment="标注配置（XML）")
    class_labels = Column(JSON, comment="类别标签列表")

    # 状态管理
    status = Column(
        String(50),
        default="pending",
        index=True,
        comment="任务状态: pending, in_progress, completed, archived"
    )
    total_tasks = Column(Integer, default=0, comment="总任务数")
    completed_tasks = Column(Integer, default=0, comment="已完成任务数")
    progress = Column(Integer, default=0, comment="完成进度（百分比）")

    # 审核状态
    is_published = Column(Boolean, default=False, comment="是否已发布")
    requires_review = Column(Boolean, default=False, comment="是否需要审核")

    # 用户关联
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="创建者"
    )

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")

    # 关系
    annotations = relationship(
        "Annotation",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    creator = relationship("User", foreign_keys=[created_by])
    dataset = relationship("Dataset", foreign_keys=[dataset_id])

    def __repr__(self):
        return f"<AnnotationTask(id={self.id}, name='{self.name}', status='{self.status}')>"


class Annotation(Base):
    """标注记录表"""
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)

    # 任务关联
    task_id = Column(
        Integer,
        ForeignKey("annotation_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属标注任务 ID"
    )

    # Label Studio 集成
    label_studio_task_id = Column(Integer, comment="Label Studio 任务 ID")
    label_studio_annotation_id = Column(Integer, comment="Label Studio 标注 ID")

    # 图片信息
    image_path = Column(String(500), nullable=False, comment="图片路径")
    image_name = Column(String(255), comment="图片名称")
    image_width = Column(Integer, comment="图片宽度")
    image_height = Column(Integer, comment="图片高度")

    # 标注数据
    annotations_data = Column(JSON, comment="标注数据（Label Studio 格式）")
    predictions_data = Column(JSON, comment="预标注数据（来自检测结果）")

    # 标注统计
    object_count = Column(Integer, default=0, comment="标注目标数量")
    annotation_time_seconds = Column(Integer, comment="标注耗时（秒）")

    # 状态管理
    status = Column(
        String(50),
        default="pending",
        index=True,
        comment="状态: pending, annotated, verified, rejected"
    )

    # 质量控制
    quality_score = Column(Integer, comment="标注质量评分 (0-100)")
    is_difficult = Column(Boolean, default=False, comment="是否为困难样本")
    is_verified = Column(Boolean, default=False, comment="是否已审核")

    # 用户信息
    annotated_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="标注者"
    )
    verified_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="审核者"
    )

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )
    annotated_at = Column(DateTime(timezone=True), nullable=True, comment="标注完成时间")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="审核时间")

    # 关系
    task = relationship("AnnotationTask", back_populates="annotations")
    annotator = relationship("User", foreign_keys=[annotated_by])
    verifier = relationship("User", foreign_keys=[verified_by])

    def __repr__(self):
        return f"<Annotation(id={self.id}, task_id={self.task_id}, status='{self.status}')>"


class AnnotationExport(Base):
    """标注导出记录表"""
    __tablename__ = "annotation_exports"

    id = Column(Integer, primary_key=True, index=True)

    # 任务关联
    task_id = Column(
        Integer,
        ForeignKey("annotation_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="标注任务 ID"
    )

    # 导出配置
    export_format = Column(
        String(50),
        nullable=False,
        comment="导出格式: yolo, coco, label_studio_json"
    )
    export_options = Column(JSON, comment="导出选项（如是否包含未标注样本等）")

    # 导出结果
    file_path = Column(String(500), comment="导出文件路径")
    file_size_bytes = Column(Integer, comment="文件大小（字节）")
    exported_count = Column(Integer, comment="导出的标注数量")

    # 状态
    status = Column(
        String(50),
        default="pending",
        comment="导出状态: pending, processing, completed, failed"
    )
    error_message = Column(Text, comment="错误信息（如果失败）")

    # 用户信息
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="导出创建者"
    )

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")

    # 关系
    task = relationship("AnnotationTask")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<AnnotationExport(id={self.id}, format='{self.export_format}', status='{self.status}')>"
