"""
图表生成服务
"""
import os
from typing import Dict, List, Any
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime


class ChartGenerator:
    """图表生成服务"""

    def __init__(self, output_dir: str = "backend/storage/reports/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 配置中文字体支持
        self._configure_chinese_font()

    def _configure_chinese_font(self):
        """配置中文字体"""
        try:
            # 尝试使用常见的中文字体
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'STHeiti', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        except Exception:
            pass

    def generate_pie_chart(
        self,
        data: Dict[str, int],
        title: str,
        filename: str
    ) -> str:
        """
        生成饼图

        Args:
            data: 数据字典 {label: value}
            title: 图表标题
            filename: 文件名（不含扩展名）

        Returns:
            图表文件路径
        """
        if not data:
            return self._generate_empty_chart(title, filename)

        fig, ax = plt.subplots(figsize=(10, 8))

        labels = list(data.keys())
        values = list(data.values())

        # 生成颜色
        colors = plt.cm.Set3(range(len(labels)))

        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors
        )

        # 设置标题
        ax.set_title(title, fontsize=16, pad=20)

        # 美化文字
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')

        # 保存图表
        filepath = os.path.join(self.output_dir, f"{filename}.png")
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        return filepath

    def generate_line_chart(
        self,
        data: List[Dict[str, Any]],
        title: str,
        filename: str,
        x_key: str = 'date',
        y_key: str = 'count'
    ) -> str:
        """
        生成折线图

        Args:
            data: 数据列表 [{date: '2025-01-01', count: 10}, ...]
            title: 图表标题
            filename: 文件名
            x_key: X轴数据键
            y_key: Y轴数据键

        Returns:
            图表文件路径
        """
        if not data:
            return self._generate_empty_chart(title, filename)

        fig, ax = plt.subplots(figsize=(12, 6))

        # 提取数据
        x_values = [item[x_key] for item in data]
        y_values = [item[y_key] for item in data]

        # 绘制折线图
        ax.plot(x_values, y_values, marker='o', linewidth=2, markersize=6, color='#1f77b4')

        # 填充区域
        ax.fill_between(range(len(x_values)), y_values, alpha=0.3, color='#1f77b4')

        # 设置标题和标签
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('检测次数', fontsize=12)

        # 旋转X轴标签
        plt.xticks(rotation=45, ha='right')

        # 添加网格
        ax.grid(True, alpha=0.3, linestyle='--')

        # 保存图表
        filepath = os.path.join(self.output_dir, f"{filename}.png")
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        return filepath

    def generate_bar_chart(
        self,
        data: Dict[str, int],
        title: str,
        filename: str
    ) -> str:
        """
        生成柱状图

        Args:
            data: 数据字典 {label: value}
            title: 图表标题
            filename: 文件名

        Returns:
            图表文件路径
        """
        if not data:
            return self._generate_empty_chart(title, filename)

        fig, ax = plt.subplots(figsize=(12, 6))

        labels = list(data.keys())
        values = list(data.values())

        # 生成颜色
        colors = plt.cm.viridis(range(len(labels)))

        # 绘制柱状图
        bars = ax.bar(labels, values, color=colors)

        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{int(height)}',
                ha='center',
                va='bottom',
                fontsize=10
            )

        # 设置标题和标签
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel('模型', fontsize=12)
        ax.set_ylabel('使用次数', fontsize=12)

        # 旋转X轴标签
        plt.xticks(rotation=45, ha='right')

        # 添加网格
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')

        # 保存图表
        filepath = os.path.join(self.output_dir, f"{filename}.png")
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        return filepath

    def _generate_empty_chart(self, title: str, filename: str) -> str:
        """生成空数据占位图"""
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.text(
            0.5, 0.5,
            '暂无数据',
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=20,
            color='gray'
        )

        ax.set_title(title, fontsize=16, pad=20)
        ax.axis('off')

        filepath = os.path.join(self.output_dir, f"{filename}.png")
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        return filepath

    def cleanup_old_charts(self, days: int = 7):
        """清理旧的图表文件"""
        now = datetime.now()
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath):
                file_age = now - datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_age.days > days:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
