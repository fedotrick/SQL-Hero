import { motion, HTMLMotionProps } from "framer-motion";
import { forwardRef } from "react";

export type CardVariant = "default" | "elevated" | "outlined";
export type CardPadding = "none" | "sm" | "md" | "lg";

export interface CardProps extends HTMLMotionProps<"div"> {
  variant?: CardVariant;
  padding?: CardPadding;
  interactive?: boolean;
}

const variantStyles: Record<CardVariant, string> = {
  default: "bg-telegram-section-bg",
  elevated: "bg-telegram-section-bg shadow-lg",
  outlined: "bg-telegram-section-bg border border-telegram-section-separator",
};

const paddingStyles: Record<CardPadding, string> = {
  none: "",
  sm: "p-3",
  md: "p-4",
  lg: "p-6",
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = "default",
      padding = "md",
      interactive = false,
      children,
      className = "",
      ...props
    },
    ref
  ) => {
    const baseStyles = "rounded-lg transition-all";
    const interactiveStyles = interactive ? "cursor-pointer hover:shadow-md" : "";
    
    return (
      <motion.div
        ref={ref}
        className={`${baseStyles} ${variantStyles[variant]} ${paddingStyles[padding]} ${interactiveStyles} ${className}`}
        whileHover={interactive ? { scale: 1.02 } : undefined}
        whileTap={interactive ? { scale: 0.98 } : undefined}
        transition={{ duration: 0.2 }}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

Card.displayName = "Card";

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ children, className = "", ...props }, ref) => {
    return (
      <div ref={ref} className={`mb-3 ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardHeader.displayName = "CardHeader";

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

export const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ children, className = "", ...props }, ref) => {
    return (
      <h3 ref={ref} className={`text-lg font-semibold text-telegram-text ${className}`} {...props}>
        {children}
      </h3>
    );
  }
);

CardTitle.displayName = "CardTitle";

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ children, className = "", ...props }, ref) => {
    return (
      <div ref={ref} className={`text-telegram-text ${className}`} {...props}>
        {children}
      </div>
    );
  }
);

CardContent.displayName = "CardContent";
