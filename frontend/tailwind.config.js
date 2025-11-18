/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#121214',
          lighter: '#1a1a1c'
        },
        limeGlow: '#C6FF00',
        aquaGlow: '#00F5A0',
        violetGlow: '#9B5DE5',
        darkGlass: 'rgba(14, 14, 16, 0.7)',
        lightGlass: 'rgba(255, 255, 255, 0.1)'
      },
      keyframes: {
        pulse: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.7 }
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' }
        },
        glow: {
          '0%, 100%': { filter: 'brightness(1)' },
          '50%': { filter: 'brightness(1.2)' }
        }
      },
      animation: {
        pulse: 'pulse 4s ease-in-out infinite',
        float: 'float 6s ease-in-out infinite',
        glow: 'glow 3s ease-in-out infinite'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        neon: '0 0 8px rgba(198, 255, 0, 0.5), 0 0 16px rgba(0, 245, 160, 0.3)',
        violetNeon: '0 0 8px rgba(155, 93, 229, 0.5), 0 0 16px rgba(155, 93, 229, 0.3)',
        glass: '0 4px 24px rgba(0, 0, 0, 0.2)'
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'lime-aqua-gradient': 'linear-gradient(135deg, #C6FF00 0%, #00F5A0 100%)',
        'violet-blue-gradient': 'linear-gradient(135deg, #9B5DE5 0%, #7D4CDB 100%)'
      }
    },
  },
  plugins: [],
};