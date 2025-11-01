import { createBrowserRouter } from "react-router-dom";
import { BaseLayout } from "../components/layout/BaseLayout";
import { HomePage } from "../pages/HomePage";
import { AchievementsPage } from "../pages/AchievementsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ComponentShowcase } from "../pages/ComponentShowcase";
import { ModulesMapPage } from "../pages/ModulesMapPage";
import { LessonsListPage } from "../pages/LessonsListPage";

export const router = createBrowserRouter([
  {
    path: "/",
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
    path: "/achievements",
    element: (
      <BaseLayout>
        <AchievementsPage />
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
    path: "/showcase",
    element: (
      <BaseLayout>
        <ComponentShowcase />
      </BaseLayout>
    ),
  },
]);
