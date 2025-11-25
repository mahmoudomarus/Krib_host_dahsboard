import { Home, Building2, Plus, BarChart3, Calendar, Settings, Bot, LogOut, User, DollarSign, Award, MessageSquare, Star } from "lucide-react"
import KribLogo from "../assets/krib-logo.svg"
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
    id: 'superhost' as NavigationItem,
    title: 'Superhost',
    icon: Award,
    description: 'Verification status'
  },
  {
    id: 'messages' as NavigationItem,
    title: 'Messages',
    icon: MessageSquare,
    description: 'Guest communications'
  },
  {
    id: 'reviews' as NavigationItem,
    title: 'Reviews',
    icon: Star,
    description: 'Guest feedback'
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
    <Sidebar className="krib-sidebar w-64 border-r border-border/50">
      <SidebarHeader className="krib-sidebar-header border-b border-border/50 px-4 py-5">
        <button 
          onClick={() => onSectionChange('overview')}
          className="flex items-center gap-3 w-full hover:opacity-80 transition-opacity cursor-pointer"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-lg krib-logo-container bg-krib-lime/10">
            <img src={KribLogo} alt="Krib" className="h-6 w-6" />
          </div>
          <div className="text-left">
            <h2 className="text-lg font-bold text-foreground">
              Krib
            </h2>
            <p className="text-xs text-muted-foreground font-medium">Property Dashboard</p>
          </div>
        </button>
      </SidebarHeader>
      
      <SidebarContent className="px-3 py-4">
        <SidebarGroup>
          <SidebarGroupLabel className="krib-sidebar-group-label text-xs font-semibold text-muted-foreground uppercase tracking-wider px-3 mb-2">
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="krib-sidebar-menu space-y-1">
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => onSectionChange(item.id)}
                    isActive={activeSection === item.id}
                    tooltip={item.description}
                    className={`
                      flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                      transition-all duration-200 w-full
                      ${activeSection === item.id 
                        ? 'bg-krib-lime/10 text-foreground shadow-sm border border-krib-lime/20' 
                        : 'text-muted-foreground hover:bg-accent hover:text-foreground'
                      }
                    `}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    <span className="truncate">{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="border-t border-border/50 p-4 krib-sidebar-header mt-auto">
        <div className="space-y-2">
          <button 
            onClick={() => onSectionChange('settings')}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-accent/50 border border-border/50 w-full hover:bg-accent hover:border-border transition-all cursor-pointer"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-krib-lime/10">
              <User className="h-4 w-4 text-foreground" />
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-sm font-medium text-foreground truncate">{user?.name || 'User'}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
            </div>
          </button>
          <Button
            variant="ghost"
            size="sm"
            onClick={signOut}
            className="w-full justify-start text-muted-foreground hover:text-foreground hover:bg-red-50 dark:hover:bg-red-950 transition-all duration-200 h-9"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}