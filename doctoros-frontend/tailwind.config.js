/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Manrope Variable"', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['"Fraunces Variable"', 'ui-serif', 'Georgia', 'serif'],
        label: ['"Cinzel Variable"', 'ui-serif', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono Variable"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        white: '#FFFBF1', // warm "paper white" used for cards, inputs and modals
        // Warm sepia replaces the cold grey scale everywhere (text-slate-*, border-slate-*, ...)
        slate: {
          50: '#FAF6EC', 100: '#F3ECDC', 200: '#E4D9C0', 300: '#CFC1A3', 400: '#A39577',
          500: '#7C705A', 600: '#5E5343', 700: '#463D31', 800: '#2E2721', 900: '#1B1612',
        },
        paper: { 50: '#FBF5E6', 100: '#F6ECD3', 200: '#EEDFBB', 300: '#DFCB98', 400: '#C9AE70' },
        ink: { 500: '#5A4B3D', 600: '#43372C', 700: '#31281F', 800: '#221B15', 900: '#16110D' },
        // sage / teal waves from the artwork
        brand: {
          50: '#EEF5F3', 100: '#D6E7E3', 200: '#B2D1CC', 300: '#8DB8B2', 400: '#6FA19B',
          500: '#5A8C8C', 600: '#47797B', 700: '#346062', 800: '#264B4D', 900: '#1B3739',
        },
        // ochre / gold = AI accent
        ai: { 50: '#FBF3DC', 100: '#F6E5B3', 200: '#EBCF82', 500: '#C58A1E', 600: '#9C6A14', 700: '#7A500C' },
        rust: { 50: '#FBEDEA', 100: '#F4D2CC', 500: '#B3382F', 600: '#962B24', 700: '#782019' },
        moss: { 50: '#EDF4EA', 100: '#D3E6CC', 500: '#4F8A5B', 600: '#3C7048', 700: '#2D5636' },
        azure: { 50: '#E8F0F5', 100: '#CFE0EA', 500: '#3E7A99', 700: '#245570' },
      },
      keyframes: {
        fadeUp: { '0%': { opacity: 0, transform: 'translateY(10px)' }, '100%': { opacity: 1, transform: 'translateY(0)' } },
        float: { '0%,100%': { transform: 'translate3d(0,0,0)' }, '50%': { transform: 'translate3d(0,-12px,0)' } },
        coin: { '0%': { transform: 'rotateY(0deg)' }, '100%': { transform: 'rotateY(360deg)' } },
        ring: { '0%': { transform: 'rotateY(0deg)' }, '100%': { transform: 'rotateY(360deg)' } },
        sway: { '0%,100%': { transform: 'rotateY(-10deg) rotateX(3deg)' }, '50%': { transform: 'rotateY(10deg) rotateX(-3deg)' } },
      },
      animation: {
        fadeUp: 'fadeUp .45s cubic-bezier(.2,.7,.2,1) both',
        float: 'float 7s ease-in-out infinite',
        coin: 'coin 14s linear infinite',
        ring: 'ring 32s linear infinite',
        sway: 'sway 12s ease-in-out infinite',
      },
      boxShadow: {
        soft: '0 14px 34px -16px rgba(52,34,16,.45), 0 2px 0 rgba(255,255,255,.7) inset',
        deep: '0 30px 60px -24px rgba(22,17,13,.7)',
      },
    },
  },
  plugins: [],
};
