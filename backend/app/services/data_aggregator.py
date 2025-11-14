"""
报告数据聚合服务
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from app.models.detection_history import DetectionHistory, DetectionInputType, DetectionStatus
from app.models.ml_model import MLModel


class ReportDataAggregator:
    """报告数据聚合服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def aggregate_detection_data(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        dataset_id: Optional[int] = None,
        model_id: Optional[int] = None,
        detection_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        聚合检测数据用于报告生成

        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            dataset_id: 数据集ID（可选）
            model_id: 模型ID（可选）
            detection_type: 检测类型（可选）

        Returns:
            聚合后的数据字典
        """
        # 构建基础查询条件
        conditions = [
            DetectionHistory.user_id == user_id,
            DetectionHistory.status == DetectionStatus.COMPLETED
        ]

        if start_date:
            conditions.append(DetectionHistory.created_at >= start_date)
        if end_date:
            conditions.append(DetectionHistory.created_at <= end_date)
        if model_id:
            conditions.append(DetectionHistory.model_id == model_id)
        if detection_type:
            conditions.append(DetectionHistory.input_type == detection_type)

        # 1. 获取总体统计
        total_stats = await self._get_total_stats(conditions)

        # 2. 获取类别分布
        class_distribution = await self._get_class_distribution(conditions)

        # 3. 获取时间趋势
        time_trend = await self._get_time_trend(conditions, start_date, end_date)

        # 4. 获取模型使用统计
        model_usage = await self._get_model_usage(conditions)

        # 5. 获取最近检测记录
        recent_detections = await self._get_recent_detections(conditions, limit=10)

        return {
            'total_stats': total_stats,
            'class_distribution': class_distribution,
            'time_trend': time_trend,
            'model_usage': model_usage,
            'recent_detections': recent_detections,
            'parameters': {
                'user_id': user_id,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'dataset_id': dataset_id,
                'model_id': model_id,
                'detection_type': detection_type
            }
        }

    async def _get_total_stats(self, conditions: List) -> Dict[str, Any]:
        """获取总体统计"""
        # 总检测次数
        count_query = select(func.count(DetectionHistory.id)).where(and_(*conditions))
        total_detections = (await self.db.execute(count_query)).scalar()

        # 总检测对象数
        objects_query = select(func.sum(DetectionHistory.detected_objects_count)).where(and_(*conditions))
        total_objects = (await self.db.execute(objects_query)).scalar() or 0

        # 平均处理时间
        avg_time_query = select(func.avg(DetectionHistory.processing_time)).where(and_(*conditions))
        avg_processing_time = (await self.db.execute(avg_time_query)).scalar() or 0

        # 图片和视频数量
        image_query = select(func.count(DetectionHistory.id)).where(
            and_(*conditions, DetectionHistory.input_type == DetectionInputType.IMAGE)
        )
        image_count = (await self.db.execute(image_query)).scalar()

        video_query = select(func.count(DetectionHistory.id)).where(
            and_(*conditions, DetectionHistory.input_type == DetectionInputType.VIDEO)
        )
        video_count = (await self.db.execute(video_query)).scalar()

        return {
            'total_detections': total_detections or 0,
            'total_objects': int(total_objects),
            'avg_processing_time': round(float(avg_processing_time), 2),
            'image_count': image_count or 0,
            'video_count': video_count or 0
        }

    async def _get_class_distribution(self, conditions: List) -> Dict[str, int]:
        """获取类别分布"""
        # 查询所有检测记录的 result_json
        query = select(DetectionHistory.result_json).where(and_(*conditions))
        result = await self.db.execute(query)
        result_jsons = result.scalars().all()

        # 解析并统计类别
        class_counter = Counter()
        for result_json_str in result_jsons:
            if not result_json_str:
                continue

            try:
                result_data = json.loads(result_json_str)

                # 支持多种 JSON 格式
                if isinstance(result_data, dict):
                    detections = result_data.get('detections', [])
                elif isinstance(result_data, list):
                    detections = result_data
                else:
                    continue

                for detection in detections:
                    if isinstance(detection, dict):
                        class_name = detection.get('class') or detection.get('class_name', 'unknown')
                        class_counter[class_name] += 1

            except (json.JSONDecodeError, AttributeError):
                continue

        return dict(class_counter.most_common())

    async def _get_time_trend(
        self,
        conditions: List,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """获取时间趋势"""
        # 如果没有指定日期范围，使用最近30天
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # 按日期分组统计
        query = (
            select(
                func.date(DetectionHistory.created_at).label('date'),
                func.count(DetectionHistory.id).label('count')
            )
            .where(and_(*conditions))
            .group_by(func.date(DetectionHistory.created_at))
            .order_by(func.date(DetectionHistory.created_at))
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {'date': str(row.date), 'count': row.count}
            for row in rows
        ]

    async def _get_model_usage(self, conditions: List) -> List[Dict[str, Any]]:
        """获取模型使用统计"""
        query = (
            select(
                MLModel.id,
                MLModel.name,
                func.count(DetectionHistory.id).label('usage_count')
            )
            .join(DetectionHistory, DetectionHistory.model_id == MLModel.id)
            .where(and_(*conditions))
            .group_by(MLModel.id, MLModel.name)
            .order_by(func.count(DetectionHistory.id).desc())
        )

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {'model_id': row.id, 'model_name': row.name, 'usage_count': row.usage_count}
            for row in rows
        ]

    async def _get_recent_detections(
        self,
        conditions: List,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近的检测记录"""
        query = (
            select(DetectionHistory)
            .where(and_(*conditions))
            .order_by(DetectionHistory.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        detections = result.scalars().all()

        return [
            {
                'id': d.id,
                'input_type': d.input_type.value,
                'detected_objects_count': d.detected_objects_count,
                'processing_time': d.processing_time,
                'created_at': d.created_at.isoformat() if d.created_at else None
            }
            for d in detections
        ]

    async def aggregate_comparison_data(
        self,
        user_id: int,
        model_ids: List[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        dataset_id: Optional[int] = None,
        detection_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        聚合多模型对比数据

        Args:
            user_id: 用户ID
            model_ids: 要对比的模型ID列表
            start_date: 开始日期
            end_date: 结束日期
            dataset_id: 数据集ID（可选）
            detection_type: 检测类型（可选）

        Returns:
            对比数据字典
        """
        # 为每个模型聚合数据
        models_compared = []

        for model_id in model_ids:
            # 构建查询条件
            conditions = [
                DetectionHistory.user_id == user_id,
                DetectionHistory.status == DetectionStatus.COMPLETED,
                DetectionHistory.model_id == model_id
            ]

            if start_date:
                conditions.append(DetectionHistory.created_at >= start_date)
            if end_date:
                conditions.append(DetectionHistory.created_at <= end_date)
            if detection_type:
                conditions.append(DetectionHistory.input_type == detection_type)

            # 获取该模型的统计数据
            stats = await self._get_total_stats(conditions)

            # 获取模型名称
            model_query = select(MLModel.name).where(MLModel.id == model_id)
            model_name = (await self.db.execute(model_query)).scalar() or f"Model {model_id}"

            models_compared.append({
                'model_id': model_id,
                'model_name': model_name,
                **stats
            })

        # 获取类别对比数据（所有模型）
        class_comparison = await self._get_class_comparison(
            user_id, model_ids, start_date, end_date, detection_type
        )

        return {
            'models_compared': models_compared,
            'class_comparison': class_comparison,
            'parameters': {
                'user_id': user_id,
                'model_ids': model_ids,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'dataset_id': dataset_id,
                'detection_type': detection_type
            }
        }

    async def _get_class_comparison(
        self,
        user_id: int,
        model_ids: List[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        detection_type: Optional[str]
    ) -> Dict[str, Dict[str, int]]:
        """获取各模型的类别检测对比数据"""
        class_comparison = {}

        for model_id in model_ids:
            # 构建查询条件
            conditions = [
                DetectionHistory.user_id == user_id,
                DetectionHistory.status == DetectionStatus.COMPLETED,
                DetectionHistory.model_id == model_id
            ]

            if start_date:
                conditions.append(DetectionHistory.created_at >= start_date)
            if end_date:
                conditions.append(DetectionHistory.created_at <= end_date)
            if detection_type:
                conditions.append(DetectionHistory.input_type == detection_type)

            # 获取该模型的类别分布
            class_dist = await self._get_class_distribution(conditions)

            # 获取模型名称
            model_query = select(MLModel.name).where(MLModel.id == model_id)
            model_name = (await self.db.execute(model_query)).scalar() or f"Model {model_id}"

            # 将该模型的类别数据添加到对比中
            for class_name, count in class_dist.items():
                if class_name not in class_comparison:
                    class_comparison[class_name] = {}
                class_comparison[class_name][model_name] = count

        return class_comparison
