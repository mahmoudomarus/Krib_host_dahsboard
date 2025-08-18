import { Home, Building2, Plus, BarChart3, Calendar, Settings, Bot, LogOut, User, DollarSign } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from "./ui/sidebar"
import { NavigationItem } from "../App"
import { Button } from "./ui/button"
import { useApp } from "../contexts/AppContext"

interface DashboardSidebarProps {
  activeSection: NavigationItem
  onSectionChange: (section: NavigationItem) => void
}

const navigationItems = [
  {
    id: 'overview' as NavigationItem,
    title: 'Overview',
    icon: Home,
    description: 'Dashboard overview'
  },
  {
    id: 'properties' as NavigationItem,
    title: 'My Properties',
    icon: Building2,
    description: 'Manage your listings'
  },
  {
    id: 'add-property' as NavigationItem,
    title: 'Add Property',
    icon: Plus,
    description: 'AI-powered listing creation'
  },
  {
    id: 'analytics' as NavigationItem,
    title: 'Analytics',
    icon: BarChart3,
    description: 'Performance insights'
  },
  {
    id: 'bookings' as NavigationItem,
    title: 'Bookings',
    icon: Calendar,
    description: 'Manage reservations'
  },
  {
    id: 'financials' as NavigationItem,
    title: 'Financials',
    icon: DollarSign,
    description: 'Earnings & payouts'
  },
  {
    id: 'settings' as NavigationItem,
    title: 'Settings',
    icon: Settings,
    description: 'Account preferences'
  }
]

export function DashboardSidebar({ activeSection, onSectionChange }: DashboardSidebarProps) {
  const { user, signOut } = useApp()
  
  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-sidebar-foreground">Krib AI</h2>
            <p className="text-sidebar-foreground/60">Property Dashboard</p>
          </div>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => onSectionChange(item.id)}
                    isActive={activeSection === item.id}
                    tooltip={item.description}
                    className={activeSection === item.id ? 'bg-sidebar-accent text-sidebar-accent-foreground' : ''}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="border-t border-sidebar-border p-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 px-2">
            <User className="h-4 w-4 text-sidebar-foreground/60" />
            <div className="flex-1 min-w-0">
              <p className="text-sidebar-foreground truncate">{user?.name || 'User'}</p>
              <p className="text-sidebar-foreground/60 truncate">{user?.email}</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={signOut}
            className="w-full justify-start text-sidebar-foreground/60 hover:text-sidebar-foreground"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}