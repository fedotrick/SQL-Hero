import { useState } from "react";
import { Trophy } from "lucide-react";
import { Card, CardContent, Badge, ProgressBar } from "../components/ui";
import {
  AchievementDetailModal,
  AchievementUnlockAnimation,
} from "../components/achievements";
import { useAchievements } from "../hooks/useAchievements";
import { useAuthStore } from "../store/authStore";
import type { Achievement } from "../types/achievements";
import { LoadingScreen } from "../components/LoadingScreen";
import { ErrorScreen } from "../components/ErrorScreen";

export const AchievementsPage = () => {
  const { token } = useAuthStore();
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null);
  const [animatingAchievement, setAnimatingAchievement] = useState<number | null>(null);

  const {
    achievements,
    totalEarned,
    totalPoints,
    isLoading,
    error,
    newlyUnlocked,
    dismissNewAchievement,
  } = useAchievements({
    token,
    pollingInterval: 10000,
    onNewAchievement: (achievement) => {
      setAnimatingAchievement(achievement.achievement_id);
    },
  });

  const getIconComponent = (iconName: string | null) => {
    if (!iconName) return <Trophy className="text-telegram-button" size={32} />;

    const iconMap: Record<string, React.ReactElement> = {
      trophy: <Trophy className="text-telegram-button" size={32} />,
      star: <Trophy className="text-yellow-500" size={32} />,
      award: <Trophy className="text-purple-500" size={32} />,
      target: <Trophy className="text-green-500" size={32} />,
    };

    return iconMap[iconName] || <Trophy className="text-telegram-button" size={32} />;
  };

  const handleAchievementClick = (achievement: Achievement) => {
    setSelectedAchievement(achievement);
  };

  const handleCloseModal = () => {
    setSelectedAchievement(null);
  };

  const handleAnimationComplete = () => {
    if (animatingAchievement !== null) {
      dismissNewAchievement(animatingAchievement);
      setAnimatingAchievement(null);
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (error) {
    return <ErrorScreen error="Не удалось загрузить достижения" />;
  }

  const completionPercentage =
    achievements.length > 0 ? Math.round((totalEarned / achievements.length) * 100) : 0;

  const currentAnimatingAchievement = newlyUnlocked.find(
    (a) => a.achievement_id === animatingAchievement
  );

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <header className="text-center py-6">
          <Trophy className="mx-auto mb-3 text-telegram-button" size={48} />
          <h1 className="text-3xl font-bold text-telegram-text mb-2">Достижения</h1>
          <p className="text-telegram-subtitle">Ваши награды и прогресс</p>
        </header>

        <div className="grid grid-cols-3 gap-3">
          <Card padding="sm" className="text-center">
            <div className="text-2xl font-bold text-telegram-button">
              {totalEarned}/{achievements.length}
            </div>
            <div className="text-xs text-telegram-subtitle mt-1">Открыто</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="text-2xl font-bold text-telegram-button">{totalPoints}</div>
            <div className="text-xs text-telegram-subtitle mt-1">Очков</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="text-2xl font-bold text-telegram-button">{completionPercentage}%</div>
            <div className="text-xs text-telegram-subtitle mt-1">Завершено</div>
          </Card>
        </div>

        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Все достижения</h2>
          {achievements.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Trophy className="mx-auto mb-3 text-telegram-subtitle" size={48} />
                <p className="text-telegram-subtitle">Достижения пока не доступны</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {achievements.map((achievement) => (
                <Card
                  key={achievement.id}
                  variant="outlined"
                  className={`cursor-pointer transition-transform hover:scale-[1.02] ${
                    !achievement.is_earned ? "opacity-60" : ""
                  }`}
                  onClick={() => handleAchievementClick(achievement)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">{getIconComponent(achievement.icon)}</div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <h3 className="font-semibold text-telegram-text">
                            {achievement.title}
                          </h3>
                          {achievement.is_earned && (
                            <Badge variant="success" size="sm">
                              Открыто
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-telegram-subtitle mb-2">
                          {achievement.description}
                        </p>
                        <div className="text-xs text-telegram-button font-semibold mb-3">
                          {achievement.points} очков
                        </div>
                        {!achievement.is_earned && achievement.progress && (
                          <div>
                            <ProgressBar value={achievement.progress.percentage} size="sm" />
                            <p className="text-xs text-telegram-subtitle text-right mt-1">
                              {achievement.progress.current} / {achievement.progress.target}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>

      <AchievementDetailModal achievement={selectedAchievement} onClose={handleCloseModal} />

      {currentAnimatingAchievement && (
        <AchievementUnlockAnimation
          achievement={currentAnimatingAchievement}
          onComplete={handleAnimationComplete}
        />
      )}
    </div>
  );
};
