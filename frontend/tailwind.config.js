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
        'dark-bg': '#0B0F14',
        'dark-surface': '#121A23',
        'dark-border': '#1E2A36',
        'dark-text': '#E6EEF7',
        'accent-green': '#10B981',
        'accent-blue': '#3B82F6',
      },
    },
  },
  plugins: [],
}
