/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 深海科技主题色
        'deep-blue': {
          DEFAULT: '#0A2E5B',
          50: '#E6EBF2',
          100: '#CCD8E5',
          200: '#99B1CB',
          300: '#668AB1',
          400: '#336397',
          500: '#0A2E5B',
          600: '#082549',
          700: '#061C37',
          800: '#041225',
          900: '#020913',
        },
        'coral-orange': {
          DEFAULT: '#FF7F50',
          50: '#FFF5F2',
          100: '#FFE8E0',
          200: '#FFD1C1',
          300: '#FFBAA2',
          400: '#FFA383',
          500: '#FF7F50',
          600: '#FF5C2B',
          700: '#FF3906',
          800: '#E02700',
          900: '#B51F00',
        },
        'bright-cyan': {
          DEFAULT: '#00BFFF',
          50: '#E5F7FF',
          100: '#CCEFFF',
          200: '#99DFFF',
          300: '#66CFFF',
          400: '#33BFFF',
          500: '#00BFFF',
          600: '#0099CC',
          700: '#007399',
          800: '#004D66',
          900: '#002633',
        },
        'light-gray': '#F4F7FA',
        'dark-gray': '#34495E',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(10, 46, 91, 0.08)',
        'medium': '0 4px 20px rgba(10, 46, 91, 0.12)',
        'strong': '0 8px 32px rgba(10, 46, 91, 0.16)',
        'glow-cyan': '0 0 20px rgba(0, 191, 255, 0.3)',
        'glow-orange': '0 0 20px rgba(255, 127, 80, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      backgroundImage: {
        'gradient-deep': 'linear-gradient(135deg, #0A2E5B 0%, #082549 50%, #061C37 100%)',
        'gradient-ocean': 'linear-gradient(135deg, #0A2E5B 0%, #00BFFF 100%)',
        'gradient-sunset': 'linear-gradient(135deg, #FF7F50 0%, #FF5C2B 100%)',
      },
    },
  },
  plugins: [],
}
