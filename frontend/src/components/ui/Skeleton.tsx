import { motion, type HTMLMotionProps } from "framer-motion";
import { forwardRef } from "react";

export interface SkeletonProps extends HTMLMotionProps<"div"> {
  width?: string;
  height?: string;
  circle?: boolean;
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(
  ({ width, height, circle = false, className = "", style, ...props }, ref) => {
    const defaultStyle = {
      width: width || "100%",
      height: height || "1rem",
      ...style,
    };

    return (
      <motion.div
        ref={ref}
        className={`bg-telegram-secondary-bg animate-pulse ${circle ? "rounded-full" : "rounded"} ${className}`}
        style={defaultStyle}
        initial={{ opacity: 0.6 }}
        animate={{ opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        {...props}
      />
    );
  }
);

Skeleton.displayName = "Skeleton";
