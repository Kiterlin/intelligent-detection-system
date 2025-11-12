/**
 * 用户状态管理（auth store的别名导出）
 */
import { useAuthStore } from './auth'

export const useUserStore = useAuthStore

// 为了方便使用，也导出别名
export { useAuthStore }
