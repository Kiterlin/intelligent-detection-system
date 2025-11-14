"""
告警规则 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.alert import AlertRule, AlertLog, AlertLogStatus


# ==================== 告警规则 CRUD ====================

async def create_alert_rule(
    db: AsyncSession,
    user_id: int,
    name: str,
    conditions: Dict[str, Any],
    actions: Dict[str, Any],
    description: Optional[str] = None,
    is_active: bool = True,
) -> AlertRule:
    """
    创建新告警规则

    Args:
        db: 数据库会话
        user_id: 创建者ID
        name: 规则名称
        conditions: 触发条件（JSON格式）
        actions: 执行动作（JSON格式）
        description: 规则描述
        is_active: 是否启用

    Returns:
        AlertRule: 创建的告警规则对象

    Raises:
        ValueError: 创建失败
    """
    db_rule = AlertRule(
        user_id=user_id,
        name=name,
        description=description,
        is_active=is_active,
        conditions=conditions,
        actions=actions,
    )

    db.add(db_rule)
    try:
        await db.commit()
        await db.refresh(db_rule)
        return db_rule
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建告警规则失败：数据冲突")


async def get_alert_rule_by_id(
    db: AsyncSession, rule_id: int, user_id: Optional[int] = None
) -> Optional[AlertRule]:
    """
    根据ID获取告警规则

    Args:
        db: 数据库会话
        rule_id: 规则ID
        user_id: 用户ID（如果提供，验证所有权）

    Returns:
        Optional[AlertRule]: 告警规则对象，不存在则返回None
    """
    query = select(AlertRule).where(AlertRule.id == rule_id)

    # 如果提供了user_id，验证所有权
    if user_id is not None:
        query = query.where(AlertRule.user_id == user_id)

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_alert_rules(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> tuple[List[AlertRule], int]:
    """
    获取用户告警规则列表

    Args:
        db: 数据库会话
        user_id: 用户ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        is_active: 是否启用过滤（None表示不过滤）
        search: 搜索关键词（搜索名称和描述）

    Returns:
        (告警规则列表, 总数) 元组
    """
    query = select(AlertRule).where(AlertRule.user_id == user_id)
    count_query = select(func.count(AlertRule.id)).where(AlertRule.user_id == user_id)

    # 状态过滤
    if is_active is not None:
        query = query.where(AlertRule.is_active == is_active)
        count_query = count_query.where(AlertRule.is_active == is_active)

    # 搜索过滤
    if search:
        search_filter = or_(
            AlertRule.name.ilike(f"%{search}%"),
            AlertRule.description.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按创建时间倒序
    query = query.offset(skip).limit(limit).order_by(AlertRule.created_at.desc())

    result = await db.execute(query)
    rules = list(result.scalars().all())

    return rules, total


async def get_active_alert_rules(
    db: AsyncSession, user_id: int
) -> List[AlertRule]:
    """
    获取用户所有启用的告警规则（用于检测时评估）

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        List[AlertRule]: 启用的告警规则列表
    """
    query = (
        select(AlertRule)
        .where(and_(AlertRule.user_id == user_id, AlertRule.is_active == True))
        .order_by(AlertRule.created_at.asc())
    )

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_alert_rule(
    db: AsyncSession,
    rule_id: int,
    user_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    conditions: Optional[Dict[str, Any]] = None,
    actions: Optional[Dict[str, Any]] = None,
    is_active: Optional[bool] = None,
) -> Optional[AlertRule]:
    """
    更新告警规则

    Args:
        db: 数据库会话
        rule_id: 规则ID
        user_id: 用户ID（验证所有权）
        name: 新名称
        description: 新描述
        conditions: 新触发条件
        actions: 新执行动作
        is_active: 是否启用

    Returns:
        Optional[AlertRule]: 更新后的告警规则对象，不存在或无权限则返回None
    """
    rule = await get_alert_rule_by_id(db, rule_id, user_id)
    if not rule:
        return None

    if name is not None:
        rule.name = name
    if description is not None:
        rule.description = description
    if conditions is not None:
        rule.conditions = conditions
    if actions is not None:
        rule.actions = actions
    if is_active is not None:
        rule.is_active = is_active

    rule.updated_at = datetime.now()

    await db.commit()
    await db.refresh(rule)
    return rule


async def toggle_alert_rule(
    db: AsyncSession, rule_id: int, user_id: int, is_active: bool
) -> Optional[AlertRule]:
    """
    切换告警规则启用状态

    Args:
        db: 数据库会话
        rule_id: 规则ID
        user_id: 用户ID（验证所有权）
        is_active: 是否启用

    Returns:
        Optional[AlertRule]: 更新后的告警规则对象，不存在或无权限则返回None
    """
    return await update_alert_rule(db, rule_id, user_id, is_active=is_active)


async def delete_alert_rule(db: AsyncSession, rule_id: int, user_id: int) -> bool:
    """
    删除告警规则（级联删除日志）

    Args:
        db: 数据库会话
        rule_id: 规则ID
        user_id: 用户ID（验证所有权）

    Returns:
        bool: 是否删除成功
    """
    rule = await get_alert_rule_by_id(db, rule_id, user_id)
    if not rule:
        return False

    await db.delete(rule)
    await db.commit()
    return True


# ==================== 告警日志 CRUD ====================

async def create_alert_log(
    db: AsyncSession,
    rule_id: int,
    detection_id: int,
    conditions_met: Dict[str, Any],
    actions_executed: Dict[str, Any],
    status: str = "success",
) -> AlertLog:
    """
    创建告警日志

    Args:
        db: 数据库会话
        rule_id: 规则ID
        detection_id: 检测记录ID
        conditions_met: 满足的条件（JSON格式）
        actions_executed: 执行的动作结果（JSON格式）
        status: 执行状态

    Returns:
        AlertLog: 创建的告警日志对象

    Raises:
        ValueError: 创建失败
    """
    db_log = AlertLog(
        rule_id=rule_id,
        detection_id=detection_id,
        conditions_met=conditions_met,
        actions_executed=actions_executed,
        status=status,
    )

    db.add(db_log)
    try:
        await db.commit()
        await db.refresh(db_log)
        return db_log
    except IntegrityError:
        await db.rollback()
        raise ValueError("创建告警日志失败：数据冲突")


async def get_alert_log_by_id(
    db: AsyncSession, log_id: int
) -> Optional[AlertLog]:
    """
    根据ID获取告警日志

    Args:
        db: 数据库会话
        log_id: 日志ID

    Returns:
        Optional[AlertLog]: 告警日志对象，不存在则返回None
    """
    query = (
        select(AlertLog)
        .where(AlertLog.id == log_id)
        .options(
            selectinload(AlertLog.rule),
            selectinload(AlertLog.detection)
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_alert_logs(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    rule_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> tuple[List[AlertLog], int]:
    """
    获取告警日志列表

    Args:
        db: 数据库会话
        user_id: 用户ID（过滤该用户的规则日志）
        skip: 跳过的记录数
        limit: 返回的最大记录数
        rule_id: 规则ID过滤（可选）
        status: 状态过滤（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）

    Returns:
        (告警日志列表, 总数) 元组
    """
    # 基础查询 - 通过rule关联过滤用户
    query = (
        select(AlertLog)
        .join(AlertRule, AlertLog.rule_id == AlertRule.id)
        .where(AlertRule.user_id == user_id)
    )
    count_query = (
        select(func.count(AlertLog.id))
        .join(AlertRule, AlertLog.rule_id == AlertRule.id)
        .where(AlertRule.user_id == user_id)
    )

    # 规则过滤
    if rule_id is not None:
        query = query.where(AlertLog.rule_id == rule_id)
        count_query = count_query.where(AlertLog.rule_id == rule_id)

    # 状态过滤
    if status:
        query = query.where(AlertLog.status == status)
        count_query = count_query.where(AlertLog.status == status)

    # 日期范围过滤
    if start_date:
        query = query.where(AlertLog.triggered_at >= start_date)
        count_query = count_query.where(AlertLog.triggered_at >= start_date)
    if end_date:
        query = query.where(AlertLog.triggered_at <= end_date)
        count_query = count_query.where(AlertLog.triggered_at <= end_date)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按触发时间倒序
    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(AlertLog.triggered_at.desc())
        .options(
            selectinload(AlertLog.rule),
            selectinload(AlertLog.detection)
        )
    )

    result = await db.execute(query)
    logs = list(result.scalars().all())

    return logs, total


async def get_rule_alert_logs(
    db: AsyncSession,
    rule_id: int,
    skip: int = 0,
    limit: int = 10,
) -> tuple[List[AlertLog], int]:
    """
    获取特定规则的告警日志

    Args:
        db: 数据库会话
        rule_id: 规则ID
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        (告警日志列表, 总数) 元组
    """
    query = select(AlertLog).where(AlertLog.rule_id == rule_id)
    count_query = select(func.count(AlertLog.id)).where(AlertLog.rule_id == rule_id)

    # 获取总数
    total = await db.scalar(count_query) or 0

    # 分页查询 - 按触发时间倒序
    query = (
        query.offset(skip)
        .limit(limit)
        .order_by(AlertLog.triggered_at.desc())
        .options(selectinload(AlertLog.detection))
    )

    result = await db.execute(query)
    logs = list(result.scalars().all())

    return logs, total
