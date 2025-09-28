import { TrendingDown, TrendingUp, Users, UserCheck, Clock, BarChart3 } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { CandidateDashboardStats } from "@/lib/candidates/types"

interface CandidateStatsCardsProps {
  stats: CandidateDashboardStats;
}

export function CandidateStatsCards({ stats }: CandidateStatsCardsProps) {
  const hireRate = stats.total_candidates > 0 ? (stats.hire_recommendations / stats.total_candidates) * 100 : 0;
  const completionRate = stats.total_candidates > 0 ? (stats.completed_interviews / stats.total_candidates) * 100 : 0;

  return (
    <div className="grid grid-cols-1 gap-6 px-6 lg:px-8 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm flex items-center gap-2">
            <Users className="h-4 w-4" />
            Total Candidates
          </CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            {stats.total_candidates}
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className="bg-blue-500/10 border-blue-500/20 text-blue-400">
              <TrendingUp className="h-3 w-3 mr-1" />
              Active Pipeline
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            Growing candidate pool <TrendingUp className="size-4 text-blue-400" />
          </div>
          <div className="text-muted-foreground">
            Interviews completed: {stats.completed_interviews}
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm flex items-center gap-2">
            <UserCheck className="h-4 w-4" />
            Hire Recommendations
          </CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            {stats.hire_recommendations}
          </CardTitle>
          <CardAction>
            <Badge 
              variant="outline" 
              className={hireRate >= 30 
                ? "bg-green-500/10 border-green-500/20 text-green-400" 
                : "bg-red-500/10 border-red-500/20 text-red-400"
              }
            >
              {hireRate >= 30 ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              {hireRate.toFixed(1)}%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            {hireRate >= 30 ? "Strong hire rate" : "Hire rate needs improvement"} 
            {hireRate >= 30 ? (
              <TrendingUp className="size-4 text-green-400" />
            ) : (
              <TrendingDown className="size-4 text-red-400" />
            )}
          </div>
          <div className="text-muted-foreground">
            Quality candidates in pipeline
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Average Score
          </CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            {stats.average_score.toFixed(1)}
          </CardTitle>
          <CardAction>
            <Badge 
              variant="outline" 
              className={stats.average_score >= 60 
                ? "bg-green-500/10 border-green-500/20 text-green-400" 
                : stats.average_score >= 40
                ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-400"
                : "bg-red-500/10 border-red-500/20 text-red-400"
              }
            >
              {stats.average_score >= 60 ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              {stats.average_score >= 60 ? "High" : stats.average_score >= 40 ? "Medium" : "Low"}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            {stats.average_score >= 60 ? "Excellent performance" : "Room for improvement"}
            {stats.average_score >= 60 ? (
              <TrendingUp className="size-4 text-green-400" />
            ) : (
              <TrendingDown className="size-4 text-red-400" />
            )}
          </div>
          <div className="text-muted-foreground">
            Across all assessment areas
          </div>
        </CardFooter>
      </Card>

      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Completion Rate
          </CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            {completionRate.toFixed(0)}%
          </CardTitle>
          <CardAction>
            <Badge 
              variant="outline" 
              className={completionRate >= 90 
                ? "bg-green-500/10 border-green-500/20 text-green-400" 
                : "bg-yellow-500/10 border-yellow-500/20 text-yellow-400"
              }
            >
              {completionRate >= 90 ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <Clock className="h-3 w-3 mr-1" />
              )}
              {completionRate >= 90 ? "Excellent" : "In Progress"}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            {completionRate >= 90 ? "High completion rate" : "Interviews in progress"}
            <Clock className="size-4 text-blue-400" />
          </div>
          <div className="text-muted-foreground">
            {stats.pending_reviews > 0 ? `${stats.pending_reviews} pending reviews` : "All interviews completed"}
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
