import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',  // Ensure it scans all app files
    './pages/**/*.{js,ts,jsx,tsx}', 
    './components/**/*.{js,ts,jsx,tsx}', 
  ],
  theme: {
    extend: {
      colors: {
        primary: '#9BB67C',     // For text and highlights
        secondary: '#E3DFC8',   // For borders or backgrounds
        background: '#F5F1DA',  // For main background color
        accent: '#EEBB4D',      // For buttons and CTA elements
      },
    },
  },
  plugins: [],
};

export default config;

