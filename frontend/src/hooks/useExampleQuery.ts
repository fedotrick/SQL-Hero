import { useQuery } from "@tanstack/react-query";

interface ExampleData {
  message: string;
}

const fetchExample = async (): Promise<ExampleData> => {
  const response = await fetch("http://localhost:8000/");
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response.json();
};

export const useExampleQuery = () => {
  return useQuery({
    queryKey: ["example"],
    queryFn: fetchExample,
    enabled: false, // Disabled by default, enable when backend is ready
  });
};
