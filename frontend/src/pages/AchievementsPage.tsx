import { Trophy, Star, Award, Target, Zap } from "lucide-react";
import { Card, CardContent, Badge, ProgressBar } from "../components/ui";

export const AchievementsPage = () => {
  const achievements = [
    {
      id: 1,
      title: "First Steps",
      description: "Complete your first lesson",
      icon: <Star className="text-yellow-500" size={32} />,
      unlocked: true,
      progress: 100,
    },
    {
      id: 2,
      title: "Week Warrior",
      description: "Complete 7 days in a row",
      icon: <Trophy className="text-blue-500" size={32} />,
      unlocked: true,
      progress: 100,
    },
    {
      id: 3,
      title: "Fast Learner",
      description: "Complete 10 lessons in one day",
      icon: <Zap className="text-purple-500" size={32} />,
      unlocked: false,
      progress: 60,
    },
    {
      id: 4,
      title: "Perfect Score",
      description: "Get 100% on any test",
      icon: <Target className="text-green-500" size={32} />,
      unlocked: true,
      progress: 100,
    },
    {
      id: 5,
      title: "Master",
      description: "Complete all available courses",
      icon: <Award className="text-red-500" size={32} />,
      unlocked: false,
      progress: 35,
    },
  ];

  const stats = {
    totalAchievements: achievements.length,
    unlocked: achievements.filter((a) => a.unlocked).length,
    totalPoints: 1250,
  };

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
              {stats.unlocked}/{stats.totalAchievements}
            </div>
            <div className="text-xs text-telegram-subtitle mt-1">Открыто</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="text-2xl font-bold text-telegram-button">{stats.totalPoints}</div>
            <div className="text-xs text-telegram-subtitle mt-1">Очков</div>
          </Card>
          <Card padding="sm" className="text-center">
            <div className="text-2xl font-bold text-telegram-button">
              {Math.round((stats.unlocked / stats.totalAchievements) * 100)}%
            </div>
            <div className="text-xs text-telegram-subtitle mt-1">Завершено</div>
          </Card>
        </div>

        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Все достижения</h2>
          <div className="space-y-3">
            {achievements.map((achievement) => (
              <Card
                key={achievement.id}
                variant="outlined"
                className={!achievement.unlocked ? "opacity-60" : ""}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">{achievement.icon}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <h3 className="font-semibold text-telegram-text">{achievement.title}</h3>
                        {achievement.unlocked && (
                          <Badge variant="success" size="sm">
                            Открыто
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-telegram-subtitle mb-3">{achievement.description}</p>
                      {!achievement.unlocked && (
                        <ProgressBar value={achievement.progress} size="sm" />
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};
