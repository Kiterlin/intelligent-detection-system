"""
标注导出相关的 Celery 异步任务
"""
import logging
import os
import zipfile
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from app.celery_app import celery_app
from app.core.database import get_db
from app.crud.annotation import crud_annotation_export, crud_annotation_task, crud_annotation
from app.services.label_studio_service import label_studio_service
from app.services.annotation_converter import annotation_converter
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="export_annotations_yolo", bind=True, max_retries=3)
def export_annotations_yolo_task(self, export_id: int) -> Dict[str, Any]:
    """
    异步导出标注数据为 YOLO 格式

    Args:
        export_id: 导出记录ID

    Returns:
        任务执行结果
    """
    logger.info(f"开始导出 YOLO 格式标注: export_id={export_id}")

    try:
        import asyncio
        result = asyncio.run(_export_yolo_async(export_id))
        return result

    except Exception as e:
        logger.error(f"YOLO 导出失败: export_id={export_id}, error={str(e)}", exc_info=True)

        # 更新导出状态为失败
        try:
            asyncio.run(_update_export_error(export_id, str(e)))
        except Exception as update_error:
            logger.error(f"更新导出错误状态失败: {str(update_error)}")

        # 重试任务
        raise self.retry(exc=e, countdown=60)


@celery_app.task(name="export_annotations_coco", bind=True, max_retries=3)
def export_annotations_coco_task(self, export_id: int) -> Dict[str, Any]:
    """
    异步导出标注数据为 COCO 格式

    Args:
        export_id: 导出记录ID

    Returns:
        任务执行结果
    """
    logger.info(f"开始导出 COCO 格式标注: export_id={export_id}")

    try:
        import asyncio
        result = asyncio.run(_export_coco_async(export_id))
        return result

    except Exception as e:
        logger.error(f"COCO 导出失败: export_id={export_id}, error={str(e)}", exc_info=True)

        # 更新导出状态为失败
        try:
            asyncio.run(_update_export_error(export_id, str(e)))
        except Exception as update_error:
            logger.error(f"更新导出错误状态失败: {str(update_error)}")

        # 重试任务
        raise self.retry(exc=e, countdown=60)


@celery_app.task(name="export_annotations_label_studio", bind=True, max_retries=3)
def export_annotations_label_studio_task(self, export_id: int) -> Dict[str, Any]:
    """
    异步从 Label Studio 导出标注数据

    Args:
        export_id: 导出记录ID

    Returns:
        任务执行结果
    """
    logger.info(f"开始从 Label Studio 导出标注: export_id={export_id}")

    try:
        import asyncio
        result = asyncio.run(_export_label_studio_async(export_id))
        return result

    except Exception as e:
        logger.error(f"Label Studio 导出失败: export_id={export_id}, error={str(e)}", exc_info=True)

        # 更新导出状态为失败
        try:
            asyncio.run(_update_export_error(export_id, str(e)))
        except Exception as update_error:
            logger.error(f"更新导出错误状态失败: {str(update_error)}")

        # 重试任务
        raise self.retry(exc=e, countdown=60)


async def _export_yolo_async(export_id: int) -> Dict[str, Any]:
    """
    异步导出 YOLO 格式的内部方法

    Args:
        export_id: 导出记录ID

    Returns:
        导出结果
    """
    async for db in get_db():
        try:
            # 1. 获取导出记录
            export_record = await crud_annotation_export.get(db, export_id)
            if not export_record:
                raise ValueError(f"导出记录不存在: {export_id}")

            # 2. 更新状态为处理中
            await crud_annotation_export.update_status(
                db=db,
                db_obj=export_record,
                status='processing'
            )

            logger.info(f"导出状态更新为 processing: export_id={export_id}")

            # 3. 获取标注任务
            task = await crud_annotation_task.get(db, export_record.task_id)
            if not task:
                raise ValueError(f"标注任务不存在: {export_record.task_id}")

            # 4. 从 Label Studio 导出标注数据
            if not task.label_studio_project_id:
                raise ValueError(f"任务 {task.id} 没有关联的 Label Studio 项目")

            ls_annotations = label_studio_service.export_tasks(
                project_id=task.label_studio_project_id,
                export_type='JSON'
            )

            logger.info(f"从 Label Studio 导出了 {len(ls_annotations)} 条标注")

            # 5. 准备类别映射
            class_mapping = {}
            if task.class_labels:
                for idx, label in enumerate(task.class_labels):
                    class_mapping[label] = idx

            # 6. 创建输出目录
            output_dir = Path(settings.UPLOAD_DIR) / 'exports' / 'yolo' / f"task_{task.id}_{export_id}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # 7. 转换为 YOLO 格式
            image_files, label_files = annotation_converter.label_studio_to_yolo(
                annotations=ls_annotations,
                class_mapping=class_mapping,
                output_dir=str(output_dir)
            )

            # 8. 创建完整的 YOLO 数据集
            dataset_info = annotation_converter.create_yolo_dataset(
                image_files=image_files,
                label_files=label_files,
                output_dir=str(output_dir / 'dataset'),
                class_names=task.class_labels or [],
                train_split=export_record.export_config.get('train_split', 0.8) if export_record.export_config else 0.8
            )

            logger.info(f"YOLO 数据集创建完成: {dataset_info['dataset_dir']}")

            # 9. 打包为 ZIP 文件
            zip_path = output_dir / f"yolo_export_{export_id}.zip"
            _create_zip_archive(dataset_info['dataset_dir'], zip_path)

            file_size = os.path.getsize(zip_path)

            # 10. 更新导出状态为完成
            await crud_annotation_export.update_status(
                db=db,
                db_obj=export_record,
                status='completed',
                file_path=str(zip_path),
                file_size_bytes=file_size,
                exported_count=len(label_files)
            )

            logger.info(f"YOLO 导出成功: export_id={export_id}, file={zip_path}")

            return {
                'export_id': export_id,
                'status': 'completed',
                'file_path': str(zip_path),
                'file_size': file_size,
                'exported_count': len(label_files),
                'dataset_info': dataset_info
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"YOLO 导出过程出错: {str(e)}", exc_info=True)
            raise


async def _export_coco_async(export_id: int) -> Dict[str, Any]:
    """
    异步导出 COCO 格式的内部方法

    Args:
        export_id: 导出记录ID

    Returns:
        导出结果
    """
    async for db in get_db():
        try:
            # 1. 获取导出记录
            export_record = await crud_annotation_export.get(db, export_id)
            if not export_record:
                raise ValueError(f"导出记录不存在: {export_id}")

            # 2. 更新状态为处理中
            await crud_annotation_export.update_status(
                db=db,
                db_obj=export_record,
                status='processing'
            )

            logger.info(f"导出状态更新为 processing: export_id={export_id}")

            # 3. 获取标注任务
            task = await crud_annotation_task.get(db, export_record.task_id)
            if not task:
                raise ValueError(f"标注任务不存在: {export_record.task_id}")

            # 4. 从 Label Studio 导出标注数据
            if not task.label_studio_project_id:
                raise ValueError(f"任务 {task.id} 没有关联的 Label Studio 项目")

            ls_annotations = label_studio_service.export_tasks(
                project_id=task.label_studio_project_id,
                export_type='JSON'
            )

            logger.info(f"从 Label Studio 导出了 {len(ls_annotations)} 条标注")

            # 5. 准备类别映射
            category_mapping = {}
            if task.class_labels:
                for idx, label in enumerate(task.class_labels, start=1):
                    category_mapping[label] = idx

            # 6. 创建输出目录
            output_dir = Path(settings.UPLOAD_DIR) / 'exports' / 'coco' / f"task_{task.id}_{export_id}"
            output_dir.mkdir(parents=True, exist_ok=True)

            # 7. 转换为 COCO 格式
            output_file = output_dir / 'annotations.json'
            annotation_converter.label_studio_to_coco(
                annotations=ls_annotations,
                category_mapping=category_mapping,
                output_file=str(output_file)
            )

            logger.info(f"COCO 格式文件生成完成: {output_file}")

            # 8. 打包为 ZIP 文件（包含 JSON 文件）
            zip_path = output_dir / f"coco_export_{export_id}.zip"
            _create_zip_archive(str(output_dir), zip_path, include_only=['*.json'])

            file_size = os.path.getsize(zip_path)

            # 9. 更新导出状态为完成
            await crud_annotation_export.update_status(
                db=db,
                db_obj=export_record,
                status='completed',
                file_path=str(zip_path),
                file_size_bytes=file_size,
                exported_count=len(ls_annotations)
            )

            logger.info(f"COCO 导出成功: export_id={export_id}, file={zip_path}")

            return {
                'export_id': export_id,
                'status': 'completed',
                'file_path': str(zip_path),
                'file_size': file_size,
                'exported_count': len(ls_annotations)
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"COCO 导出过程出错: {str(e)}", exc_info=True)
            raise


async def _export_label_studio_async(export_id: int) -> Dict[str, Any]:
    """
    异步从 Label Studio 导出原始 JSON 格式

    Args:
        export_id: 导出记录ID

    Returns:
        导出结果
    """
    async for db in get_db():
        try:
            # 1. 获取导出记录
            export_record = await crud_annotation_export.get(db, export_id)
            if not export_record:
                raise ValueError(f"导出记录不存在: {export_id}")

            # 2. 更新状态为处理中
            await crud_annotation_export.update_status(
                db=db,
                db_obj=export_record,
                status='processing'
            )

            # 3. 获取标注任务
            task = await crud_annotation_task.get(db, export_record.task_id)
            if not task:
                raise ValueError(f"标注任务不存在: {export_record.task_id}")

            # 4. 从 Label Studio 导出
            if not task.label_studio_project_id:
                raise ValueError(f"任务 {task.id} 没有关联的 Label Studio 项目")

            ls_annotations = label_studio_service.export_tasks(
                project_id=task.label_studio_project_id,
                export_type='JSON'
            )

            # 5. 保存为 JSON 文件
            import json
            output_dir = Path(settings.UPLOAD_DIR) / 'exports' / 'label_studio' / f"task_{task.id}_{export_id}"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / f'label_studio_export_{export_id}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(ls_annotations, f, indent=2, ensure_ascii=False)

            file_size = os.path.getsize(output_file)

            # 6. 更新导出状态为完成
            await crud_annotation_export.update_status(
                db=db,
                db_obj=export_record,
                status='completed',
                file_path=str(output_file),
                file_size_bytes=file_size,
                exported_count=len(ls_annotations)
            )

            logger.info(f"Label Studio JSON 导出成功: export_id={export_id}")

            return {
                'export_id': export_id,
                'status': 'completed',
                'file_path': str(output_file),
                'file_size': file_size,
                'exported_count': len(ls_annotations)
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Label Studio 导出过程出错: {str(e)}", exc_info=True)
            raise


async def _update_export_error(export_id: int, error_message: str):
    """
    更新导出错误状态

    Args:
        export_id: 导出记录ID
        error_message: 错误信息
    """
    async for db in get_db():
        try:
            export_record = await crud_annotation_export.get(db, export_id)
            if export_record:
                await crud_annotation_export.update_status(
                    db=db,
                    db_obj=export_record,
                    status='failed',
                    error_message=error_message
                )
                logger.info(f"导出错误状态已更新: export_id={export_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"更新导出错误状态失败: {str(e)}", exc_info=True)
            raise


def _create_zip_archive(source_dir: str, zip_path: Path, include_only: List[str] = None):
    """
    创建 ZIP 压缩包

    Args:
        source_dir: 源目录
        zip_path: ZIP 文件路径
        include_only: 只包含匹配的文件模式（例如 ['*.json', '*.txt']）
    """
    import fnmatch

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        source_path = Path(source_dir)
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                # 如果指定了包含模式，检查文件是否匹配
                if include_only:
                    if not any(fnmatch.fnmatch(file_path.name, pattern) for pattern in include_only):
                        continue

                # 计算相对路径
                arcname = file_path.relative_to(source_path)
                zipf.write(file_path, arcname)

    logger.info(f"ZIP 压缩包创建完成: {zip_path}")
