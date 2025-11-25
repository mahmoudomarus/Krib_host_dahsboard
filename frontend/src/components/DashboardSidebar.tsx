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
    <Sidebar className="krib-sidebar w-[280px] fixed left-0 top-0 h-screen">
      <SidebarHeader className="krib-sidebar-header border-b border-sidebar-border p-8">
        <button 
          onClick={() => onSectionChange('overview')}
          className="flex items-center gap-4 w-full hover:opacity-80 transition-opacity cursor-pointer"
        >
          <div className="flex h-14 w-14 items-center justify-center rounded-xl krib-logo-container">
            <img src={KribLogo} alt="Krib" className="h-10 w-10" />
          </div>
          <div className="text-left">
            <h2 className="text-2xl font-bold text-sidebar-foreground bg-gradient-to-r from-krib-gray-dark to-krib-black bg-clip-text">
              Krib
            </h2>
            <p className="text-base text-sidebar-foreground/70 font-medium">Property Dashboard</p>
          </div>
        </button>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="krib-sidebar-group-label px-6 py-3 text-xs">Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="krib-sidebar-menu px-3">
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton
                    onClick={() => onSectionChange(item.id)}
                    isActive={activeSection === item.id}
                    tooltip={item.description}
                    className={`transition-all duration-300 krib-sidebar-item text-base py-3 px-4 ${
                      activeSection === item.id ? 'krib-sidebar-active' : ''
                    }`}
                  >
                    <item.icon className="h-5 w-5" />
                    <span className="font-medium">{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="border-t border-sidebar-border p-6 krib-sidebar-header">
        <div className="space-y-3">
          <button 
            onClick={() => onSectionChange('settings')}
            className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/50 border border-krib-lime/10 w-full hover:bg-white/70 hover:border-krib-lime/20 transition-all cursor-pointer"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-krib-lime/20 to-krib-lime-light/10">
              <User className="h-5 w-5 text-krib-gray-dark" />
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-base font-semibold text-sidebar-foreground truncate">{user?.name || 'User'}</p>
              <p className="text-sm text-sidebar-foreground/70 truncate">{user?.email}</p>
            </div>
          </button>
          <Button
            variant="ghost"
            size="default"
            onClick={signOut}
            className="w-full justify-start text-base text-sidebar-foreground/70 hover:text-sidebar-foreground hover:bg-red-50 transition-all duration-200 py-3"
          >
            <LogOut className="h-5 w-5 mr-2" />
            Sign Out
          </Button>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}