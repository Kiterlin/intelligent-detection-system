"""
报告 CRUD 操作
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


async def create_report(
    db: AsyncSession,
    user_id: int,
    report_data: ReportCreate
) -> Report:
    """创建报告"""
    report = Report(
        user_id=user_id,
        name=report_data.name,
        report_type=report_data.report_type,
        status="pending",
        parameters_json=report_data.parameters.dict() if report_data.parameters else None
    )

    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


async def get_report(
    db: AsyncSession,
    report_id: int
) -> Optional[Report]:
    """获取单个报告"""
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    return result.scalar_one_or_none()


async def get_user_reports(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None
) -> tuple[List[Report], int]:
    """获取用户的报告列表"""
    # 构建查询条件
    conditions = [Report.user_id == user_id]
    if status:
        conditions.append(Report.status == status)

    # 查询报告列表
    query = (
        select(Report)
        .where(and_(*conditions))
        .order_by(Report.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    reports = result.scalars().all()

    # 查询总数
    count_query = select(func.count(Report.id)).where(and_(*conditions))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return list(reports), total


async def update_report(
    db: AsyncSession,
    report_id: int,
    report_update: ReportUpdate
) -> Optional[Report]:
    """更新报告"""
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        return None

    # 更新字段
    if report_update.name is not None:
        report.name = report_update.name
    if report_update.status is not None:
        report.status = report_update.status

    await db.commit()
    await db.refresh(report)
    return report


async def update_report_status(
    db: AsyncSession,
    report_id: int,
    status: str,
    file_path_pdf: Optional[str] = None,
    file_path_html: Optional[str] = None,
    error_message: Optional[str] = None,
    completed_at: Optional[datetime] = None
) -> Optional[Report]:
    """更新报告状态"""
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        return None

    report.status = status

    if file_path_pdf:
        report.file_path_pdf = file_path_pdf
    if file_path_html:
        report.file_path_html = file_path_html
    if error_message:
        report.error_message = error_message
    if completed_at:
        report.completed_at = completed_at

    await db.commit()
    await db.refresh(report)
    return report


async def delete_report(
    db: AsyncSession,
    report_id: int
) -> bool:
    """删除报告"""
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        return False

    await db.delete(report)
    await db.commit()
    return True


async def get_pending_reports(
    db: AsyncSession,
    limit: int = 10
) -> List[Report]:
    """获取待处理的报告"""
    result = await db.execute(
        select(Report)
        .where(Report.status == "pending")
        .order_by(Report.created_at)
        .limit(limit)
    )
    return list(result.scalars().all())
