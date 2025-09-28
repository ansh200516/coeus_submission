import { AppSidebar } from "@/components/app-sidebar"
import { CandidateDataTable } from "@/components/candidates/candidate-data-table"
import { CandidateStatsCards } from "@/components/candidates/candidate-stats-cards"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { CandidateDataService } from "@/lib/candidates/data-service"
import { Button } from "@/components/ui/button"
import { Plus, Filter, Download, Search } from "lucide-react"
import { Input } from "@/components/ui/input"

export default async function CandidatesPage() {
  // Fetch candidate data
  const candidateStats = await CandidateDataService.getDashboardStats()
  const candidateTableData = await CandidateDataService.getCandidateTableData()

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
                    <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
                    <p className="text-muted-foreground">
                      Manage and review all candidate applications and interviews
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Filter className="h-4 w-4 mr-2" />
                      Filter
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Candidate
                    </Button>
                  </div>
                </div>
                
                {/* Search Bar */}
                <div className="flex items-center gap-4">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search candidates by name, skills, or position..."
                      className="pl-10"
                    />
                  </div>
                </div>
              </div>

              {/* Stats Cards */}
              <CandidateStatsCards stats={candidateStats} />
              
              {/* Candidates Table */}
              <CandidateDataTable data={candidateTableData} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
