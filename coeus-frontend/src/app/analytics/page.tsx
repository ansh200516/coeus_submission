import { AppSidebar } from "@/components/app-sidebar"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { CandidateStatsCards } from "@/components/candidates/candidate-stats-cards"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { CandidateDataService } from "@/lib/candidates/data-service"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, Users, Award, Clock, Target } from "lucide-react"

export default async function AnalyticsPage() {
  // Fetch candidate data for analytics
  const candidateStats = await CandidateDataService.getDashboardStats()
  const candidates = await CandidateDataService.getAllCandidates()

  // Calculate analytics metrics
  const avgTechnicalScore = candidates.reduce((sum, c) => 
    sum + (c.hirability_score?.category_breakdown.technical_skills.score || 0), 0
  ) / candidates.length

  const avgCommunicationScore = candidates.reduce((sum, c) => 
    sum + c.candidate_scores.scores.components.communication, 0
  ) / candidates.length

  const topSkills = candidates.flatMap(c => 
    c.hirability_score?.category_breakdown.technical_skills.matches || []
  ).reduce((acc, skill) => {
    acc[skill] = (acc[skill] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const topSkillsList = Object.entries(topSkills)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10)

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              {/* Page Header */}
              <div className="flex flex-col gap-4 px-6 lg:px-8">
                <div>
                  <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
                  <p className="text-muted-foreground">
                    Insights and performance metrics for candidate evaluation
                  </p>
                </div>
              </div>

              {/* Overview Stats */}
              <CandidateStatsCards stats={candidateStats} />

              {/* Analytics Charts and Metrics */}
              <div className="px-4 lg:px-6">
                <ChartAreaInteractive />
              </div>

              {/* Detailed Analytics Cards */}
              <div className="grid grid-cols-1 gap-6 px-6 lg:px-8 @xl/main:grid-cols-2">
                {/* Technical Skills Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Award className="h-5 w-5" />
                      Technical Skills Analysis
                    </CardTitle>
                    <CardDescription>
                      Average technical performance across all candidates
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Average Technical Score</span>
                        <span className="text-2xl font-bold text-primary">
                          {avgTechnicalScore.toFixed(1)}
                        </span>
                      </div>
                      <div className="space-y-2">
                        <h4 className="text-sm font-medium">Top Skills</h4>
                        <div className="flex flex-wrap gap-2">
                          {topSkillsList.slice(0, 6).map(([skill, count]) => (
                            <Badge key={skill} variant="secondary" className="text-xs">
                              {skill} ({count})
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Communication Analysis */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Users className="h-5 w-5" />
                      Communication Analysis
                    </CardTitle>
                    <CardDescription>
                      Communication skills assessment results
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Average Communication Score</span>
                        <span className="text-2xl font-bold text-primary">
                          {avgCommunicationScore.toFixed(1)}/10
                        </span>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Excellent (8-10)</span>
                          <span>{candidates.filter(c => c.candidate_scores.scores.components.communication >= 8).length}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Good (6-7)</span>
                          <span>{candidates.filter(c => c.candidate_scores.scores.components.communication >= 6 && c.candidate_scores.scores.components.communication < 8).length}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Needs Improvement (0-5)</span>
                          <span>{candidates.filter(c => c.candidate_scores.scores.components.communication < 6).length}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Hiring Trends */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5" />
                      Hiring Trends
                    </CardTitle>
                    <CardDescription>
                      Recruitment performance and trends
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-600">
                            {candidateStats.hire_recommendations}
                          </div>
                          <div className="text-sm text-muted-foreground">Hire Recommended</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-red-600">
                            {candidateStats.total_candidates - candidateStats.hire_recommendations}
                          </div>
                          <div className="text-sm text-muted-foreground">Not Recommended</div>
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold">
                          {((candidateStats.hire_recommendations / candidateStats.total_candidates) * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-muted-foreground">Success Rate</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Interview Performance */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Clock className="h-5 w-5" />
                      Interview Performance
                    </CardTitle>
                    <CardDescription>
                      Interview completion and timing metrics
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Completion Rate</span>
                        <span className="text-2xl font-bold text-primary">
                          {((candidateStats.completed_interviews / candidateStats.total_candidates) * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Completed Interviews</span>
                          <span>{candidateStats.completed_interviews}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Pending Reviews</span>
                          <span>{candidateStats.pending_reviews}</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
