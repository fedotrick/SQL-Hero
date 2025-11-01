export interface LessonAttemptRequest {
  user_query: string;
  success: boolean;
}

export interface AchievementUnlocked {
  achievement_id: number;
  code: string;
  title: string;
  icon: string | null;
  points: number;
}

export interface LessonAttemptResponse {
  success: boolean;
  xp_earned: number;
  total_xp: number;
  level: number;
  level_up: boolean;
  current_streak: number;
  longest_streak: number;
  attempts: number;
  first_try: boolean;
  progress_status: string;
  message: string;
  achievements_unlocked: AchievementUnlocked[];
}
