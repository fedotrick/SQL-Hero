export const designTokens = {
  colors: {
    primary: "var(--tg-theme-button-color)",
    primaryText: "var(--tg-theme-button-text-color)",
    text: "var(--tg-theme-text-color)",
    hint: "var(--tg-theme-hint-color)",
    link: "var(--tg-theme-link-color)",
    bg: "var(--tg-theme-bg-color)",
    secondaryBg: "var(--tg-theme-secondary-bg-color)",
    sectionBg: "var(--tg-theme-section-bg-color)",
    separator: "var(--tg-theme-section-separator-color)",
    accent: "var(--tg-theme-accent-text-color)",
    destructive: "var(--tg-theme-destructive-text-color)",
    subtitle: "var(--tg-theme-subtitle-text-color)",
  },
  spacing: {
    xs: "0.25rem", // 4px
    sm: "0.5rem", // 8px
    md: "1rem", // 16px
    lg: "1.5rem", // 24px
    xl: "2rem", // 32px
    "2xl": "3rem", // 48px
  },
  borderRadius: {
    sm: "0.25rem", // 4px
    md: "0.5rem", // 8px
    lg: "0.75rem", // 12px
    xl: "1rem", // 16px
    full: "9999px",
  },
  fontSize: {
    xs: "0.75rem", // 12px
    sm: "0.875rem", // 14px
    base: "1rem", // 16px
    lg: "1.125rem", // 18px
    xl: "1.25rem", // 20px
    "2xl": "1.5rem", // 24px
    "3xl": "1.875rem", // 30px
  },
  fontWeight: {
    normal: "400",
    medium: "500",
    semibold: "600",
    bold: "700",
  },
  shadow: {
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
  },
  transition: {
    fast: "150ms cubic-bezier(0.4, 0, 0.2, 1)",
    base: "200ms cubic-bezier(0.4, 0, 0.2, 1)",
    slow: "300ms cubic-bezier(0.4, 0, 0.2, 1)",
  },
} as const;
