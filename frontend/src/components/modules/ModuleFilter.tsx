import { Button } from "../ui";

export type FilterOption = "all" | "available" | "in-progress" | "completed";

interface ModuleFilterProps {
  activeFilter: FilterOption;
  onFilterChange: (filter: FilterOption) => void;
}

export const ModuleFilter = ({ activeFilter, onFilterChange }: ModuleFilterProps) => {
  const filters: { value: FilterOption; label: string }[] = [
    { value: "all", label: "Все" },
    { value: "available", label: "Доступные" },
    { value: "in-progress", label: "В процессе" },
    { value: "completed", label: "Завершенные" },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {filters.map((filter) => (
        <Button
          key={filter.value}
          size="sm"
          variant={activeFilter === filter.value ? "primary" : "outline"}
          onClick={() => onFilterChange(filter.value)}
        >
          {filter.label}
        </Button>
      ))}
    </div>
  );
};
