import { createBrowserRouter } from "react-router-dom";
import { BaseLayout } from "../components/layout/BaseLayout";
import { HomePage } from "../pages/HomePage";
import { AchievementsPage } from "../pages/AchievementsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ComponentShowcase } from "../pages/ComponentShowcase";

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
