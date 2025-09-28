import { AppSidebar } from "@/components/app-sidebar"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { CandidateDataTable } from "@/components/candidates/candidate-data-table"
import { CandidateStatsCards } from "@/components/candidates/candidate-stats-cards"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { CandidateDataService } from "@/lib/candidates/data-service"

export default async function Page() {
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
              <CandidateStatsCards stats={candidateStats} />
              <div className="px-4 lg:px-6">
                <ChartAreaInteractive />
              </div>
              <CandidateDataTable data={candidateTableData} />
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
