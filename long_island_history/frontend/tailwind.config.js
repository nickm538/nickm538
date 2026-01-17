/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'li-blue': '#1e3a5f',
        'li-gold': '#c9a227',
        'li-sand': '#f5e6d3',
      },
      fontFamily: {
        'serif': ['Georgia', 'Cambria', 'serif'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
