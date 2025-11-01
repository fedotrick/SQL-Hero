import { motion } from "framer-motion";
import { BookOpen, Trophy, User } from "lucide-react";
import { NavLink } from "react-router-dom";

export interface NavigationItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

export interface BottomNavigationProps {
  className?: string;
}

const navigationItems: NavigationItem[] = [
  {
    path: "/",
    label: "Курс",
    icon: <BookOpen size={24} />,
  },
  {
    path: "/achievements",
    label: "Достижения",
    icon: <Trophy size={24} />,
  },
  {
    path: "/profile",
    label: "Профиль",
    icon: <User size={24} />,
  },
];

export const BottomNavigation = ({ className = "" }: BottomNavigationProps) => {
  return (
    <nav
      className={`fixed bottom-0 left-0 right-0 bg-telegram-section-bg border-t border-telegram-section-separator safe-area-bottom ${className}`}
    >
      <div className="max-w-telegram mx-auto flex items-center justify-around h-16">
        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors ${
                isActive ? "text-telegram-button" : "text-telegram-hint"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <motion.div
                  className="relative"
                  animate={{
                    scale: isActive ? 1.1 : 1,
                  }}
                  transition={{ duration: 0.2 }}
                >
                  {item.icon}
                  {isActive && (
                    <motion.div
                      className="absolute -bottom-1 left-1/2 w-1 h-1 bg-telegram-button rounded-full"
                      layoutId="activeIndicator"
                      style={{ x: "-50%" }}
                      transition={{
                        type: "spring",
                        stiffness: 380,
                        damping: 30,
                      }}
                    />
                  )}
                </motion.div>
                <span className="text-xs font-medium">{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};
