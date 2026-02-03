/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0B0E14',
        'dark-surface': '#121826',
        'dark-border': '#1E2A36',
        'dark-text': '#E6EEF7',
        'caramelo': {
          DEFAULT: '#D4A373',
          hover: '#E7B984',
          accent: '#C58B3A',
          dark: '#A67C52',
        },
        'accent-blue': '#D4A373',
        'accent-green': '#22C55E',
      },
    },
  },
  plugins: [],
}
