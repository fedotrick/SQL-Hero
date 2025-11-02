import { BookOpen } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../store/authStore";
import { telegramHaptics } from "../services/telegramHaptics";
import { telegramService } from "../services/telegram";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  Badge,
  ProgressBar,
} from "../components/ui";

export const HomePage = () => {
  const { user } = useAuthStore();

  const handleHapticClick = (
    type: "light" | "medium" | "heavy" | "success" | "error" | "warning"
  ) => {
    switch (type) {
      case "light":
        telegramHaptics.light();
        break;
      case "medium":
        telegramHaptics.medium();
        break;
      case "heavy":
        telegramHaptics.heavy();
        break;
      case "success":
        telegramHaptics.success();
        break;
      case "error":
        telegramHaptics.error();
        break;
      case "warning":
        telegramHaptics.warning();
        break;
    }
  };

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <header className="text-center py-6">
          <BookOpen className="mx-auto mb-3 text-telegram-button" size={48} />
          <h1 className="text-3xl font-bold text-telegram-text mb-2">Курс</h1>
          <p className="text-telegram-subtitle">Добро пожаловать в обучение</p>
        </header>

        {user && (
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Профиль пользователя</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-telegram-text">
                  {user.first_name} {user.last_name}
                  {user.username && (
                    <Badge className="ml-2" size="sm">
                      @{user.username}
                    </Badge>
                  )}
                </p>
                <p className="text-xs text-telegram-hint">Telegram ID: {user.telegram_id}</p>
              </div>
            </CardContent>
          </Card>
        )}

        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Текущий прогресс</h2>
          <Card>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-telegram-text">Модуль 1: Основы</span>
                    <Badge variant="success" size="sm">
                      Завершено
                    </Badge>
                  </div>
                  <ProgressBar value={100} variant="success" size="sm" />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-telegram-text">Модуль 2: Продвинутый</span>
                    <Badge variant="info" size="sm">
                      В процессе
                    </Badge>
                  </div>
                  <ProgressBar value={65} size="sm" showLabel />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-telegram-text">Модуль 3: Эксперт</span>
                    <Badge variant="default" size="sm">
                      Заблокировано
                    </Badge>
                  </div>
                  <ProgressBar value={0} size="sm" />
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-telegram-text mb-4">Быстрые действия</h2>
          <div className="grid grid-cols-2 gap-3">
            <Link to="/modules">
              <Button fullWidth>Карта модулей</Button>
            </Link>
            <Link to="/leaderboard">
              <Button variant="secondary" fullWidth>
                Рейтинг
              </Button>
            </Link>
            <Link to="/stats">
              <Button variant="secondary" fullWidth>
                Статистика
              </Button>
            </Link>
            <Link to="/profile">
              <Button variant="outline" fullWidth>
                Профиль
              </Button>
            </Link>
          </div>
        </section>

        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-telegram-text">UI Компоненты</h2>
            <Link to="/showcase">
              <Button size="sm" variant="outline">
                Посмотреть все
              </Button>
            </Link>
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Особенности</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="mr-2 text-telegram-accent-text">✓</span>
                  <span className="text-telegram-subtitle">Telegram Design Tokens</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-telegram-accent-text">✓</span>
                  <span className="text-telegram-subtitle">Framer Motion анимации</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-telegram-accent-text">✓</span>
                  <span className="text-telegram-subtitle">Адаптивные компоненты</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-telegram-accent-text">✓</span>
                  <span className="text-telegram-subtitle">Поддержка темной темы</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </section>

        <Card>
          <CardHeader>
            <CardTitle>Haptic Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-telegram-subtitle">
              Попробуйте тактильную обратную связь (работает только в Telegram)
            </p>
            <div className="space-y-3">
              <div>
                <p className="mb-2 text-sm font-semibold text-telegram-text">Тип вибрации:</p>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" variant="outline" onClick={() => handleHapticClick("light")}>
                    Light
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleHapticClick("medium")}>
                    Medium
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleHapticClick("heavy")}>
                    Heavy
                  </Button>
                </div>
              </div>
              <div>
                <p className="mb-2 text-sm font-semibold text-telegram-text">Уведомления:</p>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" onClick={() => handleHapticClick("success")}>
                    Success
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleHapticClick("error")}
                  >
                    Error
                  </Button>
                  <Button size="sm" onClick={() => handleHapticClick("warning")}>
                    Warning
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Telegram WebApp Info</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-telegram-hint">Platform:</span>
                <span className="text-telegram-text">{telegramService.getPlatform()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-telegram-hint">Version:</span>
                <span className="text-telegram-text">{telegramService.getVersion()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-telegram-hint">Color Scheme:</span>
                <span className="text-telegram-text">{telegramService.getColorScheme()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-telegram-hint">Available:</span>
                <span className="text-telegram-text">
                  {telegramService.isAvailable() ? "Yes" : "No"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-telegram-hint">Haptics Available:</span>
                <span className="text-telegram-text">
                  {telegramHaptics.isAvailable() ? "Yes" : "No"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
