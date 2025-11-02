import { createBrowserRouter } from "react-router-dom";
import { BaseLayout } from "../components/layout/BaseLayout";
import { DashboardPage } from "../pages/DashboardPage";
import { HomePage } from "../pages/HomePage";
import { AchievementsPage } from "../pages/AchievementsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { StatsPage } from "../pages/StatsPage";
import { ComponentShowcase } from "../pages/ComponentShowcase";
import { ModulesMapPage } from "../pages/ModulesMapPage";
import { LessonsListPage } from "../pages/LessonsListPage";
import { LessonPlayerPage } from "../pages/LessonPlayerPage";
import { LeaderboardPage } from "../pages/LeaderboardPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <BaseLayout>
        <DashboardPage />
      </BaseLayout>
    ),
  },
  {
    path: "/demo",
    element: (
      <BaseLayout>
        <HomePage />
      </BaseLayout>
    ),
  },
  {
    path: "/modules",
    element: (
      <BaseLayout>
        <ModulesMapPage />
      </BaseLayout>
    ),
  },
  {
    path: "/modules/:moduleId/lessons",
    element: (
      <BaseLayout>
        <LessonsListPage />
      </BaseLayout>
    ),
  },
  {
    path: "/lessons/:lessonId",
    element: (
      <BaseLayout>
        <LessonPlayerPage />
      </BaseLayout>
    ),
  },
  {
    path: "/achievements",
    element: (
      <BaseLayout>
        <AchievementsPage />
      </BaseLayout>
    ),
  },
  {
    path: "/leaderboard",
    element: (
      <BaseLayout>
        <LeaderboardPage />
      </BaseLayout>
    ),
  },
  {
    path: "/profile",
    element: (
      <BaseLayout>
        <ProfilePage />
      </BaseLayout>
    ),
  },
  {
    path: "/stats",
    element: (
      <BaseLayout>
        <StatsPage />
      </BaseLayout>
    ),
  },
  {
    path: "/showcase",
    element: (
      <BaseLayout>
        <ComponentShowcase />
      </BaseLayout>
    ),
  },
]);
