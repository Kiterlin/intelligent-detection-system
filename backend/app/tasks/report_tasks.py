"""
报告生成相关的Celery异步任务
"""
import logging
from datetime import datetime
from typing import Dict, Any

from app.celery_app import celery_app
from app.core.database import get_db
from app.crud import report as report_crud
from app.services.report_generator import ReportGenerator
from app.models.report import ReportStatus

logger = logging.getLogger(__name__)


@celery_app.task(name="generate_report", bind=True, max_retries=3)
def generate_report_task(self, report_id: int) -> Dict[str, Any]:
    """
    异步生成报告任务

    Args:
        report_id: 报告ID

    Returns:
        任务执行结果
    """
    logger.info(f"开始生成报告: report_id={report_id}")

    try:
        # 同步执行（在Celery worker中）
        import asyncio
        result = asyncio.run(_generate_report_async(report_id))
        return result

    except Exception as e:
        logger.error(f"报告生成失败: report_id={report_id}, error={str(e)}", exc_info=True)

        # 更新报告状态为失败
        try:
            asyncio.run(_update_report_error(report_id, str(e)))
        except Exception as update_error:
            logger.error(f"更新报告错误状态失败: {str(update_error)}")

        # 重试任务
        raise self.retry(exc=e, countdown=60)


async def _generate_report_async(report_id: int) -> Dict[str, Any]:
    """
    异步生成报告的内部方法

    Args:
        report_id: 报告ID

    Returns:
        生成结果
    """
    async for db in get_db():
        try:
            # 1. 获取报告记录
            report = await report_crud.get_report(db, report_id)
            if not report:
                raise ValueError(f"报告不存在: {report_id}")

            # 2. 更新状态为生成中
            await report_crud.update_report_status(
                db,
                report_id,
                ReportStatus.GENERATING
            )
            await db.commit()

            logger.info(f"报告状态更新为 GENERATING: report_id={report_id}")

            # 3. 生成报告
            generator = ReportGenerator()

            pdf_path, html_path = await generator.generate_report(
                db=db,
                report_id=report_id,
                report_type=report.report_type,
                user_id=report.user_id,
                parameters=report.parameters_json
            )

            logger.info(f"报告文件生成完成: pdf={pdf_path}, html={html_path}")

            # 4. 更新报告状态为完成
            await report_crud.update_report(
                db,
                report_id,
                {
                    'status': ReportStatus.COMPLETED,
                    'file_path_pdf': pdf_path,
                    'file_path_html': html_path,
                    'completed_at': datetime.now(),
                    'error_message': None
                }
            )
            await db.commit()

            logger.info(f"报告生成成功: report_id={report_id}")

            return {
                'report_id': report_id,
                'status': 'completed',
                'pdf_path': pdf_path,
                'html_path': html_path
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"报告生成过程出错: {str(e)}", exc_info=True)
            raise


async def _update_report_error(report_id: int, error_message: str):
    """
    更新报告错误状态

    Args:
        report_id: 报告ID
        error_message: 错误信息
    """
    async for db in get_db():
        try:
            await report_crud.update_report(
                db,
                report_id,
                {
                    'status': ReportStatus.FAILED,
                    'error_message': error_message,
                    'completed_at': datetime.now()
                }
            )
            await db.commit()
            logger.info(f"报告错误状态已更新: report_id={report_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"更新报告错误状态失败: {str(e)}", exc_info=True)
            raise
