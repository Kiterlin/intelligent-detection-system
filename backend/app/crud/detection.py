"""
检测历史 CRUD 操作
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.exc import IntegrityError

from app.models.detection_history import (
    DetectionHistory,
    DetectionInputType,
    DetectionStatus,
)


async def get_detection_by_id(
    db: AsyncSession, detection_id: int
) -> Optional[DetectionHistory]:
    """
    根据ID获取检测记录

    Args:
        db: 数据库会话
        detection_id: 检测记录ID

    Returns:
        Optional[DetectionHistory]: 检测记录对象，不存在则返回None
    """
    result = await db.execute(
        select(DetectionHistory).where(DetectionHistory.id == detection_id)
    )
    return result.scalar_one_or_none()


async def get_detection_by_task_id(
    db: AsyncSession, task_id: str
) -> Optional[DetectionHistory]:
    """
    根据任务ID获取检测记录

    Args:
        db: 数据库会话
        task_id: Celery任务ID

    Returns:
        Optional[DetectionHistory]: 检测记录对象，不存在则返回None
    """
    result = await db.execute(
        select(DetectionHistory).where(DetectionHistory.task_id == task_id)
    )
    return result.scalar_one_or_none()


async def get_detections_with_filter(
    db: AsyncSession,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    input_type: Optional[DetectionInputType] = None,
    status: Optional[DetectionStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> tuple[List[DetectionHistory], int]:
    """
    获取检测历史列表（支持筛选）

    Args:
        db: 数据库会话
        user_id: 用户ID（如果提供，只返回该用户的记录）
        skip: 跳过的记录数
        limit: 返回的最大记录数
        input_type: 输入类型筛选
        status: 状态筛选
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        (检测记录列表, 总数) 元组
    """
    query = select(DetectionHistory)
    filters = []

    # 用户筛选
    if user_id:
        filters.append(DetectionHistory.user_id == user_id)

    # 输入类型筛选
    if input_type:
        filters.append(DetectionHistory.input_type == input_type)

    # 状态筛选
    if status:
        filters.append(DetectionHistory.status == status)

    # 日期范围筛选
    if start_date:
        filters.append(DetectionHistory.created_at >= start_date)
    if end_date:
        filters.append(DetectionHistory.created_at <= end_date)

    # 应用筛选条件
    if filters:
        query = query.where(and_(*filters))

    # 获取总数 - 使用优化的计数查询
    count_query = select(func.count(DetectionHistory.id))
    if filters:
        count_query = count_query.where(and_(*filters))
    total = await db.scalar(count_query)

    # 分页查询 - 按创建时间倒序排序（利用索引）
    query = query.offset(skip).limit(limit).order_by(DetectionHistory.created_at.desc())
    result = await db.execute(query)
    detections = list(result.scalars().all())

    return detections, total or 0


async def create_detection(
    db: AsyncSession,
    user_id: int,
    model_id: int,
    input_type: DetectionInputType,
    input_file_path: str,
    confidence_threshold: float,
    iou_threshold: float,
    task_id: Optional[str] = None,
) -> DetectionHistory:
    """
    创建新检测记录

    Args:
        db: 数据库会话
        user_id: 用户ID
        model_id: 模型ID
        input_type: 输入类型
        input_file_path: 输入文件路径
        confidence_threshold: 置信度阈值
        iou_threshold: IOU阈值
        task_id: Celery任务ID（用于异步任务）

    Returns:
        DetectionHistory: 创建的检测记录对象

    Raises:
        ValueError: 创建失败
    """
    db_detection = DetectionHistory(
        user_id=user_id,
        model_id=model_id,
        input_type=input_type,
        input_file_path=input_file_path,
        confidence_threshold=confidence_threshold,
        iou_threshold=iou_threshold,
        status=DetectionStatus.PENDING,
        task_id=task_id,
    )

    db.add(db_detection)
    try:
        await db.commit()
        await db.refresh(db_detection)
        return db_detection
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建检测记录失败：数据冲突")


async def update_detection_status(
    db: AsyncSession,
    detection_id: int,
    status: DetectionStatus,
    error_message: Optional[str] = None,
) -> Optional[DetectionHistory]:
    """
    更新检测状态

    Args:
        db: 数据库会话
        detection_id: 检测记录ID
        status: 新状态
        error_message: 错误信息（失败时提供）

    Returns:
        Optional[DetectionHistory]: 更新后的检测记录对象，不存在则返回None
    """
    detection = await get_detection_by_id(db, detection_id)
    if not detection:
        return None

    detection.status = status
    if error_message:
        detection.error_message = error_message

    await db.commit()
    await db.refresh(detection)
    return detection


async def update_detection_result(
    db: AsyncSession,
    detection_id: int,
    output_file_path: str,
    result_json: str,
    detected_objects_count: int,
    processing_time: float,
) -> Optional[DetectionHistory]:
    """
    更新检测结果

    Args:
        db: 数据库会话
        detection_id: 检测记录ID
        output_file_path: 输出文件路径
        result_json: 结果JSON字符串
        detected_objects_count: 检测到的对象数量
        processing_time: 处理时间（秒）

    Returns:
        Optional[DetectionHistory]: 更新后的检测记录对象，不存在则返回None
    """
    detection = await get_detection_by_id(db, detection_id)
    if not detection:
        return None

    detection.output_file_path = output_file_path
    detection.result_json = result_json
    detection.detected_objects_count = detected_objects_count
    detection.processing_time = processing_time
    detection.status = DetectionStatus.COMPLETED

    await db.commit()
    await db.refresh(detection)
    return detection


async def delete_detection(db: AsyncSession, detection_id: int) -> bool:
    """
    删除检测记录

    Args:
        db: 数据库会话
        detection_id: 检测记录ID

    Returns:
        bool: 是否删除成功
    """
    detection = await get_detection_by_id(db, detection_id)
    if not detection:
        return False

    await db.delete(detection)
    await db.commit()
    return True


async def get_user_detection_stats(
    db: AsyncSession, user_id: int
) -> dict:
    """
    获取用户检测统计信息

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        dict: 统计信息字典
    """
    # 总检测次数
    total = await db.scalar(
        select(func.count(DetectionHistory.id)).where(
            DetectionHistory.user_id == user_id
        )
    )

    # 图像检测次数
    image_count = await db.scalar(
        select(func.count(DetectionHistory.id)).where(
            and_(
                DetectionHistory.user_id == user_id,
                DetectionHistory.input_type == DetectionInputType.IMAGE,
            )
        )
    )

    # 视频检测次数
    video_count = await db.scalar(
        select(func.count(DetectionHistory.id)).where(
            and_(
                DetectionHistory.user_id == user_id,
                DetectionHistory.input_type == DetectionInputType.VIDEO,
            )
        )
    )

    # 总检测对象数
    total_objects = await db.scalar(
        select(func.sum(DetectionHistory.detected_objects_count)).where(
            DetectionHistory.user_id == user_id
        )
    )

    # 平均处理时间
    avg_time = await db.scalar(
        select(func.avg(DetectionHistory.processing_time)).where(
            and_(
                DetectionHistory.user_id == user_id,
                DetectionHistory.status == DetectionStatus.COMPLETED,
            )
        )
    )

    return {
        "total_detections": total or 0,
        "image_detections": image_count or 0,
        "video_detections": video_count or 0,
        "total_objects_detected": int(total_objects or 0),
        "avg_processing_time": float(avg_time) if avg_time else None,
    }


async def get_dashboard_stats(
    db: AsyncSession, user_id: int
) -> dict:
    """
    获取用户仪表盘统计信息

    包含总检测数、本周检测数、总对象数、最常检测类别、模型使用情况、最近活动

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        dict: 仪表盘统计信息
    """
    import json
    from datetime import timedelta

    # 当前时间
    now = datetime.now()
    week_ago = now - timedelta(days=7)

    # 1. 总检测次数
    total_detections = await db.scalar(
        select(func.count(DetectionHistory.id)).where(
            DetectionHistory.user_id == user_id
        )
    ) or 0

    # 2. 本周检测次数（视频）
    weekly_videos = await db.scalar(
        select(func.count(DetectionHistory.id)).where(
            and_(
                DetectionHistory.user_id == user_id,
                DetectionHistory.input_type == DetectionInputType.VIDEO,
                DetectionHistory.created_at >= week_ago
            )
        )
    ) or 0

    # 3. 总对象数
    total_objects = await db.scalar(
        select(func.sum(DetectionHistory.detected_objects_count)).where(
            DetectionHistory.user_id == user_id
        )
    ) or 0

    # 4. 最常检测类别（从所有result_json中统计）
    result = await db.execute(
        select(DetectionHistory.result_json).where(
            and_(
                DetectionHistory.user_id == user_id,
                DetectionHistory.status == DetectionStatus.COMPLETED,
                DetectionHistory.result_json.isnot(None)
            )
        )
    )

    class_counts = {}
    for row in result:
        if row[0]:
            try:
                result_data = json.loads(row[0])
                # 兼容新旧格式
                if isinstance(result_data, dict):
                    detections = result_data.get("detections", [])
                elif isinstance(result_data, list):
                    detections = result_data
                else:
                    detections = []

                for det in detections:
                    class_name = det.get('class_name', det.get('class', 'Unknown'))
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
            except (json.JSONDecodeError, TypeError):
                continue

    most_detected_class = max(class_counts.items(), key=lambda x: x[1])[0] if class_counts else "无"

    # 5. 模型使用统计
    from app.models.ml_model import MLModel
    model_usage_result = await db.execute(
        select(
            MLModel.name,
            func.count(DetectionHistory.id).label('count')
        ).join(
            DetectionHistory, DetectionHistory.model_id == MLModel.id
        ).where(
            DetectionHistory.user_id == user_id
        ).group_by(
            MLModel.id, MLModel.name
        )
    )

    model_usage = [
        {"model_name": row.name, "count": row.count}
        for row in model_usage_result
    ]

    # 6. 最近5条检测活动
    recent_result = await db.execute(
        select(DetectionHistory).where(
            DetectionHistory.user_id == user_id
        ).order_by(
            DetectionHistory.created_at.desc()
        ).limit(5)
    )

    recent_activities = []
    for detection in recent_result.scalars():
        recent_activities.append({
            "id": detection.id,
            "input_type": detection.input_type.value,
            "status": detection.status.value,
            "detected_count": detection.detected_objects_count or 0,
            "created_at": detection.created_at.isoformat(),
        })

    return {
        "total_detections": int(total_detections),
        "weekly_videos": int(weekly_videos),
        "total_objects": int(total_objects),
        "most_detected_class": most_detected_class,
        "model_usage": model_usage,
        "recent_activities": recent_activities,
    }
