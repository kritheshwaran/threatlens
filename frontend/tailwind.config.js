/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0E13',
        surface: '#111721',
        surface2: '#171F2B',
        border: {
          DEFAULT: '#232C3A',
          strong: '#2E3947',
        },
        text: {
          primary: '#E7ECF3',
          secondary: '#8D99AC',
          muted: '#5B6779',
        },
        accent: {
          DEFAULT: '#4C8DFF',
          soft: 'rgba(76,141,255,0.12)',
          strong: '#7AAAFF',
        },
        safe: {
          DEFAULT: '#34D399',
          soft: 'rgba(52,211,153,0.12)',
        },
        suspicious: {
          DEFAULT: '#FBBF24',
          soft: 'rgba(251,191,36,0.12)',
        },
        malicious: {
          DEFAULT: '#F87171',
          soft: 'rgba(248,113,113,0.12)',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        card: '0 1px 0 0 rgba(255,255,255,0.02) inset, 0 8px 24px -12px rgba(0,0,0,0.5)',
      },
      keyframes: {
        sweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        scanline: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        sweep: 'sweep 2.2s linear infinite',
        scanline: 'scanline 1.6s ease-in-out infinite',
        fadeUp: 'fadeUp 0.25s ease-out',
      },
    },
  },
  plugins: [],
};