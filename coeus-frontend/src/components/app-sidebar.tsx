"use client"

import * as React from "react"
import {
  IconCamera,
  IconChartBar,
  IconDashboard,
  IconDatabase,
  IconFileAi,
  IconFileDescription,
  IconFileWord,
  IconFolder,
  IconHelp,
  IconListDetails,
  IconReport,
  IconSearch,
  IconSettings,
  IconUsers,
} from "@tabler/icons-react"

import { NavDocuments } from "@/components/nav-documents"
import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: IconDashboard,
    },
    {
      title: "Candidates",
      url: "/candidates",
      icon: IconUsers,
    },
    {
      title: "Analytics",
      url: "/analytics",
      icon: IconChartBar,
    },
    {
      title: "Interview Process",
      url: "/interviews",
      icon: IconListDetails,
    },
    {
      title: "Reports",
      url: "/reports",
      icon: IconReport,
    },
  ],
  navClouds: [
    {
      title: "Interview Management",
      icon: IconCamera,
      isActive: true,
      url: "#",
      items: [
        {
          title: "Active Interviews",
          url: "/interviews/active",
        },
        {
          title: "Completed",
          url: "/interviews/completed",
        },
        {
          title: "Scheduled",
          url: "/interviews/scheduled",
        },
      ],
    },
    {
      title: "Candidate Pipeline",
      icon: IconFileDescription,
      url: "#",
      items: [
        {
          title: "New Applications",
          url: "/candidates/new",
        },
        {
          title: "In Review",
          url: "/candidates/review",
        },
        {
          title: "Hired",
          url: "/candidates/hired",
        },
      ],
    },
    {
      title: "AI Analysis",
      icon: IconFileAi,
      url: "#",
      items: [
        {
          title: "Interview Insights",
          url: "/ai/insights",
        },
        {
          title: "Performance Metrics",
          url: "/ai/metrics",
        },
        {
          title: "Recommendations",
          url: "/ai/recommendations",
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Settings",
      url: "#",
      icon: IconSettings,
    },
    {
      title: "Get Help",
      url: "#",
      icon: IconHelp,
    },
    {
      title: "Search",
      url: "#",
      icon: IconSearch,
    },
  ],
  documents: [
    {
      name: "Data Library",
      url: "/data-library",
      icon: IconDatabase,
    },
    {
      name: "Reports",
      url: "/reports",
      icon: IconReport,
    },
    {
      name: "Word Assistant",
      url: "/word-assistant",
      icon: IconFileWord,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="data-[slot=sidebar-menu-button]:!p-1.5"
            >
              <a href="/">
                <img src="/assets/logo.svg" alt="Coeus Logo" className="!size-5" />
                <span className="text-base font-semibold">Coeus</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavDocuments items={data.documents} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
