import { Trophy, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { AchievementUnlocked } from "../../types/achievements";
import { Card, CardContent } from "../ui";

interface AchievementUnlockAnimationProps {
  achievement: AchievementUnlocked | null;
  onComplete: () => void;
}

export const AchievementUnlockAnimation = ({
  achievement,
  onComplete,
}: AchievementUnlockAnimationProps) => {
  if (!achievement) return null;

  const getIconComponent = (iconName: string | null) => {
    if (!iconName) return <Trophy className="text-yellow-500" size={64} />;

    const iconMap: Record<string, React.ReactElement> = {
      trophy: <Trophy className="text-yellow-500" size={64} />,
      star: <Trophy className="text-yellow-400" size={64} />,
      award: <Trophy className="text-purple-500" size={64} />,
      target: <Trophy className="text-green-500" size={64} />,
    };

    return iconMap[iconName] || <Trophy className="text-yellow-500" size={64} />;
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70">
        <motion.div
          initial={{ opacity: 0, scale: 0.3, rotate: -180 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: -50 }}
          transition={{
            type: "spring",
            stiffness: 200,
            damping: 15,
            duration: 0.6,
          }}
          className="relative"
          onAnimationComplete={() => {
            setTimeout(() => {
              onComplete();
            }, 2500);
          }}
        >
          {/* Sparkles animation */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 1, repeat: 2, repeatDelay: 0.5 }}
          >
            <Sparkles className="text-yellow-300 absolute -top-8 -left-8" size={32} />
            <Sparkles className="text-yellow-300 absolute -top-8 -right-8" size={32} />
            <Sparkles className="text-yellow-300 absolute -bottom-8 -left-8" size={32} />
            <Sparkles className="text-yellow-300 absolute -bottom-8 -right-8" size={32} />
          </motion.div>

          {/* Ripple effect */}
          <motion.div
            className="absolute inset-0 rounded-full border-4 border-yellow-400"
            initial={{ scale: 1, opacity: 1 }}
            animate={{ scale: 2.5, opacity: 0 }}
            transition={{ duration: 1, repeat: 2, repeatDelay: 0.5 }}
          />

          <Card className="relative z-10 w-full max-w-sm">
            <CardContent className="p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.2, 1] }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <div className="flex justify-center mb-4">
                  {getIconComponent(achievement.icon)}
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.4 }}
              >
                <div className="mb-2">
                  <span className="text-sm font-semibold text-yellow-500 uppercase tracking-wide">
                    Достижение разблокировано!
                  </span>
                </div>
                <h2 className="text-2xl font-bold text-telegram-text mb-2">
                  {achievement.title}
                </h2>
                {achievement.description && (
                  <p className="text-telegram-subtitle mb-4">{achievement.description}</p>
                )}
                <div className="inline-block px-4 py-2 bg-yellow-500/20 rounded-full">
                  <span className="text-yellow-500 font-semibold">
                    +{achievement.points} очков
                  </span>
                </div>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
