import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        glow: '0 0 0 1px rgba(147,197,253,0.2), 0 10px 30px -15px rgba(59,130,246,0.5)',
      },
    },
  },
  plugins: [],
}

export default config
