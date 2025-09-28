import { TrendingDown, TrendingUp } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardAction,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function SectionCards() {
  return (
    <div className="grid grid-cols-1 gap-6 px-6 lg:px-8 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm">Total Revenue</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            $1,250.00
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className="bg-green-500/10 border-green-500/20 text-green-400">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12.5%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            Trending up this month <TrendingUp className="size-4 text-green-400" />
          </div>
          <div className="text-muted-foreground">
            Visitors for the last 6 months
          </div>
        </CardFooter>
      </Card>
      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm">New Customers</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            1,234
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className="bg-red-500/10 border-red-500/20 text-red-400">
              <TrendingDown className="h-3 w-3 mr-1" />
              -20%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            Down 20% this period <TrendingDown className="size-4 text-red-400" />
          </div>
          <div className="text-muted-foreground">
            Acquisition needs attention
          </div>
        </CardFooter>
      </Card>
      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm">Active Accounts</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            45,678
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className="bg-green-500/10 border-green-500/20 text-green-400">
              <TrendingUp className="h-3 w-3 mr-1" />
              +12.5%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            Strong user retention <TrendingUp className="size-4 text-green-400" />
          </div>
          <div className="text-muted-foreground">Engagement exceed targets</div>
        </CardFooter>
      </Card>
      <Card className="@container/card bg-background/60 backdrop-blur-sm border-border/30 hover:bg-background/80 transition-all duration-200">
        <CardHeader className="pb-4">
          <CardDescription className="text-muted-foreground text-sm">Growth Rate</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl text-foreground">
            4.5%
          </CardTitle>
          <CardAction>
            <Badge variant="outline" className="bg-blue-500/10 border-blue-500/20 text-blue-400">
              <TrendingUp className="h-3 w-3 mr-1" />
              +4.5%
            </Badge>
          </CardAction>
        </CardHeader>
        <CardFooter className="flex-col items-start gap-2 text-sm pt-0">
          <div className="line-clamp-1 flex items-center gap-2 font-medium text-foreground">
            Steady performance increase <TrendingUp className="size-4 text-blue-400" />
          </div>
          <div className="text-muted-foreground">Meets growth projections</div>
        </CardFooter>
      </Card>
    </div>
  )
}
