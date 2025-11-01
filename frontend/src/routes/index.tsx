import { createBrowserRouter } from "react-router-dom";
import { BaseLayout } from "../components/layout/BaseLayout";
import { HomePage } from "../pages/HomePage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <BaseLayout>
        <HomePage />
      </BaseLayout>
    ),
  },
]);
