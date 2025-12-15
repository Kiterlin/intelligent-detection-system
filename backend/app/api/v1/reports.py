"""
报告生成相关 API 端点
"""
import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.report import ReportStatus
from app.crud import report as report_crud
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportListResponse,
)
from app.tasks.report_tasks import generate_report_task
from loguru import logger

router = APIRouter()


# ==================== 辅助函数 ====================

def _build_report_response(report) -> ReportResponse:
    """构建报告响应对象"""
    return ReportResponse.model_validate(report)


# ==================== 报告生成端点 ====================

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建报告生成任务

    Args:
        report_data: 报告配置数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        创建的报告对象

    Raises:
        HTTPException: 创建失败
    """
    try:
        # 1. 创建报告记录
        report = await report_crud.create_report(
            db=db,
            user_id=current_user.id,
            report_data=report_data,
        )

        logger.info(f"报告记录创建成功: report_id={report.id}, user_id={current_user.id}")

        # 2. 触发异步任务生成报告
        task = generate_report_task.delay(report.id)

        logger.info(f"报告生成任务已提交: report_id={report.id}, task_id={task.id}")

        return _build_report_response(report)

    except Exception as e:
        await db.rollback()
        logger.error(f"创建报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建报告失败: {str(e)}"
        )


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status_filter: Optional[str] = Query(None, description="按状态筛选"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户的报告列表（分页）

    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        status_filter: 状态筛选（pending/generating/completed/failed）
        current_user: 当前用户
        db: 数据库会话

    Returns:
        报告列表和总数
    """
    try:
        # 解析状态筛选
        status_enum = None
        if status_filter:
            try:
                status_enum = ReportStatus(status_filter)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"无效的状态值: {status_filter}"
                )

        # 查询报告列表
        reports, total = await report_crud.get_user_reports(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status_enum
        )

        return ReportListResponse(
            reports=[_build_report_response(r) for r in reports],
            total=total,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报告列表失败: {str(e)}"
        )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取特定报告的详情

    Args:
        report_id: 报告ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        报告详情

    Raises:
        HTTPException: 报告不存在或无权访问
    """
    try:
        report = await report_crud.get_report(db, report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在"
            )

        # 检查权限
        if report.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此报告"
            )

        return _build_report_response(report)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报告详情失败: {str(e)}"
        )


@router.get("/{report_id}/download/{file_format}")
async def download_report(
    report_id: int,
    file_format: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    下载报告文件

    Args:
        report_id: 报告ID
        file_format: 文件格式（pdf/html）
        current_user: 当前用户
        db: 数据库会话

    Returns:
        报告文件

    Raises:
        HTTPException: 报告不存在、无权访问或文件不可用
    """
    try:
        # 验证格式
        if file_format not in ['pdf', 'html']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件格式必须是 pdf 或 html"
            )

        # 获取报告
        report = await report_crud.get_report(db, report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在"
            )

        # 检查权限
        if report.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权访问此报告"
            )

        # 检查报告状态
        if report.status != ReportStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"报告尚未生成完成，当前状态: {report.status.value}"
            )

        # 获取文件路径
        file_path = report.file_path_pdf if file_format == 'pdf' else report.file_path_html

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{file_format.upper()} 文件不可用"
            )

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"报告文件不存在: {file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告文件不存在"
            )

        # 生成文件名
        filename = f"{report.name.replace(' ', '_')}_{report_id}.{file_format}"

        # 返回文件
        media_type = 'application/pdf' if file_format == 'pdf' else 'text/html'

        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载报告失败: {str(e)}"
        )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除报告及其文件

    Args:
        report_id: 报告ID
        current_user: 当前用户
        db: 数据库会话

    Raises:
        HTTPException: 报告不存在或无权删除
    """
    try:
        # 获取报告
        report = await report_crud.get_report(db, report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在"
            )

        # 检查权限
        if report.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除此报告"
            )

        # 删除文件
        for file_path in [report.file_path_pdf, report.file_path_html]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"已删除报告文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除报告文件失败: {file_path}, error={str(e)}")

        # 删除数据库记录
        await report_crud.delete_report(db, report_id)
        await db.commit()

        logger.info(f"报告已删除: report_id={report_id}, user_id={current_user.id}")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"删除报告失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除报告失败: {str(e)}"
        )
