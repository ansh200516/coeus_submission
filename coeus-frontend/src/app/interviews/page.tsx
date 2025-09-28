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
  Calendar, 
  Clock, 
  User, 
  MessageSquare, 
  Code, 
  Brain,
  Plus,
  Filter,
  Search,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default async function InterviewsPage() {
  // Fetch candidate data for interviews
  const candidates = await CandidateDataService.getAllCandidates()
  
  // Categorize interviews
  const completedInterviews = candidates.filter(c => c.metadata.sources.lda_interview && c.metadata.sources.code_interview)
  const activeInterviews = candidates.filter(c => c.metadata.sources.lda_interview || c.metadata.sources.code_interview)
  const scheduledInterviews: any[] = [] // Would come from a scheduling system

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
                    <h1 className="text-3xl font-bold tracking-tight">Interview Management</h1>
                    <p className="text-muted-foreground">
                      Schedule, conduct, and review candidate interviews
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Filter className="h-4 w-4 mr-2" />
                      Filter
                    </Button>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Schedule Interview
                    </Button>
                  </div>
                </div>
                
                {/* Search Bar */}
                <div className="flex items-center gap-4">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search interviews by candidate or interviewer..."
                      className="pl-10"
                    />
                  </div>
                </div>
              </div>

              {/* Interview Stats */}
              <div className="grid grid-cols-1 gap-6 px-6 lg:px-8 @xl/main:grid-cols-3">
                <Card>
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Completed
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{completedInterviews.length}</div>
                    <p className="text-sm text-muted-foreground">Interviews completed</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Clock className="h-5 w-5 text-yellow-500" />
                      In Progress
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{activeInterviews.length - completedInterviews.length}</div>
                    <p className="text-sm text-muted-foreground">Active interviews</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="pb-4">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Calendar className="h-5 w-5 text-blue-500" />
                      Scheduled
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold">{scheduledInterviews.length}</div>
                    <p className="text-sm text-muted-foreground">Upcoming interviews</p>
                  </CardContent>
                </Card>
              </div>

              {/* Interview Tabs */}
              <div className="px-6 lg:px-8">
                <Tabs defaultValue="completed" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="completed">Completed</TabsTrigger>
                    <TabsTrigger value="active">In Progress</TabsTrigger>
                    <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="completed" className="space-y-4">
                    <div className="grid gap-4">
                      {completedInterviews.map((candidate) => (
                        <Card key={candidate.candidate_scores.candidate.user_id}>
                          <CardHeader>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                                  <User className="h-5 w-5 text-primary" />
                                </div>
                                <div>
                                  <CardTitle className="text-lg">
                                    {candidate.static_knowledge.linkedin[0] || candidate.candidate_scores.candidate.name}
                                  </CardTitle>
                                  <CardDescription>
                                    Interviewed on {new Date(candidate.metadata.consolidation_timestamp).toLocaleDateString()}
                                  </CardDescription>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge 
                                  variant={candidate.hirability_score?.recommendation === "Hire" ? "default" : "destructive"}
                                >
                                  {candidate.hirability_score?.recommendation || candidate.summary.hiring_recommendation_from_lda}
                                </Badge>
                                <div className="text-right">
                                  <div className="text-lg font-semibold">
                                    {candidate.hirability_score?.overall_score.toFixed(1) || candidate.candidate_scores.scores.final}
                                  </div>
                                  <div className="text-sm text-muted-foreground">Overall Score</div>
                                </div>
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <div className="flex items-center gap-2">
                                <Code className="h-4 w-4 text-muted-foreground" />
                                <div>
                                  <div className="font-medium">{candidate.candidate_scores.scores.components.correctness}</div>
                                  <div className="text-sm text-muted-foreground">Technical</div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                                <div>
                                  <div className="font-medium">{candidate.candidate_scores.scores.components.communication}/10</div>
                                  <div className="text-sm text-muted-foreground">Communication</div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Brain className="h-4 w-4 text-muted-foreground" />
                                <div>
                                  <div className="font-medium">{candidate.candidate_scores.scores.components.understanding}</div>
                                  <div className="text-sm text-muted-foreground">Understanding</div>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <div>
                                  <div className="font-medium">{candidate.candidate_scores.time_performance.time_used_min}min</div>
                                  <div className="text-sm text-muted-foreground">Time Used</div>
                                </div>
                              </div>
                            </div>
                            
                            {/* Interview Summary */}
                            <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                              <h4 className="font-medium mb-2">Interview Summary</h4>
                              <p className="text-sm text-muted-foreground line-clamp-2">
                                {candidate.summary.overall_summary}
                              </p>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="active" className="space-y-4">
                    <div className="text-center py-8">
                      <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-medium">No Active Interviews</h3>
                      <p className="text-muted-foreground">All interviews have been completed.</p>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="scheduled" className="space-y-4">
                    <div className="text-center py-8">
                      <Calendar className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-medium">No Scheduled Interviews</h3>
                      <p className="text-muted-foreground">Schedule new interviews to see them here.</p>
                      <Button className="mt-4">
                        <Plus className="h-4 w-4 mr-2" />
                        Schedule Interview
                      </Button>
                    </div>
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
