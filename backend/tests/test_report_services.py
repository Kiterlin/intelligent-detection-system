"""
报告生成相关服务的单元测试
"""
import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.report_generator import ReportGenerator
from app.services.data_aggregator import ReportDataAggregator
from app.services.chart_generator import ChartGenerator


class TestChartGenerator:
    """测试ChartGenerator类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.generator = ChartGenerator()

    def test_generate_pie_chart_success(self):
        """测试饼图生成 - 成功"""
        data = {"鱼": 10, "珊瑚": 15, "海龟": 5}
        result = self.generator.generate_pie_chart(
            data=data,
            title="测试饼图",
            filename="test_pie"
        )

        # 验证返回路径不为空
        assert result is not None
        assert "test_pie" in result
        assert result.endswith(".png")

        # 清理生成的文件
        if os.path.exists(result):
            os.remove(result)

    def test_generate_pie_chart_empty_data(self):
        """测试饼图生成 - 空数据"""
        data = {}
        result = self.generator.generate_pie_chart(
            data=data,
            title="空数据饼图",
            filename="test_empty_pie"
        )

        # 应该生成一个空图表
        assert result is not None

        # 清理生成的文件
        if os.path.exists(result):
            os.remove(result)

    def test_generate_line_chart_success(self):
        """测试折线图生成 - 成功"""
        data = [
            {"date": "2024-01-01", "count": 10},
            {"date": "2024-01-02", "count": 15},
            {"date": "2024-01-03", "count": 12}
        ]
        result = self.generator.generate_line_chart(
            data=data,
            title="测试折线图",
            filename="test_line"
        )

        assert result is not None
        assert "test_line" in result

        # 清理生成的文件
        if os.path.exists(result):
            os.remove(result)

    def test_generate_bar_chart_success(self):
        """测试柱状图生成 - 成功"""
        data = {"模型A": 50, "模型B": 30, "模型C": 20}
        result = self.generator.generate_bar_chart(
            data=data,
            title="测试柱状图",
            filename="test_bar"
        )

        assert result is not None
        assert "test_bar" in result

        # 清理生成的文件
        if os.path.exists(result):
            os.remove(result)


class TestReportGenerator:
    """测试ReportGenerator类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.generator = ReportGenerator()

    def test_init_creates_directories(self):
        """测试初始化时创建必要的目录"""
        assert os.path.exists(self.generator.output_dir_pdf)
        assert os.path.exists(self.generator.output_dir_html)

    def test_template_environment_configured(self):
        """测试模板环境正确配置"""
        assert self.generator.template_env is not None

        # 验证可以加载模板
        template_names = [
            "detailed_report.html",
            "summary_report.html",
            "comparison_report.html"
        ]

        for template_name in template_names:
            try:
                template = self.generator.template_env.get_template(template_name)
                assert template is not None
            except Exception as e:
                pytest.fail(f"无法加载模板 {template_name}: {str(e)}")

    @pytest.mark.asyncio
    async def test_generate_report_invalid_type(self):
        """测试生成报告 - 无效的报告类型"""
        mock_db = AsyncMock()

        with pytest.raises(Exception):
            await self.generator.generate_report(
                db=mock_db,
                report_id=1,
                report_type="invalid_type",  # 无效类型
                user_id=1,
                parameters={}
            )

    @pytest.mark.asyncio
    async def test_generate_report_comparison_missing_models(self):
        """测试生成对比报告 - 缺少模型ID"""
        mock_db = AsyncMock()

        with pytest.raises(ValueError, match="对比报告至少需要2个模型ID"):
            await self.generator.generate_report(
                db=mock_db,
                report_id=1,
                report_type="comparison",
                user_id=1,
                parameters={
                    "filters": {
                        "model_ids": [1]  # 只有1个模型，应该失败
                    }
                }
            )


class TestReportDataAggregator:
    """测试ReportDataAggregator类"""

    @pytest.mark.asyncio
    async def test_aggregator_initialization(self):
        """测试数据聚合器初始化"""
        mock_db = AsyncMock()
        aggregator = ReportDataAggregator(mock_db)
        assert aggregator.db == mock_db

    @pytest.mark.asyncio
    async def test_aggregate_detection_data_structure(self):
        """测试聚合数据返回结构"""
        mock_db = AsyncMock()

        # Mock数据库查询结果
        mock_db.execute = AsyncMock(return_value=MagicMock(
            scalar=MagicMock(return_value=0),
            scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        ))

        aggregator = ReportDataAggregator(mock_db)

        result = await aggregator.aggregate_detection_data(
            user_id=1,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )

        # 验证返回结构
        assert "total_stats" in result
        assert "class_distribution" in result
        assert "time_trend" in result
        assert "model_usage" in result
        assert "recent_detections" in result
        assert "parameters" in result

        # 验证total_stats结构
        total_stats = result["total_stats"]
        assert "total_detections" in total_stats
        assert "total_objects" in total_stats
        assert "avg_processing_time" in total_stats
        assert "image_count" in total_stats
        assert "video_count" in total_stats

    @pytest.mark.asyncio
    async def test_aggregate_comparison_data_structure(self):
        """测试对比数据聚合返回结构"""
        mock_db = AsyncMock()

        # Mock数据库查询结果
        mock_db.execute = AsyncMock(return_value=MagicMock(
            scalar=MagicMock(return_value="Model A"),
            scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))
        ))

        aggregator = ReportDataAggregator(mock_db)

        result = await aggregator.aggregate_comparison_data(
            user_id=1,
            model_ids=[1, 2],
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )

        # 验证返回结构
        assert "models_compared" in result
        assert "class_comparison" in result
        assert "parameters" in result

        # 验证参数正确传递
        params = result["parameters"]
        assert params["user_id"] == 1
        assert params["model_ids"] == [1, 2]


# 测试配置
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """设置测试环境"""
    # 确保测试目录存在
    os.makedirs("backend/storage/reports/charts", exist_ok=True)
    os.makedirs("backend/storage/reports/pdf", exist_ok=True)
    os.makedirs("backend/storage/reports/html", exist_ok=True)

    yield

    # 测试结束后清理（可选）
    pass
