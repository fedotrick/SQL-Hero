import { X, Trophy, CheckCircle, Lock } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import type { Achievement } from "../../types/achievements";
import { Card, CardContent, Badge, ProgressBar } from "../ui";

interface AchievementDetailModalProps {
  achievement: Achievement | null;
  onClose: () => void;
}

export const AchievementDetailModal = ({ achievement, onClose }: AchievementDetailModalProps) => {
  if (!achievement) return null;

  const getIconComponent = (iconName: string | null) => {
    if (!iconName) return <Trophy className="text-telegram-button" size={64} />;
    
    const iconMap: Record<string, React.ReactElement> = {
      trophy: <Trophy className="text-telegram-button" size={64} />,
      star: <Trophy className="text-yellow-500" size={64} />,
      award: <Trophy className="text-purple-500" size={64} />,
      target: <Trophy className="text-green-500" size={64} />,
    };
    
    return iconMap[iconName] || <Trophy className="text-telegram-button" size={64} />;
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-md"
        >
          <Card>
            <CardContent className="p-6">
              <div className="flex justify-end mb-2">
                <button
                  onClick={onClose}
                  className="p-1 rounded-full hover:bg-telegram-secondary-bg transition-colors"
                  aria-label="Close modal"
                >
                  <X className="text-telegram-subtitle" size={24} />
                </button>
              </div>

              <div className="text-center mb-6">
                <div className="flex justify-center mb-4">
                  {getIconComponent(achievement.icon)}
                </div>
                <h2 className="text-2xl font-bold text-telegram-text mb-2">
                  {achievement.title}
                </h2>
                {achievement.is_earned && (
                  <Badge variant="success" size="md" className="mb-2">
                    <CheckCircle size={16} className="mr-1" />
                    Открыто
                  </Badge>
                )}
                {!achievement.is_earned && (
                  <Badge variant="default" size="md" className="mb-2">
                    <Lock size={16} className="mr-1" />
                    Заблокировано
                  </Badge>
                )}
              </div>

              <div className="space-y-4">
                {achievement.description && (
                  <div>
                    <h3 className="text-sm font-semibold text-telegram-subtitle uppercase mb-1">
                      Описание
                    </h3>
                    <p className="text-telegram-text">{achievement.description}</p>
                  </div>
                )}

                {achievement.criteria && (
                  <div>
                    <h3 className="text-sm font-semibold text-telegram-subtitle uppercase mb-1">
                      Условие разблокировки
                    </h3>
                    <p className="text-telegram-text">{achievement.criteria}</p>
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-semibold text-telegram-subtitle uppercase mb-1">
                    Награда
                  </h3>
                  <p className="text-telegram-text">{achievement.points} очков</p>
                </div>

                {!achievement.is_earned && achievement.progress && (
                  <div>
                    <h3 className="text-sm font-semibold text-telegram-subtitle uppercase mb-2">
                      Прогресс
                    </h3>
                    <ProgressBar value={achievement.progress.percentage} size="md" />
                    <p className="text-sm text-telegram-subtitle text-center mt-2">
                      {achievement.progress.current} / {achievement.progress.target}
                    </p>
                  </div>
                )}

                {achievement.is_earned && achievement.earned_at && (
                  <div>
                    <h3 className="text-sm font-semibold text-telegram-subtitle uppercase mb-1">
                      Разблокировано
                    </h3>
                    <p className="text-telegram-text">
                      {new Date(achievement.earned_at).toLocaleDateString("ru-RU", {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
