"""
告警集成服务

将告警系统集成到检测任务中
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.crud.alert import get_active_alert_rules, create_alert_log
from app.services.alert_engine import evaluate_conditions, parse_detection_result_json
from app.services.alert_actions import execute_alert_actions


async def check_and_trigger_alerts(
    db: AsyncSession,
    detection_id: int,
    user_id: int,
    result_json: str,
    dataset_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    检查并触发告警

    在检测完成后调用此函数，评估所有active的告警规则，
    如果条件满足则执行相应的动作并记录日志

    Args:
        db: 数据库会话
        detection_id: 检测记录ID
        user_id: 用户ID
        result_json: 检测结果JSON字符串
        dataset_id: 数据集ID（可选）

    Returns:
        触发统计信息字典
    """
    triggered_count = 0
    checked_count = 0
    failed_count = 0

    try:
        # 获取用户的所有启用的告警规则
        active_rules = await get_active_alert_rules(db, user_id)

        if not active_rules:
            logger.debug(f"No active alert rules for user {user_id}")
            return {
                "checked": 0,
                "triggered": 0,
                "failed": 0,
            }

        # 解析检测结果JSON
        detection_result = parse_detection_result_json(result_json)
        if not detection_result:
            logger.warning(f"Failed to parse detection result JSON for detection {detection_id}")
            return {
                "checked": 0,
                "triggered": 0,
                "failed": 0,
            }

        # 评估每个规则
        for rule in active_rules:
            checked_count += 1

            try:
                # 评估条件
                is_triggered, conditions_met = evaluate_conditions(
                    detection_result=detection_result,
                    conditions=rule.conditions,
                    dataset_id=dataset_id,
                )

                if not is_triggered:
                    logger.debug(f"Rule {rule.id} ({rule.name}) not triggered")
                    continue

                logger.info(f"Rule {rule.id} ({rule.name}) triggered for detection {detection_id}")
                triggered_count += 1

                # 构建检测信息（用于动作执行）
                # 注意：此处需要从数据库获取完整的检测记录
                from app.crud.detection import crud_detection_history
                detection_record = await crud_detection_history.get_detection_by_id(db, detection_id)

                detection_info = {
                    "id": detection_id,
                    "input_type": detection_record.input_type.value if detection_record else "unknown",
                    "created_at": str(detection_record.created_at) if detection_record else None,
                }

                # 执行告警动作
                actions_result = await execute_alert_actions(
                    actions=rule.actions,
                    rule_name=rule.name,
                    rule_id=rule.id,
                    detection_info=detection_info,
                    conditions_met=conditions_met,
                )

                # 判断整体执行状态
                email_success = actions_result.get("email", {}).get("success") if actions_result.get("email") else None
                webhook_success = actions_result.get("webhook", {}).get("success") if actions_result.get("webhook") else None

                # 确定状态
                if email_success is False or webhook_success is False:
                    # 有失败的动作
                    if email_success is not False and webhook_success is not False:
                        status = "success"  # 至少有一个成功
                    elif email_success or webhook_success:
                        status = "partial"  # 部分成功
                    else:
                        status = "failed"  # 全部失败
                else:
                    status = "success"  # 全部成功

                # 记录告警日志
                try:
                    await create_alert_log(
                        db=db,
                        rule_id=rule.id,
                        detection_id=detection_id,
                        conditions_met=conditions_met,
                        actions_executed=actions_result,
                        status=status,
                    )
                except Exception as log_error:
                    logger.error(f"Failed to create alert log: {log_error}")
                    failed_count += 1

            except Exception as rule_error:
                logger.error(f"Error processing alert rule {rule.id}: {rule_error}")
                failed_count += 1
                continue

        logger.info(
            f"Alert check complete for detection {detection_id}: "
            f"checked={checked_count}, triggered={triggered_count}, failed={failed_count}"
        )

        return {
            "checked": checked_count,
            "triggered": triggered_count,
            "failed": failed_count,
        }

    except Exception as e:
        logger.error(f"Error in check_and_trigger_alerts: {e}")
        return {
            "checked": checked_count,
            "triggered": triggered_count,
            "failed": failed_count,
        }
