import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router-dom";
import { queryClient } from "./utils/queryClient";
import { router } from "./routes";
import { TelegramAuthProvider } from "./components/TelegramAuthProvider";

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TelegramAuthProvider>
        <RouterProvider router={router} />
      </TelegramAuthProvider>
    </QueryClientProvider>
  );
}

export default App;
