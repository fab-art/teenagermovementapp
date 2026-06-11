"use client"

import * as React from "react"
import Link from "next/link"
import {
  Home,
  Pill,
  BookOpen,
  CreditCard,
  ClipboardList,
  Heart,
  Stethoscope,
} from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "Medicines",
    url: "/medicines",
    icon: Pill,
  },
  {
    title: "Therapeutic Classes",
    url: "/therapeutic-classes",
    icon: Stethoscope,
  },
  {
    title: "Reimbursement",
    url: "/reimbursement",
    icon: CreditCard,
  },
  {
    title: "Product Registry",
    url: "/product-registry",
    icon: ClipboardList,
  },
  {
    title: "Guidelines",
    url: "/guidelines",
    icon: BookOpen,
  },
  {
    title: "Favorites",
    url: "/favorites",
    icon: Heart,
  },
]

export function AppSidebar() {
  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="flex items-center justify-between p-4">
        <div className="flex items-center gap-2 font-semibold text-primary text-blue-600">
          <Pill className="h-6 w-6" />
          <span className="group-data-[collapsible=icon]:hidden">RMFDP</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Menu</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton tooltip={item.title} render={<Link href={item.url} />}>
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
