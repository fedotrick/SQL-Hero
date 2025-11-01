import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Map, AlertCircle } from "lucide-react";
import { ModuleCard } from "../components/modules/ModuleCard";
import { ModuleFilter, type FilterOption } from "../components/modules/ModuleFilter";
import { LoadingScreen } from "../components/LoadingScreen";
import { Card, CardContent } from "../components/ui";
import { coursesService } from "../services/courses";
import { useAuthStore } from "../store/authStore";
import type { ModuleListItem } from "../types/courses";
import { getModuleStatus } from "../types/courses";

export const ModulesMapPage = () => {
  const navigate = useNavigate();
  const { token } = useAuthStore();
  const [modules, setModules] = useState<ModuleListItem[]>([]);
  const [filteredModules, setFilteredModules] = useState<ModuleListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<FilterOption>("all");

  useEffect(() => {
    const loadModules = async () => {
      if (!token) {
        setError("Не авторизован");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        const response = await coursesService.getModules(token, 1, 100);
        setModules(response.items);
        setFilteredModules(response.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка загрузки модулей");
      } finally {
        setLoading(false);
      }
    };

    loadModules();
  }, [token]);

  useEffect(() => {
    const filterModules = () => {
      if (activeFilter === "all") {
        setFilteredModules(modules);
        return;
      }

      const filtered = modules.filter((module) => {
        const status = getModuleStatus(module);

        switch (activeFilter) {
          case "available":
            return !module.is_locked && status === "available";
          case "in-progress":
            return status === "in-progress";
          case "completed":
            return status === "completed";
          default:
            return true;
        }
      });

      setFilteredModules(filtered);
    };

    filterModules();
  }, [activeFilter, modules]);

  const handleModuleClick = (moduleId: number) => {
    navigate(`/modules/${moduleId}/lessons`);
  };

  const handleFilterChange = (filter: FilterOption) => {
    setActiveFilter(filter);
  };

  if (loading) {
    return <LoadingScreen />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20 px-4 pt-6">
        <Card variant="elevated" className="max-w-telegram mx-auto">
          <CardContent>
            <div className="text-center py-8">
              <AlertCircle className="mx-auto mb-4 text-telegram-destructive-text" size={48} />
              <h2 className="text-xl font-semibold text-telegram-text mb-2">Ошибка</h2>
              <p className="text-telegram-subtitle">{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <header className="text-center py-4">
          <Map className="mx-auto mb-3 text-telegram-button" size={48} />
          <h1 className="text-3xl font-bold text-telegram-text mb-2">Карта модулей</h1>
          <p className="text-telegram-subtitle">
            Пройдите все модули для завершения курса
          </p>
        </header>

        <div className="space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-telegram-text mb-3">Фильтр:</h2>
            <ModuleFilter activeFilter={activeFilter} onFilterChange={handleFilterChange} />
          </div>

          {filteredModules.length === 0 ? (
            <Card>
              <CardContent>
                <div className="text-center py-8">
                  <p className="text-telegram-subtitle">Модули не найдены</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredModules.map((module) => (
                <ModuleCard
                  key={module.id}
                  module={module}
                  onClick={handleModuleClick}
                  showTooltip
                />
              ))}
            </div>
          )}
        </div>

        <Card variant="outlined" className="mt-6">
          <CardContent>
            <div className="text-sm text-telegram-subtitle space-y-2">
              <h3 className="font-semibold text-telegram-text mb-2">Легенда:</h3>
              <div className="flex items-center gap-2">
                <span className="text-xl">🔒</span>
                <span>Модуль заблокирован</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl">➡️</span>
                <span>Модуль доступен</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl">🟡</span>
                <span>Модуль в процессе</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xl">✅</span>
                <span>Модуль завершен</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
