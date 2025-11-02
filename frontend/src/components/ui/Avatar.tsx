import { forwardRef } from "react";
import { motion, type HTMLMotionProps } from "framer-motion";

export type AvatarSize = "sm" | "md" | "lg" | "xl";

export interface AvatarProps extends Omit<HTMLMotionProps<"div">, "size"> {
  name?: string | null;
  src?: string;
  size?: AvatarSize;
  rank?: number;
}

const sizeStyles: Record<AvatarSize, string> = {
  sm: "w-8 h-8 text-xs",
  md: "w-10 h-10 text-sm",
  lg: "w-12 h-12 text-base",
  xl: "w-16 h-16 text-xl",
};

const rankColors: Record<number, string> = {
  1: "bg-gradient-to-br from-yellow-400 to-yellow-600 text-yellow-900",
  2: "bg-gradient-to-br from-gray-300 to-gray-500 text-gray-900",
  3: "bg-gradient-to-br from-orange-400 to-orange-600 text-orange-900",
};

const getInitials = (name?: string | null): string => {
  if (!name) return "?";
  const words = name.trim().split(" ");
  if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase();
  }
  return (words[0][0] + words[1][0]).toUpperCase();
};

export const Avatar = forwardRef<HTMLDivElement, AvatarProps>(
  ({ name, src, size = "md", rank, className = "", ...props }, ref) => {
    const bgColor =
      rank && rankColors[rank] ? rankColors[rank] : "bg-telegram-accent-text text-white";

    return (
      <motion.div
        ref={ref}
        className={`relative inline-flex items-center justify-center rounded-full font-semibold ${sizeStyles[size]} ${bgColor} ${className}`}
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.2 }}
        {...props}
      >
        {src ? (
          <img
            src={src}
            alt={name || "Avatar"}
            className="w-full h-full rounded-full object-cover"
          />
        ) : (
          <span>{getInitials(name)}</span>
        )}
      </motion.div>
    );
  }
);

Avatar.displayName = "Avatar";
