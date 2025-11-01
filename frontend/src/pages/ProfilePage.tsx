import { User, Settings, LogOut, BookOpen, Trophy, Clock } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent, Badge, CircularProgress } from "../components/ui";

export const ProfilePage = () => {
  const userProfile = {
    name: "Иван Иванов",
    username: "@ivanov",
    level: 5,
    xp: 2750,
    xpToNextLevel: 3000,
    streak: 12,
    totalLessons: 45,
    completedLessons: 38,
    hoursLearned: 24,
    achievements: 8,
  };

  const xpProgress = (userProfile.xp / userProfile.xpToNextLevel) * 100;

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <Card variant="elevated">
          <CardContent className="p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-20 h-20 rounded-full bg-telegram-button flex items-center justify-center text-telegram-button-text">
                <User size={40} />
              </div>
              <div className="flex-1">
                <h1 className="text-2xl font-bold text-telegram-text">{userProfile.name}</h1>
                <p className="text-telegram-subtitle">{userProfile.username}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="info" size="sm">
                    Уровень {userProfile.level}
                  </Badge>
                  <Badge variant="success" size="sm" dot>
                    {userProfile.streak} дней подряд
                  </Badge>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-telegram-text">Опыт до уровня {userProfile.level + 1}</span>
                <span className="text-telegram-subtitle">
                  {userProfile.xp} / {userProfile.xpToNextLevel} XP
                </span>
              </div>
              <div className="relative">
                <div className="h-3 bg-telegram-secondary-bg rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                    style={{ width: `${xpProgress}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Статистика</h2>
          <div className="grid grid-cols-2 gap-3">
            <Card>
              <CardContent className="p-4 text-center">
                <BookOpen className="mx-auto mb-2 text-telegram-button" size={32} />
                <div className="text-2xl font-bold text-telegram-text">
                  {userProfile.completedLessons}/{userProfile.totalLessons}
                </div>
                <div className="text-sm text-telegram-subtitle mt-1">Уроков пройдено</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <Trophy className="mx-auto mb-2 text-telegram-button" size={32} />
                <div className="text-2xl font-bold text-telegram-text">{userProfile.achievements}</div>
                <div className="text-sm text-telegram-subtitle mt-1">Достижений</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <Clock className="mx-auto mb-2 text-telegram-button" size={32} />
                <div className="text-2xl font-bold text-telegram-text">{userProfile.hoursLearned}</div>
                <div className="text-sm text-telegram-subtitle mt-1">Часов обучения</div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <div className="flex justify-center mb-2">
                  <CircularProgress
                    value={(userProfile.completedLessons / userProfile.totalLessons) * 100}
                    size={48}
                    strokeWidth={4}
                    showLabel={false}
                  />
                </div>
                <div className="text-2xl font-bold text-telegram-text">
                  {Math.round((userProfile.completedLessons / userProfile.totalLessons) * 100)}%
                </div>
                <div className="text-sm text-telegram-subtitle mt-1">Прогресс курса</div>
              </CardContent>
            </Card>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Настройки</h2>
          <div className="space-y-3">
            <Card interactive>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Settings className="text-telegram-button" size={24} />
                  <div className="flex-1">
                    <div className="font-medium text-telegram-text">Настройки профиля</div>
                    <div className="text-sm text-telegram-subtitle">Изменить личные данные</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card interactive>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <LogOut className="text-telegram-destructive" size={24} />
                  <div className="flex-1">
                    <div className="font-medium text-telegram-destructive">Выйти</div>
                    <div className="text-sm text-telegram-subtitle">Выйти из учетной записи</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <Card>
          <CardHeader>
            <CardTitle>О приложении</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-telegram-subtitle">
              <div className="flex justify-between">
                <span>Версия</span>
                <span className="text-telegram-text">1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span>Сборка</span>
                <span className="text-telegram-text">2024.01</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
