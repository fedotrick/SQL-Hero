export interface AchievementProgress {
  current: number;
  target: number;
  percentage: number;
}

export interface Achievement {
  id: number;
  code: string;
  type: string;
  title: string;
  description: string | null;
  icon: string | null;
  points: number;
  criteria: string | null;
  created_at: string;
  is_earned: boolean;
  earned_at: string | null;
  progress: AchievementProgress | null;
}

export interface AchievementsListResponse {
  achievements: Achievement[];
  total_earned: number;
  total_points: number;
}

export interface AchievementUnlocked {
  achievement_id: number;
  achievement_code: string;
  title: string;
  description: string | null;
  icon: string | null;
  points: number;
}
