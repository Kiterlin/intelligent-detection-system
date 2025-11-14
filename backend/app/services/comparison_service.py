"""
检测结果对比服务

提供检测结果的对象匹配和差异分析功能
"""
import json
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger


class ComparisonService:
    """检测结果对比服务类"""

    def __init__(self, iou_threshold: float = 0.5):
        """
        初始化对比服务

        Args:
            iou_threshold: IOU阈值，用于判断两个边界框是否匹配同一对象
        """
        self.iou_threshold = iou_threshold

    @staticmethod
    def calculate_iou(bbox1: List[float], bbox2: List[float]) -> float:
        """
        计算两个边界框的交并比（IOU）

        Args:
            bbox1: 边界框1 [x1, y1, x2, y2]
            bbox2: 边界框2 [x1, y1, x2, y2]

        Returns:
            IOU值 (0-1之间)
        """
        # 解析坐标
        x1_min, y1_min, x1_max, y1_max = bbox1
        x2_min, y2_min, x2_max, y2_max = bbox2

        # 计算交集区域坐标
        inter_xmin = max(x1_min, x2_min)
        inter_ymin = max(y1_min, y2_min)
        inter_xmax = min(x1_max, x2_max)
        inter_ymax = min(y1_max, y2_max)

        # 计算交集面积
        inter_width = max(0, inter_xmax - inter_xmin)
        inter_height = max(0, inter_ymax - inter_ymin)
        inter_area = inter_width * inter_height

        # 如果没有交集
        if inter_area == 0:
            return 0.0

        # 计算各自的面积
        bbox1_area = (x1_max - x1_min) * (y1_max - y1_min)
        bbox2_area = (x2_max - x2_min) * (y2_max - y2_min)

        # 计算并集面积
        union_area = bbox1_area + bbox2_area - inter_area

        # 避免除零
        if union_area == 0:
            return 0.0

        # 返回IOU
        return inter_area / union_area

    def match_objects(
        self,
        detections1: List[Dict[str, Any]],
        detections2: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        匹配两个检测结果中的对象

        使用IOU算法找出共同对象和独有对象

        Args:
            detections1: 检测结果1的对象列表
            detections2: 检测结果2的对象列表

        Returns:
            匹配结果字典，包含：
            - common_objects: 共同对象（两边都检测到）
            - unique_to_first: 仅在第一个结果中的对象
            - unique_to_second: 仅在第二个结果中的对象
            - match_stats: 匹配统计信息
        """
        # 跟踪已匹配的索引
        matched_in_second = set()

        common_objects = []
        unique_to_first = []

        # 遍历第一个检测结果
        for idx1, obj1 in enumerate(detections1):
            bbox1 = obj1.get('bbox', [])
            if not bbox1 or len(bbox1) != 4:
                continue

            best_match_idx = None
            best_iou = 0.0

            # 在第二个结果中寻找最佳匹配
            for idx2, obj2 in enumerate(detections2):
                if idx2 in matched_in_second:
                    continue

                bbox2 = obj2.get('bbox', [])
                if not bbox2 or len(bbox2) != 4:
                    continue

                # 计算IOU
                iou = self.calculate_iou(bbox1, bbox2)

                # 更新最佳匹配
                if iou > best_iou:
                    best_iou = iou
                    best_match_idx = idx2

            # 如果找到匹配（IOU超过阈值）
            if best_match_idx is not None and best_iou >= self.iou_threshold:
                matched_in_second.add(best_match_idx)
                obj2 = detections2[best_match_idx]

                common_objects.append({
                    'first': obj1,
                    'second': obj2,
                    'iou': round(best_iou, 3),
                    'class_match': obj1.get('class_name') == obj2.get('class_name'),
                })
            else:
                # 没有找到匹配，是独有对象
                unique_to_first.append(obj1)

        # 第二个结果中未匹配的对象
        unique_to_second = [
            obj for idx, obj in enumerate(detections2)
            if idx not in matched_in_second
        ]

        # 统计信息
        match_stats = {
            'total_in_first': len(detections1),
            'total_in_second': len(detections2),
            'common_count': len(common_objects),
            'unique_to_first_count': len(unique_to_first),
            'unique_to_second_count': len(unique_to_second),
            'match_rate': round(
                len(common_objects) / max(len(detections1), 1) * 100, 2
            ) if detections1 else 0.0,
        }

        return {
            'common_objects': common_objects,
            'unique_to_first': unique_to_first,
            'unique_to_second': unique_to_second,
            'match_stats': match_stats,
        }

    @staticmethod
    def parse_detection_result(result_json: Optional[str]) -> List[Dict[str, Any]]:
        """
        解析检测结果JSON

        兼容新旧格式：
        - 新格式: {"detections": [...], "count": N}
        - 旧格式: [...]

        Args:
            result_json: 检测结果的JSON字符串

        Returns:
            检测对象列表
        """
        if not result_json:
            return []

        try:
            result_data = json.loads(result_json)

            # 新格式
            if isinstance(result_data, dict):
                return result_data.get("detections", [])
            # 旧格式
            elif isinstance(result_data, list):
                return result_data
            else:
                logger.warning(f"未知的检测结果格式: {type(result_data)}")
                return []

        except json.JSONDecodeError as e:
            logger.error(f"解析检测结果JSON失败: {str(e)}")
            return []

    def compare_detections(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        对比多个检测结果

        Args:
            results: 检测结果列表，每个包含：
                - detection_id: 检测记录ID
                - result_json: 检测结果JSON
                - metadata: 其他元数据（模型、时间等）

        Returns:
            完整的对比分析结果
        """
        if len(results) < 2:
            raise ValueError("至少需要2个检测结果进行对比")

        # 解析所有结果
        parsed_results = []
        for result in results:
            detections = self.parse_detection_result(result.get('result_json'))
            parsed_results.append({
                **result,
                'detections': detections,
                'count': len(detections),
            })

        # 当前仅支持两两对比
        # 未来可扩展为多个结果的复杂对比
        if len(parsed_results) == 2:
            match_result = self.match_objects(
                parsed_results[0]['detections'],
                parsed_results[1]['detections']
            )

            return {
                'records': [
                    {
                        'detection_id': r['detection_id'],
                        'count': r['count'],
                        'metadata': r.get('metadata', {}),
                    }
                    for r in parsed_results
                ],
                'comparison': match_result,
            }
        else:
            # 多结果对比（未来功能）
            return {
                'records': [
                    {
                        'detection_id': r['detection_id'],
                        'count': r['count'],
                        'metadata': r.get('metadata', {}),
                    }
                    for r in parsed_results
                ],
                'comparison': {
                    'message': '暂不支持3个以上结果的对比',
                },
            }

    @staticmethod
    def calculate_statistics_comparison(
        record1: Dict[str, Any],
        record2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        计算两个检测记录的统计对比

        Args:
            record1: 检测记录1
            record2: 检测记录2

        Returns:
            统计对比结果
        """
        return {
            'detection_count': {
                'first': record1.get('detected_objects_count', 0),
                'second': record2.get('detected_objects_count', 0),
                'diff': record2.get('detected_objects_count', 0) - record1.get('detected_objects_count', 0),
            },
            'processing_time': {
                'first': round(record1.get('processing_time', 0), 2),
                'second': round(record2.get('processing_time', 0), 2),
                'diff': round(
                    record2.get('processing_time', 0) - record1.get('processing_time', 0),
                    2
                ),
            },
            'model': {
                'first': record1.get('model_id'),
                'second': record2.get('model_id'),
                'same': record1.get('model_id') == record2.get('model_id'),
            },
            'parameters': {
                'confidence_threshold': {
                    'first': record1.get('confidence_threshold'),
                    'second': record2.get('confidence_threshold'),
                },
                'iou_threshold': {
                    'first': record1.get('iou_threshold'),
                    'second': record2.get('iou_threshold'),
                },
            },
        }
