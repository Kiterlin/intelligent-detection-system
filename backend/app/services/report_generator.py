"""
报告生成服务
"""
import os
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.data_aggregator import ReportDataAggregator
from app.services.chart_generator import ChartGenerator


class ReportGenerator:
    """报告生成服务"""

    def __init__(self):
        # Jinja2 模板环境
        template_dir = os.path.join(os.getcwd(), "backend/app/templates/reports")
        self.template_env = Environment(loader=FileSystemLoader(template_dir))

        # 图表生成器
        self.chart_generator = ChartGenerator()

        # 输出目录
        self.output_dir_pdf = "backend/storage/reports/pdf"
        self.output_dir_html = "backend/storage/reports/html"
        os.makedirs(self.output_dir_pdf, exist_ok=True)
        os.makedirs(self.output_dir_html, exist_ok=True)

    async def generate_report(
        self,
        db: AsyncSession,
        report_id: int,
        report_type: str,
        user_id: int,
        parameters: Dict[str, Any]
    ) -> tuple[str, str]:
        """
        生成报告

        Args:
            db: 数据库会话
            report_id: 报告ID
            report_type: 报告类型（summary/detailed/comparison）
            user_id: 用户ID
            parameters: 报告参数

        Returns:
            (pdf_path, html_path)
        """
        # 1. 聚合数据
        aggregator = ReportDataAggregator(db)

        # 解析时间范围
        start_date = None
        end_date = None
        if parameters and 'time_range' in parameters:
            time_range = parameters['time_range']
            if 'start' in time_range:
                start_date = datetime.fromisoformat(time_range['start'])
            if 'end' in time_range:
                end_date = datetime.fromisoformat(time_range['end'])

        # 解析过滤条件
        filters = parameters.get('filters', {}) if parameters else {}
        dataset_id = filters.get('dataset_id')
        model_id = filters.get('model_id')
        detection_type = filters.get('detection_type')

        # 根据报告类型聚合数据
        if report_type == 'comparison':
            # 对比报告：需要多个模型ID
            model_ids = filters.get('model_ids', [])
            if not model_ids or len(model_ids) < 2:
                raise ValueError("对比报告至少需要2个模型ID")

            data = await aggregator.aggregate_comparison_data(
                user_id=user_id,
                model_ids=model_ids,
                start_date=start_date,
                end_date=end_date,
                dataset_id=dataset_id,
                detection_type=detection_type
            )
        else:
            # 概要报告和详细报告
            data = await aggregator.aggregate_detection_data(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                dataset_id=dataset_id,
                model_id=model_id,
                detection_type=detection_type
            )

        # 2. 生成图表
        charts = {}
        timestamp = int(datetime.now().timestamp())

        if report_type == 'comparison':
            # 对比报告的图表
            if data.get('models_compared'):
                # 生成模型对比柱状图
                comparison_data = {
                    m['model_name']: m['total_detections']
                    for m in data['models_compared']
                }
                charts['comparison_chart'] = self.chart_generator.generate_bar_chart(
                    data=comparison_data,
                    title='模型检测次数对比',
                    filename=f'report_{report_id}_comparison_{timestamp}'
                )
        else:
            # 概要和详细报告的图表
            # 类别分布饼图
            if data.get('class_distribution'):
                charts['pie_chart'] = self.chart_generator.generate_pie_chart(
                    data=data['class_distribution'],
                    title='检测对象类别分布',
                    filename=f'report_{report_id}_pie_{timestamp}'
                )

            # 时间趋势折线图 (仅详细报告)
            if report_type == 'detailed' and data.get('time_trend'):
                charts['line_chart'] = self.chart_generator.generate_line_chart(
                    data=data['time_trend'],
                    title='检测时间趋势',
                    filename=f'report_{report_id}_line_{timestamp}'
                )

            # 模型使用柱状图
            if data.get('model_usage'):
                model_usage_dict = {m['model_name']: m['usage_count'] for m in data['model_usage']}
                charts['bar_chart'] = self.chart_generator.generate_bar_chart(
                    data=model_usage_dict,
                    title='模型使用情况',
                    filename=f'report_{report_id}_bar_{timestamp}'
                )

        # 3. 确定报告标题
        report_titles = {
            'summary': '智能目标检测概要报告',
            'detailed': '智能目标检测详细报告',
            'comparison': '智能目标检测模型对比报告'
        }
        report_title = report_titles.get(report_type, '智能目标检测报告')

        # 4. 渲染 HTML
        template_name = f"{report_type}_report.html"
        template = self.template_env.get_template(template_name)

        html_content = template.render(
            title=report_title,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            time_range={
                'start': start_date.strftime('%Y-%m-%d') if start_date else '不限',
                'end': end_date.strftime('%Y-%m-%d') if end_date else '不限'
            } if start_date or end_date else None,
            data=data,
            charts=charts
        )

        # 5. 保存 HTML
        html_path = os.path.join(self.output_dir_html, f"report_{report_id}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 6. 生成 PDF
        pdf_path = os.path.join(self.output_dir_pdf, f"report_{report_id}.pdf")

        try:
            HTML(string=html_content, base_url=os.getcwd()).write_pdf(
                pdf_path,
                stylesheets=None
            )
        except Exception as e:
            # 如果PDF生成失败，至少返回HTML
            print(f"PDF generation failed: {e}")
            pdf_path = None

        return pdf_path, html_path

    def cleanup_old_reports(self, days: int = 30):
        """清理旧的报告文件"""
        now = datetime.now()

        for directory in [self.output_dir_pdf, self.output_dir_html]:
            if not os.path.exists(directory):
                continue

            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    file_age = now - datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_age.days > days:
                        try:
                            os.remove(filepath)
                        except Exception:
                            pass
