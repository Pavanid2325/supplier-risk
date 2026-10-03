/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          950: '#090d16',
          900: '#0f172a',
          850: '#152035',
          800: '#1e293b',
          700: '#334155'
        },
        cyan: {
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2'
        },
        emerald: {
          400: '#34d399',
          500: '#10b981'
        },
        amber: {
          400: '#fbbf24',
          500: '#f59e0b'
        }
      }
    },
  },
  plugins: [],
}
