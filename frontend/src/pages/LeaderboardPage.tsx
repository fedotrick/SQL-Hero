import { useState, useEffect, useRef } from "react";
import { Trophy, Medal, Award, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/authStore";
import { leaderboardService } from "../services/leaderboard";
import { telegramHaptics } from "../services/telegramHaptics";
import type { LeaderboardResponse, LeaderboardEntry } from "../types/leaderboard";
import { Card, Avatar, Badge, Skeleton } from "../components/ui";

export const LeaderboardPage = () => {
  const { token, user } = useAuthStore();
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pullDistance, setPullDistance] = useState(0);
  const startY = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);

  const fetchLeaderboard = async (isRefresh = false) => {
    if (!token) return;

    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const response = await leaderboardService.getLeaderboard(token);
      setData(response);

      if (isRefresh) {
        telegramHaptics.success();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load leaderboard");
      if (isRefresh) {
        telegramHaptics.error();
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
      setPullDistance(0);
    }
  };

  useEffect(() => {
    if (token) {
      fetchLeaderboard();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  // Pull to refresh handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    if (containerRef.current && containerRef.current.scrollTop === 0) {
      startY.current = e.touches[0].clientY;
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (startY.current && containerRef.current && containerRef.current.scrollTop === 0) {
      const currentY = e.touches[0].clientY;
      const distance = currentY - startY.current;

      if (distance > 0) {
        setPullDistance(Math.min(distance, 100));
        if (distance > 50) {
          telegramHaptics.light();
        }
      }
    }
  };

  const handleTouchEnd = () => {
    if (pullDistance > 70 && !refreshing) {
      fetchLeaderboard(true);
    } else {
      setPullDistance(0);
    }
    startY.current = 0;
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Trophy className="text-yellow-500" size={20} />;
      case 2:
        return <Medal className="text-gray-400" size={20} />;
      case 3:
        return <Award className="text-orange-500" size={20} />;
      default:
        return null;
    }
  };

  const isCurrentUser = (entry: LeaderboardEntry) => {
    return user && entry.user_id === user.id;
  };

  const currentUserInTopList = data?.entries.some((entry) => isCurrentUser(entry));

  if (loading) {
    return <LeaderboardSkeleton />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20">
        <div className="max-w-telegram mx-auto p-4">
          <Card padding="lg">
            <div className="text-center py-8">
              <p className="text-telegram-destructive-text mb-4">{error}</p>
              <button
                onClick={() => fetchLeaderboard()}
                className="text-telegram-button hover:underline"
              >
                Try again
              </button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  if (!data || data.entries.length === 0) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20">
        <div className="max-w-telegram mx-auto p-4">
          <header className="text-center py-6">
            <Trophy className="mx-auto mb-3 text-telegram-button" size={48} />
            <h1 className="text-3xl font-bold text-telegram-text mb-2">Leaderboard</h1>
            <p className="text-telegram-subtitle">No users yet</p>
          </header>
          <Card padding="lg">
            <div className="text-center py-8 text-telegram-hint">
              <p>The leaderboard is empty.</p>
              <p className="mt-2">Complete lessons to appear on the leaderboard!</p>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-telegram-bg pb-32 overflow-y-auto"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      <div className="max-w-telegram mx-auto p-4">
        {/* Pull to refresh indicator */}
        <AnimatePresence>
          {pullDistance > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex justify-center mb-2"
            >
              <RefreshCw
                className={`text-telegram-button ${refreshing || pullDistance > 70 ? "animate-spin" : ""}`}
                size={24}
                style={{
                  transform: `rotate(${pullDistance * 3.6}deg)`,
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Header */}
        <header className="text-center py-6">
          <Trophy className="mx-auto mb-3 text-telegram-button" size={48} />
          <h1 className="text-3xl font-bold text-telegram-text mb-2">Leaderboard</h1>
          <p className="text-telegram-subtitle">{data.total_users} active learners</p>
        </header>

        {/* Top 3 Podium */}
        {data.entries.length >= 3 && (
          <div className="grid grid-cols-3 gap-2 mb-6">
            {/* 2nd Place */}
            <PodiumCard
              entry={data.entries[1]}
              rank={2}
              isCurrentUser={isCurrentUser(data.entries[1])}
            />
            {/* 1st Place */}
            <PodiumCard
              entry={data.entries[0]}
              rank={1}
              isCurrentUser={isCurrentUser(data.entries[0])}
            />
            {/* 3rd Place */}
            <PodiumCard
              entry={data.entries[2]}
              rank={3}
              isCurrentUser={isCurrentUser(data.entries[2])}
            />
          </div>
        )}

        {/* Leaderboard List */}
        <Card padding="none">
          <div className="divide-y divide-telegram-section-separator">
            {data.entries.map((entry) => (
              <LeaderboardItem
                key={entry.user_id}
                entry={entry}
                isCurrentUser={isCurrentUser(entry)}
                rankIcon={getRankIcon(entry.rank)}
              />
            ))}
          </div>
        </Card>
      </div>

      {/* Current User Fixed Position (if not in top list) */}
      {data.current_user && !currentUserInTopList && (
        <div className="fixed bottom-16 left-0 right-0 bg-telegram-bg border-t border-telegram-section-separator shadow-lg">
          <div className="max-w-telegram mx-auto px-4 py-2">
            <Card padding="sm" className="border-2 border-telegram-button">
              <LeaderboardItem
                entry={data.current_user}
                isCurrentUser={true}
                rankIcon={getRankIcon(data.current_user.rank)}
                compact
              />
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};

interface PodiumCardProps {
  entry: LeaderboardEntry;
  rank: number;
  isCurrentUser: boolean;
}

const PodiumCard = ({ entry, rank, isCurrentUser }: PodiumCardProps) => {
  const heights = {
    1: "h-32",
    2: "h-24",
    3: "h-20",
  };

  const getRankIcon = () => {
    switch (rank) {
      case 1:
        return <Trophy className="text-yellow-500" size={24} />;
      case 2:
        return <Medal className="text-gray-400" size={20} />;
      case 3:
        return <Award className="text-orange-500" size={20} />;
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: rank * 0.1 }}
      className={`flex flex-col items-center ${rank === 2 ? "order-1" : rank === 1 ? "order-2" : "order-3"}`}
    >
      <Avatar name={entry.first_name || entry.username} size="lg" rank={rank} />
      <p className="text-xs font-medium text-telegram-text mt-2 truncate w-full text-center">
        {entry.first_name || entry.username || "User"}
      </p>
      <Card
        padding="sm"
        className={`w-full mt-2 ${heights[rank as keyof typeof heights]} flex flex-col items-center justify-center ${
          isCurrentUser ? "border-2 border-telegram-button" : ""
        }`}
      >
        <div className="mb-1">{getRankIcon()}</div>
        <Badge size="sm" variant="info">
          {entry.xp} XP
        </Badge>
      </Card>
    </motion.div>
  );
};

interface LeaderboardItemProps {
  entry: LeaderboardEntry;
  isCurrentUser: boolean;
  rankIcon?: React.ReactNode;
  compact?: boolean;
}

const LeaderboardItem = ({
  entry,
  isCurrentUser,
  rankIcon,
  compact = false,
}: LeaderboardItemProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center gap-3 ${compact ? "p-2" : "p-4"} ${
        isCurrentUser ? "bg-telegram-button/10" : ""
      }`}
    >
      {/* Rank */}
      <div className="w-8 flex-shrink-0 text-center">
        {rankIcon || <span className="text-sm font-bold text-telegram-text">#{entry.rank}</span>}
      </div>

      {/* Avatar */}
      <Avatar name={entry.first_name || entry.username} size={compact ? "sm" : "md"} />

      {/* User Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className={`font-medium text-telegram-text truncate ${compact ? "text-sm" : ""}`}>
            {entry.first_name || entry.username || "User"}
          </p>
          {isCurrentUser && (
            <Badge size="sm" variant="info">
              You
            </Badge>
          )}
        </div>
        {!compact && (
          <div className="flex items-center gap-3 text-xs text-telegram-hint mt-1">
            <span>Level {entry.level}</span>
            <span>•</span>
            <span>{entry.lessons_completed} lessons</span>
            {entry.achievements_count > 0 && (
              <>
                <span>•</span>
                <span>{entry.achievements_count} achievements</span>
              </>
            )}
          </div>
        )}
      </div>

      {/* XP */}
      <div className="flex-shrink-0 text-right">
        <p className={`font-bold text-telegram-button ${compact ? "text-sm" : ""}`}>
          {entry.xp.toLocaleString()}
        </p>
        {!compact && <p className="text-xs text-telegram-hint">XP</p>}
      </div>
    </motion.div>
  );
};

const LeaderboardSkeleton = () => {
  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4">
        <header className="text-center py-6">
          <Skeleton width="48px" height="48px" circle className="mx-auto mb-3" />
          <Skeleton width="200px" height="32px" className="mx-auto mb-2" />
          <Skeleton width="150px" height="20px" className="mx-auto" />
        </header>

        {/* Podium Skeleton */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex flex-col items-center">
              <Skeleton width="48px" height="48px" circle />
              <Skeleton width="60px" height="16px" className="mt-2" />
              <Card padding="sm" className="w-full mt-2 h-24 flex items-center justify-center">
                <Skeleton width="40px" height="24px" />
              </Card>
            </div>
          ))}
        </div>

        {/* List Skeleton */}
        <Card padding="none">
          <div className="divide-y divide-telegram-section-separator">
            {[...Array(7)].map((_, i) => (
              <div key={i} className="flex items-center gap-3 p-4">
                <Skeleton width="32px" height="20px" />
                <Skeleton width="40px" height="40px" circle />
                <div className="flex-1">
                  <Skeleton width="120px" height="20px" className="mb-2" />
                  <Skeleton width="200px" height="16px" />
                </div>
                <div className="text-right">
                  <Skeleton width="60px" height="20px" className="mb-1" />
                  <Skeleton width="40px" height="16px" />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};
