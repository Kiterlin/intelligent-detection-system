"""
Label Studio API 服务封装
提供与 Label Studio 的集成功能
"""
import os
from typing import List, Dict, Optional, Any
import requests
from requests.exceptions import RequestException
from loguru import logger

from app.core.config import settings


class LabelStudioService:
    """Label Studio API 服务"""

    def __init__(self):
        self.url = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
        self.api_key = os.getenv('LABEL_STUDIO_API_KEY', '')
        self.timeout = 30  # 请求超时时间（秒）

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            'Content-Type': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Token {self.api_key}'
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: 请求方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点
            **kwargs: 其他请求参数

        Returns:
            响应 JSON 数据

        Raises:
            Exception: 请求失败时抛出异常
        """
        url = f"{self.url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json() if response.content else {}

        except RequestException as e:
            logger.error(f"Label Studio API 请求失败: {str(e)}")
            raise Exception(f"Label Studio API 请求失败: {str(e)}")

    def check_connection(self) -> bool:
        """检查 Label Studio 连接"""
        try:
            self._make_request('GET', '/version')
            return True
        except Exception as e:
            logger.error(f"无法连接到 Label Studio: {str(e)}")
            return False

    def create_project(
        self,
        title: str,
        description: str = "",
        label_config: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建 Label Studio 项目

        Args:
            title: 项目标题
            description: 项目描述
            label_config: 标注配置 XML

        Returns:
            项目信息字典，包含 id, title 等
        """
        if label_config is None:
            label_config = self._get_default_labeling_config()

        project_data = {
            "title": title,
            "description": description,
            "label_config": label_config,
            "is_published": True,
        }

        try:
            project = self._make_request('POST', '/api/projects', json=project_data)
            logger.info(f"创建 Label Studio 项目成功: {project.get('id')} - {title}")
            return project

        except Exception as e:
            logger.error(f"创建 Label Studio 项目失败: {str(e)}")
            raise

    def get_project(self, project_id: int) -> Dict[str, Any]:
        """获取项目信息"""
        try:
            return self._make_request('GET', f'/api/projects/{project_id}')
        except Exception as e:
            logger.error(f"获取 Label Studio 项目失败: {str(e)}")
            raise

    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        try:
            self._make_request('DELETE', f'/api/projects/{project_id}')
            logger.info(f"删除 Label Studio 项目成功: {project_id}")
            return True
        except Exception as e:
            logger.error(f"删除 Label Studio 项目失败: {str(e)}")
            return False

    def import_tasks(
        self,
        project_id: int,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        导入任务到项目

        Args:
            project_id: 项目 ID
            tasks: 任务列表，每个任务包含 data 和可选的 predictions

        Returns:
            导入结果，包含 task_count 等信息
        """
        try:
            result = self._make_request(
                'POST',
                f'/api/projects/{project_id}/import',
                json=tasks
            )
            logger.info(
                f"导入任务到 Label Studio 项目 {project_id} 成功: "
                f"{result.get('task_count', len(tasks))} 个任务"
            )
            return result

        except Exception as e:
            logger.error(f"导入任务失败: {str(e)}")
            raise

    def get_tasks(self, project_id: int) -> List[Dict[str, Any]]:
        """获取项目的所有任务"""
        try:
            return self._make_request('GET', f'/api/projects/{project_id}/tasks')
        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
            raise

    def export_tasks(
        self,
        project_id: int,
        export_type: str = 'JSON'
    ) -> List[Dict[str, Any]]:
        """
        导出项目的标注数据

        Args:
            project_id: 项目 ID
            export_type: 导出类型 (JSON, YOLO, COCO 等)

        Returns:
            标注数据列表
        """
        try:
            # Label Studio 导出 API
            params = {'exportType': export_type}
            result = self._make_request(
                'GET',
                f'/api/projects/{project_id}/export',
                params=params
            )
            logger.info(f"导出 Label Studio 项目 {project_id} 的标注数据成功")
            return result if isinstance(result, list) else [result]

        except Exception as e:
            logger.error(f"导出标注数据失败: {str(e)}")
            raise

    def update_task(
        self,
        task_id: int,
        annotations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新任务的标注数据"""
        try:
            return self._make_request(
                'PATCH',
                f'/api/tasks/{task_id}',
                json=annotations
            )
        except Exception as e:
            logger.error(f"更新任务标注失败: {str(e)}")
            raise

    def _get_default_labeling_config(self) -> str:
        """
        获取默认的标注配置模板（目标检测）

        Returns:
            Label Studio XML 配置
        """
        return '''
<View>
  <Image name="image" value="$image" zoom="true" zoomControl="true" rotateControl="true"/>
  <RectangleLabels name="label" toName="image" showInline="true">
    <Label value="fish" background="#FF0000"/>
    <Label value="turtle" background="#0000FF"/>
    <Label value="coral" background="#00FF00"/>
    <Label value="seahorse" background="#FFA500"/>
    <Label value="starfish" background="#800080"/>
    <Label value="jellyfish" background="#FFC0CB"/>
    <Label value="crab" background="#FFFF00"/>
    <Label value="octopus" background="#A52A2A"/>
    <Label value="shark" background="#808080"/>
    <Label value="dolphin" background="#00FFFF"/>
  </RectangleLabels>
</View>
'''

    def get_labeling_config_for_classes(self, class_labels: List[str]) -> str:
        """
        根据类别标签生成标注配置

        Args:
            class_labels: 类别标签列表

        Returns:
            Label Studio XML 配置
        """
        # 预定义的颜色列表
        colors = [
            "#FF0000", "#0000FF", "#00FF00", "#FFA500", "#800080",
            "#FFC0CB", "#FFFF00", "#A52A2A", "#808080", "#00FFFF",
            "#FF00FF", "#C0C0C0", "#008000", "#000080", "#800000",
        ]

        labels_xml = ""
        for i, label in enumerate(class_labels):
            color = colors[i % len(colors)]
            labels_xml += f'    <Label value="{label}" background="{color}"/>\n'

        return f'''
<View>
  <Image name="image" value="$image" zoom="true" zoomControl="true" rotateControl="true"/>
  <RectangleLabels name="label" toName="image" showInline="true">
{labels_xml}  </RectangleLabels>
</View>
'''


# 创建全局服务实例
label_studio_service = LabelStudioService()
