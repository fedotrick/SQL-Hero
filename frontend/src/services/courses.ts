import type { ModuleListResponse, ModuleDetail, LessonDetail } from "../types/courses";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class CoursesError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "CoursesError";
    this.statusCode = statusCode;
  }
}

class CoursesService {
  private async makeRequest<T>(endpoint: string, token: string): Promise<T> {
    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: "Request failed",
        }));
        throw new CoursesError(
          errorData.detail || `Request failed with status ${response.status}`,
          response.status
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof CoursesError) {
        throw error;
      }
      if (error instanceof Error) {
        throw new CoursesError(`Network error: ${error.message}`);
      }
      throw new CoursesError("Unknown error");
    }
  }

  async getModules(token: string, page = 1, pageSize = 20): Promise<ModuleListResponse> {
    return this.makeRequest<ModuleListResponse>(
      `/courses/modules?page=${page}&page_size=${pageSize}`,
      token
    );
  }

  async getModuleDetail(token: string, moduleId: number): Promise<ModuleDetail> {
    return this.makeRequest<ModuleDetail>(`/courses/modules/${moduleId}`, token);
  }

  async getLessonDetail(token: string, lessonId: number): Promise<LessonDetail> {
    return this.makeRequest<LessonDetail>(`/courses/lessons/${lessonId}`, token);
  }
}

export const coursesService = new CoursesService();
