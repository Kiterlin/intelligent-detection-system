"""
检测结果对比服务的单元测试
"""
import pytest
import json
from app.services.comparison_service import ComparisonService


class TestComparisonService:
    """测试ComparisonService类"""

    def setup_method(self):
        """每个测试方法前执行，初始化服务实例"""
        self.service = ComparisonService(iou_threshold=0.5)

    def test_calculate_iou_no_overlap(self):
        """测试IOU计算 - 无重叠"""
        bbox1 = [0, 0, 10, 10]
        bbox2 = [20, 20, 30, 30]
        iou = self.service.calculate_iou(bbox1, bbox2)
        assert iou == 0.0

    def test_calculate_iou_perfect_overlap(self):
        """测试IOU计算 - 完全重叠"""
        bbox1 = [0, 0, 10, 10]
        bbox2 = [0, 0, 10, 10]
        iou = self.service.calculate_iou(bbox1, bbox2)
        assert iou == 1.0

    def test_calculate_iou_partial_overlap(self):
        """测试IOU计算 - 部分重叠"""
        bbox1 = [0, 0, 10, 10]  # 面积 100
        bbox2 = [5, 5, 15, 15]  # 面积 100
        # 交集: [5,5,10,10] 面积 25
        # 并集: 100 + 100 - 25 = 175
        # IOU: 25 / 175 ≈ 0.1429
        iou = self.service.calculate_iou(bbox1, bbox2)
        assert abs(iou - 0.1428571) < 0.001

    def test_calculate_iou_contained(self):
        """测试IOU计算 - 一个包含另一个"""
        bbox1 = [0, 0, 20, 20]  # 面积 400
        bbox2 = [5, 5, 15, 15]  # 面积 100（完全在bbox1内）
        # 交集: bbox2 面积 100
        # 并集: 400
        # IOU: 100 / 400 = 0.25
        iou = self.service.calculate_iou(bbox1, bbox2)
        assert abs(iou - 0.25) < 0.001

    def test_parse_detection_result_new_format(self):
        """测试解析检测结果 - 新格式"""
        result_json = json.dumps({
            "detections": [
                {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
                {"class_name": "coral", "confidence": 0.8, "bbox": [50, 60, 70, 80]}
            ],
            "count": 2
        })
        detections = self.service.parse_detection_result(result_json)
        assert len(detections) == 2
        assert detections[0]["class_name"] == "fish"
        assert detections[1]["class_name"] == "coral"

    def test_parse_detection_result_old_format(self):
        """测试解析检测结果 - 旧格式"""
        result_json = json.dumps([
            {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
            {"class_name": "coral", "confidence": 0.8, "bbox": [50, 60, 70, 80]}
        ])
        detections = self.service.parse_detection_result(result_json)
        assert len(detections) == 2
        assert detections[0]["class_name"] == "fish"

    def test_parse_detection_result_empty(self):
        """测试解析检测结果 - 空结果"""
        detections = self.service.parse_detection_result(None)
        assert detections == []

        detections = self.service.parse_detection_result("")
        assert detections == []

    def test_parse_detection_result_invalid_json(self):
        """测试解析检测结果 - 无效JSON"""
        detections = self.service.parse_detection_result("invalid json")
        assert detections == []

    def test_match_objects_perfect_match(self):
        """测试对象匹配 - 完美匹配"""
        detections1 = [
            {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
            {"class_name": "coral", "confidence": 0.8, "bbox": [50, 60, 70, 80]}
        ]
        detections2 = [
            {"class_name": "fish", "confidence": 0.85, "bbox": [10, 20, 30, 40]},
            {"class_name": "coral", "confidence": 0.75, "bbox": [50, 60, 70, 80]}
        ]

        result = self.service.match_objects(detections1, detections2)

        assert result['match_stats']['common_count'] == 2
        assert result['match_stats']['unique_to_first_count'] == 0
        assert result['match_stats']['unique_to_second_count'] == 0
        assert result['match_stats']['match_rate'] == 100.0

    def test_match_objects_no_match(self):
        """测试对象匹配 - 无匹配"""
        detections1 = [
            {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
        ]
        detections2 = [
            {"class_name": "coral", "confidence": 0.8, "bbox": [100, 200, 300, 400]},
        ]

        result = self.service.match_objects(detections1, detections2)

        assert result['match_stats']['common_count'] == 0
        assert result['match_stats']['unique_to_first_count'] == 1
        assert result['match_stats']['unique_to_second_count'] == 1

    def test_match_objects_partial_match(self):
        """测试对象匹配 - 部分匹配"""
        detections1 = [
            {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
            {"class_name": "coral", "confidence": 0.8, "bbox": [50, 60, 70, 80]},
            {"class_name": "shark", "confidence": 0.95, "bbox": [100, 100, 150, 150]}
        ]
        detections2 = [
            {"class_name": "fish", "confidence": 0.85, "bbox": [10, 20, 30, 40]},
            {"class_name": "turtle", "confidence": 0.7, "bbox": [200, 200, 250, 250]}
        ]

        result = self.service.match_objects(detections1, detections2)

        # fish匹配，coral和shark是unique_to_first，turtle是unique_to_second
        assert result['match_stats']['common_count'] == 1
        assert result['match_stats']['unique_to_first_count'] == 2
        assert result['match_stats']['unique_to_second_count'] == 1

    def test_match_objects_class_mismatch(self):
        """测试对象匹配 - 位置匹配但类别不同"""
        detections1 = [
            {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
        ]
        detections2 = [
            {"class_name": "coral", "confidence": 0.8, "bbox": [10, 20, 30, 40]},
        ]

        result = self.service.match_objects(detections1, detections2)

        # 位置完全重叠（IOU=1.0），应该匹配
        assert result['match_stats']['common_count'] == 1
        # 但类别不匹配
        assert result['common_objects'][0]['class_match'] is False

    def test_match_objects_empty_detections(self):
        """测试对象匹配 - 空检测结果"""
        result = self.service.match_objects([], [])
        assert result['match_stats']['common_count'] == 0
        assert result['match_stats']['total_in_first'] == 0
        assert result['match_stats']['total_in_second'] == 0

    def test_compare_detections_two_results(self):
        """测试完整对比流程 - 两个结果"""
        results = [
            {
                'detection_id': 1,
                'result_json': json.dumps({
                    "detections": [
                        {"class_name": "fish", "confidence": 0.9, "bbox": [10, 20, 30, 40]},
                        {"class_name": "coral", "confidence": 0.8, "bbox": [50, 60, 70, 80]}
                    ]
                }),
                'metadata': {'model_id': 1}
            },
            {
                'detection_id': 2,
                'result_json': json.dumps({
                    "detections": [
                        {"class_name": "fish", "confidence": 0.85, "bbox": [10, 20, 30, 40]}
                    ]
                }),
                'metadata': {'model_id': 2}
            }
        ]

        comparison_result = self.service.compare_detections(results)

        assert len(comparison_result['records']) == 2
        assert comparison_result['records'][0]['detection_id'] == 1
        assert comparison_result['records'][0]['count'] == 2
        assert comparison_result['records'][1]['detection_id'] == 2
        assert comparison_result['records'][1]['count'] == 1

        # fish应该被匹配，coral是unique_to_first
        assert comparison_result['comparison']['match_stats']['common_count'] == 1
        assert comparison_result['comparison']['match_stats']['unique_to_first_count'] == 1

    def test_compare_detections_insufficient_results(self):
        """测试对比 - 结果数量不足"""
        results = [
            {
                'detection_id': 1,
                'result_json': json.dumps({"detections": []}),
                'metadata': {}
            }
        ]

        with pytest.raises(ValueError, match="至少需要2个检测结果"):
            self.service.compare_detections(results)

    def test_calculate_statistics_comparison(self):
        """测试统计对比"""
        record1 = {
            'detected_objects_count': 10,
            'processing_time': 1.5,
            'model_id': 1,
            'confidence_threshold': 0.25,
            'iou_threshold': 0.45
        }
        record2 = {
            'detected_objects_count': 15,
            'processing_time': 2.0,
            'model_id': 2,
            'confidence_threshold': 0.3,
            'iou_threshold': 0.5
        }

        stats = self.service.calculate_statistics_comparison(record1, record2)

        assert stats['detection_count']['first'] == 10
        assert stats['detection_count']['second'] == 15
        assert stats['detection_count']['diff'] == 5

        assert stats['processing_time']['first'] == 1.5
        assert stats['processing_time']['second'] == 2.0
        assert stats['processing_time']['diff'] == 0.5

        assert stats['model']['first'] == 1
        assert stats['model']['second'] == 2
        assert stats['model']['same'] is False

    def test_iou_threshold_effect(self):
        """测试IOU阈值的影响"""
        detections1 = [
            {"class_name": "fish", "confidence": 0.9, "bbox": [0, 0, 10, 10]},
        ]
        detections2 = [
            # 部分重叠，IOU约0.14
            {"class_name": "fish", "confidence": 0.8, "bbox": [5, 5, 15, 15]},
        ]

        # 使用高阈值（0.5），不应匹配
        service_high = ComparisonService(iou_threshold=0.5)
        result_high = service_high.match_objects(detections1, detections2)
        assert result_high['match_stats']['common_count'] == 0

        # 使用低阈值（0.1），应该匹配
        service_low = ComparisonService(iou_threshold=0.1)
        result_low = service_low.match_objects(detections1, detections2)
        assert result_low['match_stats']['common_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
