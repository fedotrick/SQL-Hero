import { motion } from "framer-motion";
import { forwardRef } from "react";

export type ProgressBarSize = "sm" | "md" | "lg";
export type ProgressBarVariant = "default" | "success" | "warning" | "error";

export interface ProgressBarProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: ProgressBarSize;
  variant?: ProgressBarVariant;
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
}

const sizeStyles: Record<ProgressBarSize, string> = {
  sm: "h-1",
  md: "h-2",
  lg: "h-3",
};

const variantStyles: Record<ProgressBarVariant, string> = {
  default: "bg-telegram-button",
  success: "bg-green-500",
  warning: "bg-yellow-500",
  error: "bg-red-500",
};

export const ProgressBar = forwardRef<HTMLDivElement, ProgressBarProps>(
  (
    {
      value,
      max = 100,
      size = "md",
      variant = "default",
      showLabel = false,
      label,
      animated = true,
      className = "",
      ...props
    },
    ref
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    const displayLabel = label || `${Math.round(percentage)}%`;

    return (
      <div ref={ref} className={`w-full ${className}`} {...props}>
        {showLabel && (
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-telegram-text">{displayLabel}</span>
            <span className="text-sm text-telegram-subtitle">{Math.round(percentage)}%</span>
          </div>
        )}
        <div className={`w-full bg-telegram-secondary-bg rounded-full overflow-hidden ${sizeStyles[size]}`}>
          <motion.div
            className={`h-full rounded-full ${variantStyles[variant]}`}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{
              duration: animated ? 0.5 : 0,
              ease: "easeOut",
            }}
          />
        </div>
      </div>
    );
  }
);

ProgressBar.displayName = "ProgressBar";

export interface CircularProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  variant?: ProgressBarVariant;
  showLabel?: boolean;
}

export const CircularProgress = forwardRef<HTMLDivElement, CircularProgressProps>(
  (
    {
      value,
      max = 100,
      size = 64,
      strokeWidth = 4,
      variant = "default",
      showLabel = true,
      className = "",
      ...props
    },
    ref
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    const strokeColor = {
      default: "var(--tg-theme-button-color)",
      success: "#10b981",
      warning: "#eab308",
      error: "#ef4444",
    }[variant];

    return (
      <div ref={ref} className={`relative inline-flex items-center justify-center ${className}`} {...props}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="var(--tg-theme-secondary-bg-color)"
            strokeWidth={strokeWidth}
            fill="none"
          />
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </svg>
        {showLabel && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-sm font-semibold text-telegram-text">{Math.round(percentage)}%</span>
          </div>
        )}
      </div>
    );
  }
);

CircularProgress.displayName = "CircularProgress";
