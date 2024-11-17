/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./**/*.{html,js}'],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#1A1B1E',
          surface: '#25262B',
          elevated: '#2C2D32',
          border: '#383A3F',
          text: 'rgba(255, 255, 255, 0.95)',
          'text-secondary': 'rgba(255, 255, 255, 0.75)'
        },
        ai: {
          chatgpt: '#19C37D',
          claude: '#6B4BCC',
          gemini: '#1B72E8'
        }
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px'
      },
      transitionProperty: {
        'height': 'height',
        'spacing': 'margin, padding',
      }
    }
  },
  plugins: [
    function({ addUtilities }) {
      addUtilities({
        '.line-clamp-2': {
          display: '-webkit-box',
          '-webkit-line-clamp': '2',
          '-webkit-box-orient': 'vertical',
          overflow: 'hidden'
        }
      })
    }
  ]
}
