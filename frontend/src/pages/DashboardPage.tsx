import { motion } from "framer-motion";
import { Flame, Trophy, Target, Zap, User } from "lucide-react";
import { useProgressSummary } from "../hooks/useProgressSummary";
import { useActivityHeatmap } from "../hooks/useActivityHeatmap";
import { Card, CardHeader, CardTitle, CardContent, Badge, ProgressBar, Skeleton } from "../components/ui";
import { ActivityHeatmap } from "../components/ActivityHeatmap";

const DashboardSkeleton = () => (
  <div className="space-y-6">
    <div className="h-48 rounded-xl overflow-hidden">
      <Skeleton height="100%" />
    </div>
    <div className="grid grid-cols-2 gap-3">
      <Skeleton height={100} />
      <Skeleton height={100} />
      <Skeleton height={100} />
      <Skeleton height={100} />
    </div>
    <Card>
      <CardContent>
        <Skeleton height={120} />
      </CardContent>
    </Card>
  </div>
);

const HeroHeader = ({ 
  level, 
  username, 
  xp, 
  progressPercentage, 
  xpToNextLevel 
}: { 
  level: number; 
  username: string | null; 
  xp: number;
  progressPercentage: number;
  xpToNextLevel: number;
}) => (
  <motion.div
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className="relative rounded-xl overflow-hidden mb-6"
  >
    <div className="absolute inset-0 bg-gradient-to-br from-telegram-button via-telegram-link to-telegram-accent-text opacity-90" />
    <div className="relative p-6 text-white">
      <div className="flex items-center gap-4 mb-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring" }}
          className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center border-4 border-white/30"
        >
          <User size={40} className="text-white" />
        </motion.div>
        <div className="flex-1">
          <motion.h1
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="text-2xl font-bold"
          >
            {username || "Learner"}
          </motion.h1>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="flex items-center gap-2 mt-1"
          >
            <Badge className="bg-white/20 text-white border-white/30">
              Level {level}
            </Badge>
            <span className="text-sm text-white/80">{xp} XP</span>
          </motion.div>
        </div>
      </div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <div className="flex justify-between text-sm mb-2">
          <span className="text-white/80">Level Progress</span>
          <span className="font-semibold">{xpToNextLevel} XP to next level</span>
        </div>
        <ProgressBar
          value={progressPercentage}
          variant="default"
          size="md"
          className="bg-white/20"
        />
      </motion.div>
    </div>
  </motion.div>
);

const StatCard = ({
  icon: Icon,
  label,
  value,
  subtitle,
  delay,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  subtitle?: string;
  delay: number;
}) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay, type: "spring" }}
  >
    <Card className="h-full">
      <CardContent className="flex flex-col items-center justify-center text-center p-4">
        <Icon className="text-telegram-button mb-2" size={24} />
        <div className="text-2xl font-bold text-telegram-text mb-1">{value}</div>
        <div className="text-xs text-telegram-hint">{label}</div>
        {subtitle && (
          <div className="text-xs text-telegram-subtitle mt-1">{subtitle}</div>
        )}
      </CardContent>
    </Card>
  </motion.div>
);

export const DashboardPage = () => {
  const { data: progress, isLoading: progressLoading, error: progressError } = useProgressSummary();
  const { data: heatmap, isLoading: heatmapLoading } = useActivityHeatmap();

  if (progressLoading) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20">
        <div className="max-w-telegram mx-auto p-4">
          <DashboardSkeleton />
        </div>
      </div>
    );
  }

  if (progressError) {
    return (
      <div className="min-h-screen bg-telegram-bg pb-20">
        <div className="max-w-telegram mx-auto p-4">
          <Card variant="elevated">
            <CardContent className="text-center py-8">
              <p className="text-telegram-destructive mb-2">Failed to load dashboard</p>
              <p className="text-sm text-telegram-hint">
                {progressError instanceof Error ? progressError.message : "Unknown error"}
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!progress) {
    return null;
  }

  return (
    <div className="min-h-screen bg-telegram-bg pb-20">
      <div className="max-w-telegram mx-auto p-4 space-y-6">
        <HeroHeader
          level={progress.level}
          username={progress.username}
          xp={progress.xp}
          progressPercentage={progress.progress_percentage}
          xpToNextLevel={progress.xp_to_next_level}
        />

        <section>
          <h2 className="text-lg font-semibold text-telegram-text mb-3">Quick Stats</h2>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              icon={Flame}
              label="Current Streak"
              value={progress.current_streak}
              subtitle={`Best: ${progress.longest_streak}`}
              delay={0.1}
            />
            <StatCard
              icon={Trophy}
              label="Achievements"
              value={progress.achievements_count}
              delay={0.2}
            />
            <StatCard
              icon={Target}
              label="Lessons Done"
              value={`${progress.lessons_completed}/${progress.total_lessons}`}
              delay={0.3}
            />
            <StatCard
              icon={Zap}
              label="Total Queries"
              value={progress.total_queries}
              delay={0.4}
            />
          </div>
        </section>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Module Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-telegram-text">Completed Modules</span>
                    <span className="text-telegram-hint">
                      {progress.modules_completed} / {progress.total_modules}
                    </span>
                  </div>
                  <ProgressBar
                    value={(progress.modules_completed / progress.total_modules) * 100}
                    showLabel
                    size="sm"
                  />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-telegram-text">Completed Lessons</span>
                    <span className="text-telegram-hint">
                      {progress.lessons_completed} / {progress.total_lessons}
                    </span>
                  </div>
                  <ProgressBar
                    value={(progress.lessons_completed / progress.total_lessons) * 100}
                    showLabel
                    size="sm"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Activity Heatmap</CardTitle>
            </CardHeader>
            <CardContent>
              {heatmapLoading ? (
                <Skeleton height={120} />
              ) : heatmap && heatmap.data.length > 0 ? (
                <>
                  <ActivityHeatmap data={heatmap.data} />
                  <div className="mt-4 text-sm text-telegram-hint">
                    Total activities: {heatmap.total_activities}
                  </div>
                </>
              ) : (
                <div className="text-center py-8 text-telegram-hint">
                  <p>No activity data yet</p>
                  <p className="text-xs mt-1">Start completing lessons to see your progress!</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.section>

        {progress.last_active_date && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-center text-sm text-telegram-hint"
          >
            Last active: {new Date(progress.last_active_date).toLocaleDateString()}
          </motion.div>
        )}
      </div>
    </div>
  );
};
