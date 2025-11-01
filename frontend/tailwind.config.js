/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      screens: {
        telegram: { max: "480px" },
      },
      colors: {
        telegram: {
          bg: "var(--tg-theme-bg-color)",
          text: "var(--tg-theme-text-color)",
          hint: "var(--tg-theme-hint-color)",
          link: "var(--tg-theme-link-color)",
          button: "var(--tg-theme-button-color)",
          "button-text": "var(--tg-theme-button-text-color)",
          "secondary-bg": "var(--tg-theme-secondary-bg-color)",
          "header-bg": "var(--tg-theme-header-bg-color)",
          "section-bg": "var(--tg-theme-section-bg-color)",
          "section-separator": "var(--tg-theme-section-separator-color)",
          "accent-text": "var(--tg-theme-accent-text-color)",
          destructive: "var(--tg-theme-destructive-text-color)",
          subtitle: "var(--tg-theme-subtitle-text-color)",
        },
      },
      maxWidth: {
        telegram: "480px",
      },
    },
  },
  plugins: [],
};
