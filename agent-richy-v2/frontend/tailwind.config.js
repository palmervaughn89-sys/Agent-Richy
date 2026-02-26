/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        /* ── New design system ─────────────────────────── */
        bg:        '#000000',
        s1:        '#080C0A',
        s2:        '#0C1210',
        card:      { DEFAULT: '#101A15', hover: '#162420' },
        accent:    { DEFAULT: '#00E87B', dim: '#00C968', dark: '#009E52' },
        ghost:     'rgba(0,232,123,.06)',
        glow:      'rgba(0,232,123,.18)',
        txt:       { DEFAULT: '#F2F8F5', off: '#B8C9C0', muted: '#5E736A' },
        line:      { DEFAULT: 'rgba(255,255,255,.06)', hover: 'rgba(0,232,123,.25)' },
        /* Keep some legacy tokens for non-migrated code */
        navy: {
          700: '#111D32', 800: '#0F2035', 900: '#0A1628', 950: '#060E1A',
          DEFAULT: '#0A1628',
        },
        surface: { DEFAULT: '#0C1210', alt: '#101A15' },
      },
      fontFamily: {
        sans:  ['Outfit', 'system-ui', 'sans-serif'],
        mono:  ['IBM Plex Mono', 'monospace'],
      },
      letterSpacing: {
        label: '0.12em',
        tight: '-0.035em',
        tighter: '-0.045em',
      },
      borderRadius: {
        card: '14px',
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-soft':  'pulse 3s infinite',
        'float':       'float 3s ease-in-out infinite',
        'marquee':     'marquee 30s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-10px)' },
        },
        marquee: {
          '0%':   { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [],
};
