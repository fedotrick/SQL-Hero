export interface LeaderboardEntry {
  user_id: number;
  username: string | null;
  first_name: string | null;
  rank: number;
  xp: number;
  level: number;
  lessons_completed: number;
  achievements_count: number;
}

export interface LeaderboardResponse {
  entries: LeaderboardEntry[];
  current_user: LeaderboardEntry | null;
  last_updated: string | null;
  total_users: number;
}
