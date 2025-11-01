export interface ModuleListItem {
  id: number;
  title: string;
  description: string | null;
  order: number;
  is_published: boolean;
  is_locked: boolean;
  lessons_count: number;
  completed_lessons_count: number;
}

export interface ModuleListResponse {
  items: ModuleListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LessonSummary {
  id: number;
  title: string;
  order: number;
  estimated_duration: number | null;
  is_published: boolean;
  is_locked: boolean;
  progress_status: string | null;
}

export interface ModuleDetail {
  id: number;
  title: string;
  description: string | null;
  order: number;
  is_published: boolean;
  is_locked: boolean;
  lessons: LessonSummary[];
  created_at: string;
  updated_at: string;
}

export interface LessonDetail {
  id: number;
  module_id: number;
  title: string;
  content: string | null;
  theory: string | null;
  sql_solution: string | null;
  expected_result: Record<string, any> | null;
  order: number;
  estimated_duration: number | null;
  is_published: boolean;
  is_locked: boolean;
  progress_status: string | null;
  attempts: number;
  created_at: string;
  updated_at: string;
}

export type ModuleStatus = "locked" | "available" | "in-progress" | "completed";

export const getModuleStatus = (module: ModuleListItem): ModuleStatus => {
  if (module.is_locked) return "locked";
  if (module.completed_lessons_count === module.lessons_count && module.lessons_count > 0) {
    return "completed";
  }
  if (module.completed_lessons_count > 0) return "in-progress";
  return "available";
};

export const getStatusIcon = (status: ModuleStatus): string => {
  switch (status) {
    case "locked":
      return "🔒";
    case "available":
      return "➡️";
    case "in-progress":
      return "🟡";
    case "completed":
      return "✅";
  }
};
