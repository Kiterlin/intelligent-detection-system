"""
告警动作执行器

负责执行告警规则触发后的各种通知动作（邮件、Webhook等）
"""
import asyncio
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import httpx
from loguru import logger

from app.core.config import settings


# ==================== 邮件通知 ====================

async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> Dict[str, Any]:
    """
    发送邮件通知

    Args:
        recipients: 收件人邮箱列表
        subject: 邮件主题
        body: 邮件正文（纯文本）
        html_body: HTML格式邮件正文（可选）

    Returns:
        执行结果字典
    """
    try:
        # 检查SMTP配置
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP not configured, skipping email notification")
            return {
                "success": False,
                "error": "SMTP not configured",
                "recipients": recipients,
            }

        # 创建邮件消息
        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_FROM
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject

        # 添加纯文本部分
        text_part = MIMEText(body, "plain", "utf-8")
        message.attach(text_part)

        # 添加HTML部分（如果提供）
        if html_body:
            html_part = MIMEText(html_body, "html", "utf-8")
            message.attach(html_part)

        # 发送邮件
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_TLS,
            timeout=10,
        )

        logger.info(f"Email sent successfully to {len(recipients)} recipients")

        return {
            "success": True,
            "recipients": recipients,
            "subject": subject,
        }

    except aiosmtplib.SMTPException as e:
        logger.error(f"SMTP error sending email: {e}")
        return {
            "success": False,
            "error": f"SMTP error: {str(e)}",
            "recipients": recipients,
        }

    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return {
            "success": False,
            "error": str(e),
            "recipients": recipients,
        }


async def send_alert_email(
    recipients: List[str],
    rule_name: str,
    detection_info: Dict[str, Any],
    conditions_met: Dict[str, Any],
) -> Dict[str, Any]:
    """
    发送告警邮件

    Args:
        recipients: 收件人邮箱列表
        rule_name: 规则名称
        detection_info: 检测信息
        conditions_met: 满足的条件

    Returns:
        执行结果字典
    """
    # 构建邮件主题
    subject = f"🚨 告警触发: {rule_name}"

    # 构建邮件正文
    matched_count = conditions_met.get("matched_count", 0)
    min_count = conditions_met.get("min_count", 1)
    target_classes = conditions_met.get("target_classes", [])
    matching_detections = conditions_met.get("matching_detections", [])

    body = f"""
告警规则触发通知

规则名称: {rule_name}

检测结果:
- 检测到目标数量: {matched_count} 个
- 最小触发数量: {min_count} 个
- 目标类别: {', '.join(target_classes) if target_classes else '所有类别'}

检测详情:
"""

    for idx, det in enumerate(matching_detections, 1):
        body += f"\n{idx}. 类别: {det.get('class')} | 置信度: {det.get('confidence', 0):.2%}"

    body += f"""

检测时间: {detection_info.get('created_at', 'N/A')}
检测类型: {detection_info.get('input_type', 'N/A')}

---
此邮件由水下目标智能检测平台自动发送，请勿直接回复。
"""

    # 构建HTML邮件正文
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f44336; color: white; padding: 15px; border-radius: 5px; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 10px; border-radius: 5px; }}
        .detection {{ background-color: white; padding: 10px; margin: 10px 0; border-left: 3px solid #2196F3; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🚨 告警触发: {rule_name}</h2>
        </div>
        <div class="content">
            <h3>检测结果</h3>
            <p><strong>检测到目标数量:</strong> {matched_count} 个</p>
            <p><strong>最小触发数量:</strong> {min_count} 个</p>
            <p><strong>目标类别:</strong> {', '.join(target_classes) if target_classes else '所有类别'}</p>

            <h3>检测详情</h3>
"""

    for idx, det in enumerate(matching_detections, 1):
        html_body += f"""
            <div class="detection">
                <strong>{idx}.</strong>
                类别: {det.get('class')} |
                置信度: {det.get('confidence', 0):.2%}
            </div>
"""

    html_body += f"""
            <h3>其他信息</h3>
            <p><strong>检测时间:</strong> {detection_info.get('created_at', 'N/A')}</p>
            <p><strong>检测类型:</strong> {detection_info.get('input_type', 'N/A')}</p>
        </div>
        <div class="footer">
            <p>此邮件由水下目标智能检测平台自动发送，请勿直接回复。</p>
        </div>
    </div>
</body>
</html>
"""

    return await send_email(recipients, subject, body, html_body)


# ==================== Webhook通知 ====================

async def send_webhook(
    url: str,
    payload: Dict[str, Any],
    method: str = "POST",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    发送Webhook通知

    Args:
        url: Webhook URL
        payload: 请求负载（JSON）
        method: HTTP方法（默认POST）
        headers: 额外的HTTP头
        timeout: 超时时间（秒）

    Returns:
        执行结果字典
    """
    try:
        # 设置默认头
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Water-Detection-Alert-System/1.0",
        }

        if headers:
            default_headers.update(headers)

        # 发送HTTP请求
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "POST":
                response = await client.post(url, json=payload, headers=default_headers)
            elif method.upper() == "GET":
                response = await client.get(url, params=payload, headers=default_headers)
            elif method.upper() == "PUT":
                response = await client.put(url, json=payload, headers=default_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # 检查响应状态
            response.raise_for_status()

            logger.info(
                f"Webhook sent successfully to {url}, status: {response.status_code}"
            )

            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "response": response.text[:200],  # 限制响应长度
            }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error sending webhook: {e}")
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}",
            "url": url,
        }

    except httpx.TimeoutException:
        logger.error(f"Timeout sending webhook to {url}")
        return {
            "success": False,
            "error": "Request timeout",
            "url": url,
        }

    except Exception as e:
        logger.error(f"Unexpected error sending webhook: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
        }


async def send_alert_webhook(
    url: str,
    rule_name: str,
    rule_id: int,
    detection_info: Dict[str, Any],
    conditions_met: Dict[str, Any],
    method: str = "POST",
) -> Dict[str, Any]:
    """
    发送告警Webhook

    Args:
        url: Webhook URL
        rule_name: 规则名称
        rule_id: 规则ID
        detection_info: 检测信息
        conditions_met: 满足的条件
        method: HTTP方法

    Returns:
        执行结果字典
    """
    # 构建Webhook负载
    payload = {
        "event": "alert_triggered",
        "rule": {
            "id": rule_id,
            "name": rule_name,
        },
        "detection": {
            "id": detection_info.get("id"),
            "input_type": detection_info.get("input_type"),
            "created_at": detection_info.get("created_at"),
        },
        "conditions_met": conditions_met,
        "timestamp": detection_info.get("created_at"),
    }

    return await send_webhook(url, payload, method)


# ==================== 动作执行器 ====================

async def execute_alert_actions(
    actions: Dict[str, Any],
    rule_name: str,
    rule_id: int,
    detection_info: Dict[str, Any],
    conditions_met: Dict[str, Any],
) -> Dict[str, Any]:
    """
    执行所有告警动作

    Args:
        actions: 动作配置字典
        rule_name: 规则名称
        rule_id: 规则ID
        detection_info: 检测信息
        conditions_met: 满足的条件

    Returns:
        执行结果字典
    """
    results = {
        "email": None,
        "webhook": None,
    }

    tasks = []

    # 邮件通知
    email_config = actions.get("email", {})
    if email_config.get("enabled", False):
        recipients = email_config.get("recipients", [])
        if recipients:
            tasks.append(
                ("email", send_alert_email(
                    recipients, rule_name, detection_info, conditions_met
                ))
            )

    # Webhook通知
    webhook_config = actions.get("webhook", {})
    if webhook_config.get("enabled", False):
        webhook_url = webhook_config.get("url")
        webhook_method = webhook_config.get("method", "POST")
        if webhook_url:
            tasks.append(
                ("webhook", send_alert_webhook(
                    webhook_url, rule_name, rule_id, detection_info,
                    conditions_met, webhook_method
                ))
            )

    # 并发执行所有动作
    if tasks:
        task_results = await asyncio.gather(
            *[task for _, task in tasks], return_exceptions=True
        )

        for (action_type, _), result in zip(tasks, task_results):
            if isinstance(result, Exception):
                logger.error(f"Error executing {action_type} action: {result}")
                results[action_type] = {
                    "success": False,
                    "error": str(result),
                }
            else:
                results[action_type] = result

    logger.info(f"Executed {len(tasks)} alert actions for rule {rule_id}")

    return results
