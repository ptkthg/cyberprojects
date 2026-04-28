import type { Config } from 'tailwindcss';
export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#020617',
        surface: '#0b1220',
        surface2: '#111827',
        cyan: '#38bdf8'
      }
    }
  }
} satisfies Config;
