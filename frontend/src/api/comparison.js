/**
 * 检测结果对比 API
 */
import request from '@/utils/request'

/**
 * 对比多个检测结果
 * @param {string|number[]} ids - 检测记录ID列表（逗号分隔字符串或数组）
 * @param {number} iouThreshold - IOU阈值（可选，默认0.5）
 * @returns {Promise} 对比结果
 */
export function compareDetections(ids, iouThreshold = 0.5) {
  // 将数组转换为逗号分隔的字符串
  const idsStr = Array.isArray(ids) ? ids.join(',') : ids

  return request({
    url: '/comparison/compare',
    method: 'get',
    params: {
      ids: idsStr,
      iou_threshold: iouThreshold
    }
  })
}
