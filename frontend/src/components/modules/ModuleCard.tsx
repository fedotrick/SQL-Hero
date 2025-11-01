import { motion } from "framer-motion";
import { Lock } from "lucide-react";
import { Card, CardContent, ProgressBar } from "../ui";
import type { ModuleListItem } from "../../types/courses";
import { getModuleStatus, getStatusIcon } from "../../types/courses";
import { telegramHaptics } from "../../services/telegramHaptics";

interface ModuleCardProps {
  module: ModuleListItem;
  onClick?: (moduleId: number) => void;
  showTooltip?: boolean;
}

export const ModuleCard = ({ module, onClick, showTooltip = false }: ModuleCardProps) => {
  const status = getModuleStatus(module);
  const statusIcon = getStatusIcon(status);
  const progress =
    module.lessons_count > 0
      ? Math.round((module.completed_lessons_count / module.lessons_count) * 100)
      : 0;

  const handleClick = () => {
    if (module.is_locked) {
      telegramHaptics.error();
      return;
    }
    telegramHaptics.light();
    onClick?.(module.id);
  };

  const isInteractive = !module.is_locked;

  return (
    <motion.div
      whileHover={isInteractive ? { scale: 1.02 } : undefined}
      whileTap={isInteractive ? { scale: 0.98 } : undefined}
      transition={{ duration: 0.2 }}
      className="relative"
    >
      <Card
        interactive={isInteractive}
        className={`${module.is_locked ? "opacity-60" : ""}`}
        onClick={handleClick}
        padding="md"
      >
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-2xl" role="img" aria-label={status}>
                    {statusIcon}
                  </span>
                  <h3 className="text-lg font-semibold text-telegram-text truncate">
                    {module.title}
                  </h3>
                </div>
                {module.description && (
                  <p className="text-sm text-telegram-subtitle line-clamp-2 mt-1">
                    {module.description}
                  </p>
                )}
              </div>
              {module.is_locked && (
                <Lock size={20} className="text-telegram-hint ml-2 flex-shrink-0" />
              )}
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-telegram-hint">
                  Уроков: {module.completed_lessons_count}/{module.lessons_count}
                </span>
                <span className="text-telegram-hint">{progress}%</span>
              </div>
              <ProgressBar
                value={progress}
                variant={status === "completed" ? "success" : "default"}
                size="sm"
              />
            </div>

            {module.is_locked && showTooltip && (
              <div className="text-xs text-telegram-hint bg-telegram-bg/50 rounded p-2">
                🔒 Завершите предыдущий модуль, чтобы разблокировать
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};
