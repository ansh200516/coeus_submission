import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { CandidateDataService } from "@/lib/candidates/data-service"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Download, 
  FileText, 
  BarChart3, 
  PieChart, 
  TrendingUp,
  Calendar,
  Users,
  Award,
  Clock,
  Target
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default async function ReportsPage() {
  // Fetch candidate data for reports
  const candidateStats = await CandidateDataService.getDashboardStats()
  const candidates = await CandidateDataService.getAllCandidates()

  // Calculate report metrics
  const hireRate = (candidateStats.hire_recommendations / candidateStats.total_candidates) * 100
  const avgInterviewTime = candidates.reduce((sum, c) => 
    sum + c.candidate_scores.time_performance.time_used_min, 0
  ) / candidates.length

  const skillsDistribution = candidates.flatMap(c => 
    c.hirability_score?.category_breakdown.technical_skills.matches || []
  ).reduce((acc, skill) => {
    acc[skill] = (acc[skill] || 0) + 1
    return acc
  }, {} as Record<string, number>)

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
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
                    <p className="text-muted-foreground">
                      Generate and download comprehensive recruitment reports
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Calendar className="h-4 w-4 mr-2" />
                      Date Range
                    </Button>
                    <Button size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export All
                    </Button>
                  </div>
                </div>
              </div>

              {/* Report Categories */}
              <div className="px-6 lg:px-8">
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="performance">Performance</TabsTrigger>
                    <TabsTrigger value="skills">Skills Analysis</TabsTrigger>
                    <TabsTrigger value="custom">Custom Reports</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="overview" className="space-y-6">
                    {/* Key Metrics */}
                    <div className="grid grid-cols-1 gap-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
                      <Card>
                        <CardHeader className="pb-4">
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <Users className="h-5 w-5 text-blue-500" />
                            Total Candidates
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{candidateStats.total_candidates}</div>
                          <p className="text-sm text-muted-foreground">Interviewed this period</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-4">
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <Target className="h-5 w-5 text-green-500" />
                            Hire Rate
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{hireRate.toFixed(1)}%</div>
                          <p className="text-sm text-muted-foreground">Success rate</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-4">
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <Award className="h-5 w-5 text-yellow-500" />
                            Avg Score
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{candidateStats.average_score.toFixed(1)}</div>
                          <p className="text-sm text-muted-foreground">Overall performance</p>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader className="pb-4">
                          <CardTitle className="flex items-center gap-2 text-lg">
                            <Clock className="h-5 w-5 text-purple-500" />
                            Avg Time
                          </CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="text-3xl font-bold">{avgInterviewTime.toFixed(0)}min</div>
                          <p className="text-sm text-muted-foreground">Interview duration</p>
                        </CardContent>
                      </Card>
                    </div>

                    {/* Quick Reports */}
                    <div className="grid grid-cols-1 gap-6 @xl/main:grid-cols-2">
                      <Card>
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2">
                            <FileText className="h-5 w-5" />
                            Quick Reports
                          </CardTitle>
                          <CardDescription>
                            Generate common reports instantly
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-3">
                          <Button variant="outline" className="w-full justify-start">
                            <BarChart3 className="h-4 w-4 mr-2" />
                            Candidate Performance Summary
                          </Button>
                          <Button variant="outline" className="w-full justify-start">
                            <PieChart className="h-4 w-4 mr-2" />
                            Skills Distribution Report
                          </Button>
                          <Button variant="outline" className="w-full justify-start">
                            <TrendingUp className="h-4 w-4 mr-2" />
                            Hiring Trends Analysis
                          </Button>
                          <Button variant="outline" className="w-full justify-start">
                            <Users className="h-4 w-4 mr-2" />
                            Interview Completion Report
                          </Button>
                        </CardContent>
                      </Card>

                      <Card>
                        <CardHeader>
                          <CardTitle>Recent Activity</CardTitle>
                          <CardDescription>
                            Latest interview and candidate updates
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {candidates.slice(0, 5).map((candidate) => (
                              <div key={candidate.candidate_scores.candidate.user_id} className="flex items-center justify-between">
                                <div>
                                  <div className="font-medium">
                                    {candidate.static_knowledge.linkedin[0] || candidate.candidate_scores.candidate.name}
                                  </div>
                                  <div className="text-sm text-muted-foreground">
                                    {new Date(candidate.metadata.consolidation_timestamp).toLocaleDateString()}
                                  </div>
                                </div>
                                <Badge 
                                  variant={candidate.hirability_score?.recommendation === "Hire" ? "default" : "destructive"}
                                >
                                  {candidate.hirability_score?.recommendation || candidate.summary.hiring_recommendation_from_lda}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="performance" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Performance Analytics</CardTitle>
                        <CardDescription>
                          Detailed performance metrics and trends
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 gap-6 @xl/main:grid-cols-2">
                          <div>
                            <h4 className="font-medium mb-4">Score Distribution</h4>
                            <div className="space-y-3">
                              <div className="flex justify-between">
                                <span>Excellent (80-100)</span>
                                <span>{candidates.filter(c => (c.hirability_score?.overall_score || c.candidate_scores.scores.final) >= 80).length}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Good (60-79)</span>
                                <span>{candidates.filter(c => {
                                  const score = c.hirability_score?.overall_score || c.candidate_scores.scores.final;
                                  return score >= 60 && score < 80;
                                }).length}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Average (40-59)</span>
                                <span>{candidates.filter(c => {
                                  const score = c.hirability_score?.overall_score || c.candidate_scores.scores.final;
                                  return score >= 40 && score < 60;
                                }).length}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Below Average (0-39)</span>
                                <span>{candidates.filter(c => (c.hirability_score?.overall_score || c.candidate_scores.scores.final) < 40).length}</span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <h4 className="font-medium mb-4">Recommendation Breakdown</h4>
                            <div className="space-y-3">
                              <div className="flex justify-between">
                                <span className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                                  Hire
                                </span>
                                <span>{candidateStats.hire_recommendations}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="flex items-center gap-2">
                                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                                  No Hire
                                </span>
                                <span>{candidateStats.total_candidates - candidateStats.hire_recommendations}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                  
                  <TabsContent value="skills" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Skills Analysis</CardTitle>
                        <CardDescription>
                          Technical skills distribution across candidates
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <h4 className="font-medium">Most Common Skills</h4>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {Object.entries(skillsDistribution)
                              .sort(([,a], [,b]) => b - a)
                              .slice(0, 12)
                              .map(([skill, count]) => (
                                <div key={skill} className="flex items-center justify-between p-3 border rounded-lg">
                                  <span className="text-sm font-medium">{skill}</span>
                                  <Badge variant="secondary">{count}</Badge>
                                </div>
                              ))}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                  
                  <TabsContent value="custom" className="space-y-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Custom Report Builder</CardTitle>
                        <CardDescription>
                          Create custom reports with specific metrics and filters
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="text-center py-8">
                          <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                          <h3 className="text-lg font-medium">Custom Report Builder</h3>
                          <p className="text-muted-foreground mb-4">
                            Build custom reports with advanced filtering and metrics
                          </p>
                          <Button>
                            <BarChart3 className="h-4 w-4 mr-2" />
                            Create Custom Report
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
