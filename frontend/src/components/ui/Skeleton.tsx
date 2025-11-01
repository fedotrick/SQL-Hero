import { motion } from "framer-motion";

interface SkeletonProps {
  className?: string;
  variant?: "text" | "circular" | "rectangular";
  width?: string | number;
  height?: string | number;
  animate?: boolean;
}

export const Skeleton = ({
  className = "",
  variant = "rectangular",
  width,
  height,
  animate = true,
}: SkeletonProps) => {
  const baseClasses = "bg-telegram-section-bg";

  const variantClasses = {
    text: "rounded",
    circular: "rounded-full",
    rectangular: "rounded-lg",
  };

  const style: React.CSSProperties = {
    width: width || "100%",
    height: height || (variant === "text" ? "1em" : "100%"),
  };

  const skeletonElement = (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );

  if (!animate) {
    return skeletonElement;
  }

  return (
    <motion.div
      initial={{ opacity: 0.6 }}
      animate={{ opacity: [0.6, 0.8, 0.6] }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      {skeletonElement}
    </motion.div>
  );
};
