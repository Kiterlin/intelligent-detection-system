"""
标注管理 API
提供标注任务的创建、查询、更新等功能
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.api.deps import get_current_user, get_db
from app.crud.annotation import crud_annotation_task, crud_annotation, crud_annotation_export
from app.crud.detection import crud_detection_history
from app.models.user import User
from app.schemas.annotation import (
    AnnotationTaskCreate,
    AnnotationTaskUpdate,
    AnnotationTaskResponse,
    AnnotationTaskListResponse,
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse,
    AnnotationListResponse,
    AnnotationExportCreate,
    AnnotationExportResponse,
    AnnotationTaskStatistics,
)
from loguru import logger
from app.services.label_studio_service import label_studio_service
from app.services.annotation_converter import annotation_converter
from app.tasks.annotation_tasks import (
    export_annotations_yolo_task,
    export_annotations_coco_task,
    export_annotations_label_studio_task
)

router = APIRouter()


# ============ AnnotationTask 路由 ============

@router.post("/tasks", response_model=AnnotationTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_in: AnnotationTaskCreate
):
    """
    创建标注任务

    - **name**: 任务名称（必填）
    - **description**: 任务描述
    - **dataset_id**: 关联的数据集 ID
    - **detection_history_id**: 关联的检测记录 ID
    - **class_labels**: 类别标签列表
    - **requires_review**: 是否需要审核

    自动创建 Label Studio 项目并关联
    """
    try:
        # 先创建数据库任务记录
        task = await crud_annotation_task.create(
            db=db,
            obj_in=task_in,
            created_by=current_user.id
        )

        # 尝试创建 Label Studio 项目
        try:
            # 生成 Label Studio 配置
            if task.class_labels:
                label_config = label_studio_service.get_labeling_config_for_classes(
                    task.class_labels
                )
            else:
                label_config = None

            # 创建 Label Studio 项目
            ls_project = label_studio_service.create_project(
                title=f"{task.name} (ID: {task.id})",
                description=task.description or "",
                label_config=label_config
            )

            # 更新任务记录，保存 Label Studio 项目信息
            from app.schemas.annotation import AnnotationTaskUpdate
            task_update = AnnotationTaskUpdate(
                label_studio_project_id=ls_project['id'],
                label_studio_url=f"{label_studio_service.url}/projects/{ls_project['id']}"
            )
            task = await crud_annotation_task.update(db=db, db_obj=task, obj_in=task_update)

            logger.info(
                f"创建 Label Studio 项目成功: "
                f"任务 {task.id} -> Label Studio 项目 {ls_project['id']}"
            )

        except Exception as ls_error:
            # Label Studio 创建失败不影响任务创建，仅记录警告
            logger.warning(
                f"创建 Label Studio 项目失败（任务 {task.id} 已创建）: {str(ls_error)}"
            )

        # 获取统计信息
        stats = await crud_annotation_task.get_task_statistics(db, task.id)

        logger.info(f"用户 {current_user.username} 创建了标注任务: {task.name} (ID: {task.id})")

        return AnnotationTaskResponse(**task.__dict__, **stats)

    except Exception as e:
        logger.error(f"创建标注任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建标注任务失败: {str(e)}"
        )


@router.get("/tasks", response_model=AnnotationTaskListResponse)
async def list_annotation_tasks(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="任务状态筛选"),
    created_by_me: bool = Query(False, description="只查看我创建的任务")
):
    """
    获取标注任务列表（分页）

    - **skip**: 跳过的记录数（默认 0）
    - **limit**: 返回的记录数（默认 100，最大 100）
    - **status**: 筛选状态（pending/in_progress/completed/archived）
    - **created_by_me**: 是否只查看我创建的任务
    """
    try:
        created_by = current_user.id if created_by_me else None

        tasks, total = await crud_annotation_task.get_multi(
            db=db,
            skip=skip,
            limit=limit,
            created_by=created_by,
            status=status
        )

        # 为每个任务添加统计信息
        items = []
        for task in tasks:
            stats = await crud_annotation_task.get_task_statistics(db, task.id)
            items.append(AnnotationTaskResponse(**task.__dict__, **stats))

        return AnnotationTaskListResponse(total=total, items=items)

    except Exception as e:
        logger.error(f"获取标注任务列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取标注任务列表失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=AnnotationTaskResponse)
async def get_annotation_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int
):
    """获取单个标注任务详情"""
    task = await crud_annotation_task.get(db=db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    # 获取统计信息
    stats = await crud_annotation_task.get_task_statistics(db, task.id)

    return AnnotationTaskResponse(**task.__dict__, **stats)


@router.put("/tasks/{task_id}", response_model=AnnotationTaskResponse)
async def update_annotation_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int,
    task_in: AnnotationTaskUpdate
):
    """更新标注任务"""
    task = await crud_annotation_task.get(db=db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    # 检查权限（只有创建者或管理员可以更新）
    if task.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此标注任务"
        )

    try:
        task = await crud_annotation_task.update(db=db, db_obj=task, obj_in=task_in)
        stats = await crud_annotation_task.get_task_statistics(db, task.id)

        logger.info(f"用户 {current_user.username} 更新了标注任务 {task_id}")

        return AnnotationTaskResponse(**task.__dict__, **stats)

    except Exception as e:
        logger.error(f"更新标注任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新标注任务失败: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation_task(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int
):
    """删除标注任务（级联删除所有标注记录）"""
    task = await crud_annotation_task.get(db=db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    # 检查权限（只有创建者或管理员可以删除）
    if task.created_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此标注任务"
        )

    try:
        await crud_annotation_task.delete(db=db, task_id=task_id)
        logger.info(f"用户 {current_user.username} 删除了标注任务 {task_id}")

    except Exception as e:
        logger.error(f"删除标注任务失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除标注任务失败: {str(e)}"
        )


@router.post("/tasks/{task_id}/import-detections")
async def import_detection_results(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int
):
    """
    导入检测结果作为预标注

    从关联的检测记录中导入检测框作为 Label Studio 的预标注数据
    """
    task = await crud_annotation_task.get(db=db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    # 检查是否有关联的检测记录
    if not task.detection_history_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该标注任务没有关联的检测记录"
        )

    # 检查是否有 Label Studio 项目
    if not task.label_studio_project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该标注任务没有关联的 Label Studio 项目"
        )

    try:
        # 获取检测记录
        detection = await crud_detection_history.get(db=db, history_id=task.detection_history_id)
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"检测记录 {task.detection_history_id} 不存在"
            )

        # 解析检测结果
        import json
        detection_results = json.loads(detection.detection_results) if isinstance(detection.detection_results, str) else detection.detection_results

        # 转换为 Label Studio 任务格式
        ls_tasks = []
        for result in detection_results.get('detections', []):
            # 假设每个检测结果包含 image_path, boxes 等信息
            image_path = result.get('image_path', '')
            boxes = result.get('boxes', [])

            if not image_path or not boxes:
                continue

            # 转换为 Label Studio 格式
            ls_task = annotation_converter.detection_to_label_studio(
                detection_boxes=boxes,
                image_path=image_path,
                image_url=result.get('image_url')  # 如果有公开 URL
            )
            ls_tasks.append(ls_task)

        if not ls_tasks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="检测结果中没有可导入的数据"
            )

        # 导入到 Label Studio
        import_result = label_studio_service.import_tasks(
            project_id=task.label_studio_project_id,
            tasks=ls_tasks
        )

        # 创建本地标注记录
        annotations_to_create = []
        for ls_task in ls_tasks:
            annotation_data = AnnotationCreate(
                task_id=task_id,
                image_path=ls_task['data']['image'],
                status='pending',
                annotations_data=ls_task.get('predictions', [])
            )
            annotations_to_create.append(annotation_data)

        # 批量创建标注记录
        created_annotations = await crud_annotation.batch_create(
            db=db,
            annotations=annotations_to_create
        )

        logger.info(
            f"成功导入 {len(ls_tasks)} 个检测结果到标注任务 {task_id} "
            f"(Label Studio 项目: {task.label_studio_project_id})"
        )

        return {
            "success": True,
            "message": f"成功导入 {len(ls_tasks)} 个检测结果",
            "imported_count": len(created_annotations),
            "label_studio_result": import_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导入检测结果失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入检测结果失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/statistics", response_model=AnnotationTaskStatistics)
async def get_task_statistics(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int
):
    """获取标注任务的详细统计信息"""
    task = await crud_annotation_task.get(db=db, task_id=task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    stats = await crud_annotation_task.get_task_statistics(db, task.id)

    # 计算进度百分比
    total = stats['annotation_count']
    annotated = stats['annotated_count']
    progress = (annotated / total * 100) if total > 0 else 0

    return AnnotationTaskStatistics(
        task_id=task.id,
        task_name=task.name,
        total_annotations=total,
        pending_annotations=stats['pending_count'],
        annotated_annotations=annotated,
        verified_annotations=stats.get('verified_count', 0),
        progress_percentage=round(progress, 2)
    )


# ============ Annotation 路由 ============

@router.get("/tasks/{task_id}/annotations", response_model=AnnotationListResponse)
async def list_annotations(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None, description="筛选状态")
):
    """获取指定任务的标注记录列表"""
    # 检查任务是否存在
    task = await crud_annotation_task.get(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    annotations, total = await crud_annotation.get_multi_by_task(
        db=db,
        task_id=task_id,
        skip=skip,
        limit=limit,
        status=status
    )

    items = [AnnotationResponse(**ann.__dict__) for ann in annotations]
    return AnnotationListResponse(total=total, items=items)


@router.post("/tasks/{task_id}/annotations", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int,
    annotation_in: AnnotationCreate
):
    """创建标注记录"""
    # 检查任务是否存在
    task = await crud_annotation_task.get(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    # 设置 task_id
    annotation_in.task_id = task_id

    try:
        annotation = await crud_annotation.create(db=db, obj_in=annotation_in)
        logger.info(f"用户 {current_user.username} 在任务 {task_id} 中创建了标注记录 {annotation.id}")

        return AnnotationResponse(**annotation.__dict__)

    except Exception as e:
        logger.error(f"创建标注记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建标注记录失败: {str(e)}"
        )


@router.get("/annotations/{annotation_id}", response_model=AnnotationResponse)
async def get_annotation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    annotation_id: int
):
    """获取单个标注记录"""
    annotation = await crud_annotation.get(db=db, annotation_id=annotation_id)

    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注记录 {annotation_id} 不存在"
        )

    return AnnotationResponse(**annotation.__dict__)


@router.put("/annotations/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    annotation_id: int,
    annotation_in: AnnotationUpdate
):
    """更新标注记录"""
    annotation = await crud_annotation.get(db=db, annotation_id=annotation_id)

    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注记录 {annotation_id} 不存在"
        )

    try:
        annotation = await crud_annotation.update(
            db=db,
            db_obj=annotation,
            obj_in=annotation_in,
            annotated_by=current_user.id
        )

        logger.info(f"用户 {current_user.username} 更新了标注记录 {annotation_id}")

        return AnnotationResponse(**annotation.__dict__)

    except Exception as e:
        logger.error(f"更新标注记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新标注记录失败: {str(e)}"
        )


@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    annotation_id: int
):
    """删除标注记录"""
    annotation = await crud_annotation.get(db=db, annotation_id=annotation_id)

    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注记录 {annotation_id} 不存在"
        )

    try:
        await crud_annotation.delete(db=db, annotation_id=annotation_id)
        logger.info(f"用户 {current_user.username} 删除了标注记录 {annotation_id}")

    except Exception as e:
        logger.error(f"删除标注记录失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除标注记录失败: {str(e)}"
        )


# ============ AnnotationExport 路由 ============

@router.post("/tasks/{task_id}/exports", response_model=AnnotationExportResponse, status_code=status.HTTP_201_CREATED)
async def create_annotation_export(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int,
    export_in: AnnotationExportCreate
):
    """
    创建标注导出任务

    支持的导出格式：
    - **yolo**: YOLO 格式（txt 文件 + 数据集结构）
    - **coco**: COCO 格式（JSON 文件）
    - **label_studio_json**: Label Studio 原始 JSON 格式
    """
    # 检查任务是否存在
    task = await crud_annotation_task.get(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    # 设置 task_id
    export_in.task_id = task_id

    try:
        export_record = await crud_annotation_export.create(
            db=db,
            obj_in=export_in,
            created_by=current_user.id
        )

        logger.info(
            f"用户 {current_user.username} 创建了标注导出任务 {export_record.id} "
            f"(任务: {task_id}, 格式: {export_in.export_format})"
        )

        # 触发异步导出任务（Celery）
        export_format = export_in.export_format.lower()

        if export_format == 'yolo':
            export_annotations_yolo_task.delay(export_record.id)
            logger.info(f"已触发 YOLO 导出任务: export_id={export_record.id}")

        elif export_format == 'coco':
            export_annotations_coco_task.delay(export_record.id)
            logger.info(f"已触发 COCO 导出任务: export_id={export_record.id}")

        elif export_format == 'label_studio_json':
            export_annotations_label_studio_task.delay(export_record.id)
            logger.info(f"已触发 Label Studio JSON 导出任务: export_id={export_record.id}")

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的导出格式: {export_format}"
            )

        return AnnotationExportResponse(**export_record.__dict__)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建标注导出失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建标注导出失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/exports", response_model=List[AnnotationExportResponse])
async def list_annotation_exports(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """获取指定任务的导出记录列表"""
    # 检查任务是否存在
    task = await crud_annotation_task.get(db=db, task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"标注任务 {task_id} 不存在"
        )

    exports, total = await crud_annotation_export.get_multi_by_task(
        db=db,
        task_id=task_id,
        skip=skip,
        limit=limit
    )

    return [AnnotationExportResponse(**exp.__dict__) for exp in exports]


@router.get("/exports/{export_id}", response_model=AnnotationExportResponse)
async def get_annotation_export(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    export_id: int
):
    """获取单个导出记录"""
    export_record = await crud_annotation_export.get(db=db, export_id=export_id)

    if not export_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"导出记录 {export_id} 不存在"
        )

    return AnnotationExportResponse(**export_record.__dict__)


@router.get("/exports/{export_id}/download")
async def download_annotation_export(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    export_id: int
):
    """
    下载导出文件

    导出完成后，通过此端点下载生成的文件
    """
    export_record = await crud_annotation_export.get(db=db, export_id=export_id)

    if not export_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"导出记录 {export_id} 不存在"
        )

    # 检查导出状态
    if export_record.status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"导出尚未完成，当前状态: {export_record.status}"
        )

    # 检查文件是否存在
    if not export_record.file_path or not os.path.exists(export_record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="导出文件不存在"
        )

    # 确定文件名
    filename = os.path.basename(export_record.file_path)

    logger.info(f"用户 {current_user.username} 下载导出文件: {export_record.file_path}")

    # 返回文件下载响应
    return FileResponse(
        path=export_record.file_path,
        filename=filename,
        media_type='application/octet-stream'
    )
