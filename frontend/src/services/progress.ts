import type { LessonAttemptRequest, LessonAttemptResponse } from "../types/progress";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ProgressError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "ProgressError";
    this.statusCode = statusCode;
  }
}

class ProgressService {
  async submitLessonAttempt(
    token: string,
    lessonId: number,
    attemptData: LessonAttemptRequest
  ): Promise<LessonAttemptResponse> {
    try {
      const response = await fetch(`${API_URL}/progress/lessons/${lessonId}/attempt`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(attemptData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          detail: "Request failed",
        }));
        throw new ProgressError(
          errorData.detail || `Request failed with status ${response.status}`,
          response.status
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof ProgressError) {
        throw error;
      }
      if (error instanceof Error) {
        throw new ProgressError(`Network error: ${error.message}`);
      }
      throw new ProgressError("Unknown error");
    }
  }
}

export const progressService = new ProgressService();
