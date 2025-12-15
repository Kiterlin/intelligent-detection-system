"""
检测结果对比 API 端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.crud.detection import crud_detection_history
from app.services.comparison_service import ComparisonService
from app.schemas.comparison import ComparisonResponse
from loguru import logger

router = APIRouter()


@router.get("/compare", response_model=ComparisonResponse)
async def compare_detections(
    ids: str = Query(
        ...,
        description="检测记录ID列表，用逗号分隔（例如：1,2,3）",
        example="1,2"
    ),
    iou_threshold: float = Query(
        0.5,
        ge=0.0,
        le=1.0,
        description="IOU阈值，用于判断对象匹配"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    对比多个检测结果

    支持2-4个检测结果的对比分析，返回：
    - 共同检测到的对象
    - 各自独有的对象
    - 统计对比信息
    - 匹配率等指标

    当前版本仅支持2个结果的详细对比
    """
    try:
        # 解析ID列表
        try:
            detection_ids = [int(id_str.strip()) for id_str in ids.split(',')]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID格式错误，应为用逗号分隔的数字"
            )

        # 验证数量
        if len(detection_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="至少需要2个检测结果进行对比"
            )

        if len(detection_ids) > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="最多支持4个检测结果的对比"
            )

        # 去重
        detection_ids = list(dict.fromkeys(detection_ids))

        # 获取所有检测记录
        records = []
        for detection_id in detection_ids:
            record = await crud_detection_history.get_detection_by_id(db, detection_id)

            if not record:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"检测记录 {detection_id} 不存在"
                )

            # 验证用户权限
            if record.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权访问检测记录 {detection_id}"
                )

            # 验证记录已完成
            if not record.result_json:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"检测记录 {detection_id} 尚未完成或无结果数据"
                )

            records.append(record)

        logger.info(
            f"用户 {current_user.id} 对比检测结果: {detection_ids}"
        )

        # 创建对比服务
        comparison_service = ComparisonService(iou_threshold=iou_threshold)

        # 准备对比数据
        comparison_input = []
        for record in records:
            comparison_input.append({
                'detection_id': record.id,
                'result_json': record.result_json,
                'metadata': {
                    'model_id': record.model_id,
                    'input_type': record.input_type.value,
                    'processing_time': record.processing_time,
                    'confidence_threshold': record.confidence_threshold,
                    'iou_threshold': record.iou_threshold,
                    'created_at': record.created_at.isoformat(),
                }
            })

        # 执行对比
        comparison_result = comparison_service.compare_detections(comparison_input)

        # 如果是两个结果，添加统计对比
        if len(records) == 2:
            stats_comparison = comparison_service.calculate_statistics_comparison(
                {
                    'detected_objects_count': records[0].detected_objects_count,
                    'processing_time': records[0].processing_time,
                    'model_id': records[0].model_id,
                    'confidence_threshold': records[0].confidence_threshold,
                    'iou_threshold': records[0].iou_threshold,
                },
                {
                    'detected_objects_count': records[1].detected_objects_count,
                    'processing_time': records[1].processing_time,
                    'model_id': records[1].model_id,
                    'confidence_threshold': records[1].confidence_threshold,
                    'iou_threshold': records[1].iou_threshold,
                }
            )

            return ComparisonResponse(
                **comparison_result,
                statistics=stats_comparison
            )
        else:
            return ComparisonResponse(**comparison_result)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"对比参数错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"对比检测结果失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对比失败: {str(e)}"
        )
