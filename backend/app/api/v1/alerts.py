"""
告警规则相关 API 端点
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.crud.alert import (
    create_alert_rule,
    get_alert_rule_by_id,
    get_user_alert_rules,
    update_alert_rule,
    delete_alert_rule,
    toggle_alert_rule,
    get_alert_logs,
    get_rule_alert_logs,
)
from app.schemas.alert import (
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertRuleToggle,
    AlertRuleListResponse,
    AlertLogResponse,
    AlertLogListResponse,
)
from loguru import logger

router = APIRouter()


# ==================== 辅助函数 ====================

def _build_alert_rule_response(rule) -> AlertRuleResponse:
    """构建告警规则响应对象"""
    # 计算触发次数
    trigger_count = len(rule.logs) if hasattr(rule, "logs") else 0

    return AlertRuleResponse(
        id=rule.id,
        user_id=rule.user_id,
        name=rule.name,
        description=rule.description,
        is_active=rule.is_active,
        conditions=rule.conditions,
        actions=rule.actions,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        trigger_count=trigger_count,
    )


def _build_alert_log_response(log) -> AlertLogResponse:
    """构建告警日志响应对象"""
    rule_name = log.rule.name if hasattr(log, "rule") and log.rule else None
    detection_type = (
        log.detection.input_type.value
        if hasattr(log, "detection") and log.detection
        else None
    )

    return AlertLogResponse(
        id=log.id,
        rule_id=log.rule_id,
        detection_id=log.detection_id,
        triggered_at=log.triggered_at,
        conditions_met=log.conditions_met,
        actions_executed=log.actions_executed,
        status=log.status,
        rule_name=rule_name,
        detection_type=detection_type,
    )


# ==================== 告警规则端点 ====================

@router.post("/", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: AlertRuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    创建新的告警规则

    Args:
        rule_data: 告警规则数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        创建的告警规则对象

    Raises:
        HTTPException: 创建失败
    """
    try:
        rule = await create_alert_rule(
            db=db,
            user_id=current_user.id,
            name=rule_data.name,
            description=rule_data.description,
            is_active=rule_data.is_active,
            conditions=rule_data.conditions,
            actions=rule_data.actions,
        )

        logger.info(
            f"User {current_user.id} created alert rule {rule.id}: {rule.name}"
        )

        return _build_alert_rule_response(rule)

    except ValueError as e:
        logger.error(f"Failed to create alert rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get("/", response_model=AlertRuleListResponse)
async def list_rules(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    is_active: Optional[bool] = Query(None, description="是否启用过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取用户的告警规则列表

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        is_active: 是否启用过滤
        search: 搜索关键词
        current_user: 当前用户
        db: 数据库会话

    Returns:
        告警规则列表和总数
    """
    rules, total = await get_user_alert_rules(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search,
    )

    items = [_build_alert_rule_response(rule) for rule in rules]

    return AlertRuleListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{rule_id}", response_model=AlertRuleResponse)
async def get_rule(
    rule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取告警规则详情

    Args:
        rule_id: 规则ID
        current_user: 当前用户
        db: 数据库会话

    Returns:
        告警规则对象

    Raises:
        HTTPException: 规则不存在或无权限
    """
    rule = await get_alert_rule_by_id(db, rule_id, current_user.id)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"告警规则 ID {rule_id} 不存在或无权限访问",
        )

    return _build_alert_rule_response(rule)


@router.put("/{rule_id}", response_model=AlertRuleResponse)
async def update_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    更新告警规则

    Args:
        rule_id: 规则ID
        rule_data: 更新数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的告警规则对象

    Raises:
        HTTPException: 规则不存在或无权限
    """
    rule = await update_alert_rule(
        db=db,
        rule_id=rule_id,
        user_id=current_user.id,
        name=rule_data.name,
        description=rule_data.description,
        conditions=rule_data.conditions,
        actions=rule_data.actions,
        is_active=rule_data.is_active,
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"告警规则 ID {rule_id} 不存在或无权限访问",
        )

    logger.info(
        f"User {current_user.id} updated alert rule {rule_id}: {rule.name}"
    )

    return _build_alert_rule_response(rule)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    删除告警规则

    Args:
        rule_id: 规则ID
        current_user: 当前用户
        db: 数据库会话

    Raises:
        HTTPException: 规则不存在或无权限
    """
    success = await delete_alert_rule(db, rule_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"告警规则 ID {rule_id} 不存在或无权限访问",
        )

    logger.info(f"User {current_user.id} deleted alert rule {rule_id}")


@router.patch("/{rule_id}/toggle", response_model=AlertRuleResponse)
async def toggle_rule(
    rule_id: int,
    toggle_data: AlertRuleToggle,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    切换告警规则启用状态

    Args:
        rule_id: 规则ID
        toggle_data: 切换数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        更新后的告警规则对象

    Raises:
        HTTPException: 规则不存在或无权限
    """
    rule = await toggle_alert_rule(
        db=db, rule_id=rule_id, user_id=current_user.id, is_active=toggle_data.is_active
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"告警规则 ID {rule_id} 不存在或无权限访问",
        )

    status_text = "启用" if toggle_data.is_active else "禁用"
    logger.info(
        f"User {current_user.id} {status_text} alert rule {rule_id}"
    )

    return _build_alert_rule_response(rule)


# ==================== 告警日志端点 ====================

@router.get("/logs", response_model=AlertLogListResponse)
async def list_logs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的最大记录数"),
    rule_id: Optional[int] = Query(None, description="规则ID过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取告警日志列表

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        rule_id: 规则ID过滤
        status: 状态过滤
        current_user: 当前用户
        db: 数据库会话

    Returns:
        告警日志列表和总数
    """
    logs, total = await get_alert_logs(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        rule_id=rule_id,
        status=status,
    )

    items = [_build_alert_log_response(log) for log in logs]

    return AlertLogListResponse(items=items, total=total, skip=skip, limit=limit)
