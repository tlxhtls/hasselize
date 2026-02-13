import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // 소프트 파스텔 컬러 팔레트
        pastel: {
          lavender: {
            DEFAULT: '#E6E6FA',
            50: '#F5F5FF',
            100: '#E6E6FA',
            200: '#D0D0F0',
            300: '#B8B8E8',
            400: '#A0A0E0',
            500: '#8888D8',
            600: '#7070C8',
          },
          mint: {
            DEFAULT: '#C1E1C1',
            50: '#E8F5E8',
            100: '#C1E1C1',
            200: '#A8D5A8',
            300: '#8FC98F',
            400: '#76BD76',
            500: '#5DB15D',
            600: '#44A544',
          },
          peach: {
            DEFAULT: '#FFDAB9',
            50: '#FFF5EE',
            100: '#FFDAB9',
            200: '#FFCBA8',
            300: '#FFBC97',
            400: '#FFAD86',
            500: '#FF9E75',
            600: '#FF8F64',
          },
          skyBlue: {
            DEFAULT: '#87CEEB',
            50: '#E8F5FC',
            100: '#C5E8F7',
            200: '#87CEEB',
            300: '#5BBEE8',
            400: '#2FAEE5',
            500: '#009EE2',
            600: '#008ED0',
          },
          pink: {
            DEFAULT: '#FFB6C1',
            50: '#FFF0F2',
            100: '#FFB6C1',
            200: '#FFA0AB',
            300: '#FF8AA5',
            400: '#FF749F',
            500: '#FF5E99',
            600: '#FF4893',
          },
        },

        // 프라이머리 컬러 (라벤더 기반)
        primary: {
          50: '#F5F5FF',
          100: '#E6E6FA',
          200: '#D0D0F0',
          300: '#B8B8E8',
          400: '#A0A0E0',
          500: '#8888D8',
          600: '#7070C8',
          700: '#5858B0',
          800: '#404098',
          900: '#282880',
        },

        // 세컨더리 컬러 (민트 기반)
        secondary: {
          50: '#E8F5E8',
          100: '#C1E1C1',
          200: '#A8D5A8',
          300: '#8FC98F',
          400: '#76BD76',
          500: '#5DB15D',
          600: '#44A544',
          700: '#2D8F2D',
          800: '#167917',
          900: '#006300',
        },

        // 업센트 컬러 (피치 기반)
        accent: {
          50: '#FFF5EE',
          100: '#FFDAB9',
          200: '#FFCBA8',
          300: '#FFBC97',
          400: '#FFAD86',
          500: '#FF9E75',
          600: '#FF8F64',
          700: '#FF8053',
          800: '#FF7142',
          900: '#FF6231',
        },

        // 소프트 뉴트럴 컬러
        neutral: {
          50: '#FAFAFA',
          100: '#F5F5F5',
          200: '#E8E8E8',
          300: '#D0D0D0',
          400: '#A0A0A0',
          500: '#707070',
          600: '#505050',
          700: '#404040',
          800: '#303030',
          900: '#202020',
        },
      },
      fontFamily: {
        sans: [
          'var(--font-geist-sans)',
          '-apple-system',
          'BlinkMacSystemFont',
          'Pretendard',
          'system-ui',
          'sans-serif',
        ],
        mono: ['var(--font-geist-mono)', 'monospace'],
      },
      borderRadius: {
        'soft': '1rem',
        'softer': '1.5rem',
        'softest': '2rem',
      },
      boxShadow: {
        'soft': '0 4px 20px rgba(0, 0, 0, 0.05)',
        'soft-lg': '0 8px 30px rgba(0, 0, 0, 0.08)',
        'soft-xl': '0 12px 40px rgba(0, 0, 0, 0.1)',
        'inner-soft': 'inset 0 2px 10px rgba(0, 0, 0, 0.03)',
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
    },
  },
  plugins: [],
}
export default config
