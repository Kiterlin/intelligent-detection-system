"""
告警规则评估引擎

负责评估检测结果是否满足告警规则的触发条件
"""
import json
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger


def evaluate_conditions(
    detection_result: Dict[str, Any],
    conditions: Dict[str, Any],
    dataset_id: Optional[int] = None,
) -> Tuple[bool, Dict[str, Any]]:
    """
    评估检测结果是否满足告警条件

    Args:
        detection_result: 检测结果JSON（包含detections列表）
        conditions: 告警条件JSON
        dataset_id: 数据集ID（可选，用于dataset_id条件匹配）

    Returns:
        (是否满足条件, 满足的条件详情) 元组

    条件格式:
    {
        "target_classes": ["fish", "shark"],  # 目标类别列表
        "min_count": 2,                        # 最小数量
        "min_confidence": 0.8,                 # 最小置信度
        "dataset_id": 1                        # 可选：特定数据集
    }

    检测结果格式:
    {
        "detections": [
            {
                "class": "fish",
                "confidence": 0.95,
                "bbox": [x, y, w, h]
            },
            ...
        ]
    }
    """
    try:
        # 提取条件参数
        target_classes = conditions.get("target_classes", [])
        min_count = conditions.get("min_count", 1)
        min_confidence = conditions.get("min_confidence", 0.0)
        condition_dataset_id = conditions.get("dataset_id")

        # 数据集ID过滤（如果指定）
        if condition_dataset_id is not None and dataset_id is not None:
            if condition_dataset_id != dataset_id:
                logger.debug(
                    f"Dataset ID mismatch: expected {condition_dataset_id}, got {dataset_id}"
                )
                return False, {}

        # 提取检测结果
        detections = detection_result.get("detections", [])
        if not detections:
            logger.debug("No detections found in result")
            return False, {}

        # 过滤符合条件的检测对象
        matching_detections = []
        for detection in detections:
            detected_class = detection.get("class", "")
            confidence = detection.get("confidence", 0.0)

            # 检查类别和置信度
            if (not target_classes or detected_class in target_classes) and confidence >= min_confidence:
                matching_detections.append({
                    "class": detected_class,
                    "confidence": confidence,
                })

        # 检查数量条件
        matched_count = len(matching_detections)
        if matched_count < min_count:
            logger.debug(
                f"Count not met: {matched_count} < {min_count}"
            )
            return False, {}

        # 构建满足的条件详情
        conditions_met = {
            "target_classes": target_classes,
            "min_count": min_count,
            "min_confidence": min_confidence,
            "matched_count": matched_count,
            "matching_detections": matching_detections[:10],  # 最多记录10个
        }

        if condition_dataset_id is not None:
            conditions_met["dataset_id"] = condition_dataset_id

        logger.info(
            f"Conditions met: {matched_count} detections matched (min: {min_count})"
        )

        return True, conditions_met

    except Exception as e:
        logger.error(f"Error evaluating conditions: {e}")
        return False, {}


def parse_detection_result_json(result_json_str: str) -> Optional[Dict[str, Any]]:
    """
    解析检测结果JSON字符串

    Args:
        result_json_str: JSON字符串

    Returns:
        解析后的字典，失败返回None
    """
    try:
        if isinstance(result_json_str, dict):
            return result_json_str

        if isinstance(result_json_str, str):
            return json.loads(result_json_str)

        return None

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse detection result JSON: {e}")
        return None


def validate_alert_conditions(conditions: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证告警条件的有效性

    Args:
        conditions: 告警条件字典

    Returns:
        (是否有效, 错误信息) 元组
    """
    try:
        # 检查必要字段
        if "min_count" in conditions:
            min_count = conditions["min_count"]
            if not isinstance(min_count, int) or min_count < 1:
                return False, "min_count must be a positive integer"

        if "min_confidence" in conditions:
            min_confidence = conditions["min_confidence"]
            if not isinstance(min_confidence, (int, float)) or not (0.0 <= min_confidence <= 1.0):
                return False, "min_confidence must be a number between 0.0 and 1.0"

        if "target_classes" in conditions:
            target_classes = conditions["target_classes"]
            if not isinstance(target_classes, list):
                return False, "target_classes must be a list"

        if "dataset_id" in conditions:
            dataset_id = conditions["dataset_id"]
            if dataset_id is not None and not isinstance(dataset_id, int):
                return False, "dataset_id must be an integer or null"

        return True, None

    except Exception as e:
        return False, f"Invalid conditions format: {str(e)}"


def validate_alert_actions(actions: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    验证告警动作的有效性

    Args:
        actions: 告警动作字典

    Returns:
        (是否有效, 错误信息) 元组
    """
    try:
        # 至少要有一个动作启用
        email_enabled = actions.get("email", {}).get("enabled", False)
        webhook_enabled = actions.get("webhook", {}).get("enabled", False)

        if not email_enabled and not webhook_enabled:
            return False, "At least one action (email or webhook) must be enabled"

        # 验证邮件配置
        if email_enabled:
            recipients = actions.get("email", {}).get("recipients", [])
            if not recipients or not isinstance(recipients, list) or len(recipients) == 0:
                return False, "Email recipients list cannot be empty when email is enabled"

        # 验证Webhook配置
        if webhook_enabled:
            webhook_url = actions.get("webhook", {}).get("url", "")
            if not webhook_url or not isinstance(webhook_url, str):
                return False, "Webhook URL cannot be empty when webhook is enabled"

            # 简单的URL格式验证
            if not webhook_url.startswith(("http://", "https://")):
                return False, "Webhook URL must start with http:// or https://"

        return True, None

    except Exception as e:
        return False, f"Invalid actions format: {str(e)}"
