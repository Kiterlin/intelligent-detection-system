module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    // 允许单词组件名（如 Home, Login 等）
    'vue/multi-word-component-names': 'off',

    // 生产环境警告console，开发环境允许
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',

    // 未使用变量警告而非错误
    'vue/no-unused-vars': 'warn',
    'no-unused-vars': 'warn',

    // Vue 3特定规则
    'vue/require-default-prop': 'off',
    'vue/no-v-html': 'warn',

    // 代码风格（可选）
    'vue/html-indent': ['error', 2],
    'vue/max-attributes-per-line': 'off',
    'vue/singleline-html-element-content-newline': 'off'
  }
}
