/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        // Paper & ink
        paper: {
          DEFAULT: '#F6F2EA',
          raised: '#FBF8F1',
          sunken: '#EDE8DC',
        },
        ink: {
          DEFAULT: '#1A1A1A',
          secondary: '#5A564E',
          muted: '#8A857A',
          faint: '#B8B2A3',
        },
        rule: {
          DEFAULT: '#D9D3C3',
          strong: '#B8B2A3',
        },
        // Grine bronze — institutional accent
        bronze: {
          DEFAULT: '#7A5B3F',
          dark: '#5C4430',
          light: '#A68866',
        },
        // Regime semantic (calm, not alarming)
        regime: {
          expansion: '#6B8E4E',   // warm sage
          balanced: '#6B7280',    // dusty slate
          transition: '#B8860B',  // muted amber
          endurance: '#8B5A5A',   // dusky rose
          protection: '#5D3A58',  // deep plum
        },
        // Alignment indicators
        over: '#B8860B',   // amber (overweight warning)
        under: '#6B7280',  // slate (underweight)
        aligned: '#6B8E4E', // sage (aligned)
      },
      letterSpacing: {
        tightest: '-0.04em',
      },
      fontSize: {
        // Institutional scale
        'label': ['0.6875rem', { lineHeight: '1', letterSpacing: '0.12em' }],
        'micro': ['0.75rem', { lineHeight: '1.3' }],
      },
    },
  },
  plugins: [],
};
