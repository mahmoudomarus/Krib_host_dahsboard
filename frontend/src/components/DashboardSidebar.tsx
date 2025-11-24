import { Home, Building2, Plus, BarChart3, Calendar, Settings, Bot, LogOut, User, DollarSign, Award, MessageSquare } from "lucide-react"
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
    id: 'settings' as NavigationItem,
    title: 'Settings',
    icon: Settings,
    description: 'Account preferences'
  }
]

export function DashboardSidebar({ activeSection, onSectionChange }: DashboardSidebarProps) {
  const { user, signOut } = useApp()
  
  return (
    <Sidebar className="krib-sidebar">
      <SidebarHeader className="krib-sidebar-header border-b border-sidebar-border p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl krib-logo-container">
            <img src={KribLogo} alt="Krib" className="h-8 w-8" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-sidebar-foreground bg-gradient-to-r from-krib-gray-dark to-krib-black bg-clip-text">
              Krib
            </h2>
            <p className="text-sm text-sidebar-foreground/70 font-medium">Property Dashboard</p>
          </div>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="krib-sidebar-group-label">Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="krib-sidebar-menu">
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => onSectionChange(item.id)}
                    isActive={activeSection === item.id}
                    tooltip={item.description}
                    className={`transition-all duration-300 krib-sidebar-item ${
                      activeSection === item.id ? 'krib-sidebar-active' : ''
                    }`}
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
      
      <SidebarFooter className="border-t border-sidebar-border p-4 krib-sidebar-header">
        <div className="space-y-3">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/50 border border-krib-lime/10">
            <div className="relative cursor-pointer" onClick={() => window.location.href = '/dashboard/settings'}>
              {user?.avatar_url ? (
                <img 
                  src={user.avatar_url} 
                  alt={user.name || 'User'} 
                  className="h-10 w-10 rounded-full object-cover border-2 border-krib-lime"
                />
              ) : (
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-krib-lime/20 to-krib-lime-light/10 border-2 border-krib-lime/30">
                  <User className="h-5 w-5 text-krib-gray-dark" />
                </div>
              )}
              <div className="absolute -bottom-0.5 -right-0.5 h-4 w-4 rounded-full bg-krib-lime border-2 border-white flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-2.5 h-2.5 text-krib-black">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                </svg>
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-sidebar-foreground truncate">{user?.name || 'User'}</p>
              <p className="text-xs text-sidebar-foreground/70 truncate">{user?.email}</p>
              {user?.bio && (
                <p className="text-xs text-sidebar-foreground/50 truncate mt-0.5">{user.bio}</p>
              )}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={signOut}
            className="w-full justify-start text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-red-50 transition-all duration-200"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}