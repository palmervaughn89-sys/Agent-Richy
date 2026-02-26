/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50:  '#E8ECF1',
          100: '#C5CFD9',
          200: '#8A9BB4',
          300: '#5A7190',
          400: '#3A506E',
          500: '#1E3350',
          600: '#162A44',
          700: '#111D32',
          800: '#0F2035',
          900: '#0A1628',
          950: '#060E1A',
          DEFAULT: '#0A1628',
          light: '#0F2035',
          card: '#111D32',
        },
        brand: {
          blue: '#2563EB',
          'blue-light': '#3B82F6',
          gold: '#F59E0B',
          'gold-light': '#FBBF24',
          green: '#10B981',
          'green-light': '#34D399',
          red: '#EF4444',
          'red-light': '#F87171',
          purple: '#8B5CF6',
          cyan: '#06B6D4',
        },
        gold: {
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
        },
        surface: {
          DEFAULT: '#0F172A',
          alt: '#1E293B',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-soft': 'pulse 3s infinite',
        'wiggle': 'wiggle 0.5s ease-in-out',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
