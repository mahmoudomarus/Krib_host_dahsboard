import { useState, useEffect } from "react"
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { SidebarProvider } from "./components/ui/sidebar"
import { AppProvider, useApp } from "./contexts/AppContext"
import { Homepage } from "./components/Homepage"
import { AuthForm } from "./components/AuthForm"
import { AuthCallback } from "./components/AuthCallback"
import { DashboardSidebar } from "./components/DashboardSidebar"
import { DashboardOverview } from "./components/DashboardOverview"
import { PropertyList } from "./components/PropertyList"
import { AddPropertyWizard } from "./components/AddPropertyWizard"
import { AnalyticsDashboard } from "./components/AnalyticsDashboard"
import { BookingManagement } from "./components/BookingManagement"
import { FinancialDashboard } from "./components/FinancialDashboard"
import { SettingsPage } from "./components/SettingsPage"
import { SuperhostVerification } from "./components/SuperhostVerification"
import { MessagingDashboard } from "./components/MessagingDashboard"
import { NotificationBell } from "./components/NotificationBell"
import { ReviewsDashboard } from "./components/ReviewsDashboard"
import { GuestPaymentPage } from "./components/GuestPaymentPage"

export type NavigationItem = 'overview' | 'properties' | 'add-property' | 'analytics' | 'bookings' | 'financials' | 'superhost' | 'messages' | 'reviews' | 'settings'

function AppContent() {
  const { user, isLoading } = useApp()
  const location = useLocation()
  const navigate = useNavigate()
  
  // Check if we're on a dashboard route
  const isDashboardRoute = location.pathname.startsWith('/dashboard') || 
    ['overview', 'properties', 'add-property', 'analytics', 'bookings', 'financials', 'superhost', 'messages', 'settings'].some(path => 
      location.pathname === `/${path}`
    )
  
  // Map URL paths to navigation items
  const getActiveSection = (pathname: string): NavigationItem => {
    const path = pathname.replace('/dashboard/', '').replace('/', '') || 'overview'
    return ['overview', 'properties', 'add-property', 'analytics', 'bookings', 'financials', 'superhost', 'messages', 'settings'].includes(path) 
      ? path as NavigationItem 
      : 'overview'
  }
  
  const [activeSection, setActiveSection] = useState<NavigationItem>(getActiveSection(location.pathname))
  
  // Update active section when URL changes
  useEffect(() => {
    setActiveSection(getActiveSection(location.pathname))
  }, [location.pathname])
  
  // Handle section changes with navigation
  const handleSectionChange = (section: NavigationItem) => {
    setActiveSection(section)
    navigate(section === 'overview' ? '/dashboard' : `/dashboard/${section}`)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  // Handle auth callback
  if (location.pathname === '/auth/callback') {
    return <AuthCallback />
  }

  // Public payment page (no auth required)
  if (location.pathname.startsWith('/pay/')) {
    return (
      <Routes>
        <Route path="/pay/:bookingId" element={<GuestPaymentPage />} />
        <Route path="/pay/:bookingId/success" element={<GuestPaymentPage />} />
      </Routes>
    )
  }

  // Show homepage for non-authenticated users or when on homepage route
  if (!user && !location.pathname.startsWith('/auth')) {
    return (
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/auth" element={<AuthForm />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/pay/:bookingId" element={<GuestPaymentPage />} />
        <Route path="*" element={<Homepage />} />
      </Routes>
    )
  }

  // Show auth form when on auth route (but not callback)
  if (location.pathname.startsWith('/auth') && location.pathname !== '/auth/callback') {
    return <AuthForm />
  }

  // Redirect to dashboard if user is logged in and on homepage
  if (user && location.pathname === '/') {
    navigate('/dashboard')
    return null
  }

  // Show dashboard for authenticated users
  if (!user && isDashboardRoute) {
    navigate('/auth')
    return null
  }



  return (
    <SidebarProvider>
      <div className="flex h-screen w-full">
        <DashboardSidebar 
          activeSection={activeSection} 
          onSectionChange={handleSectionChange} 
        />
        <main className="flex-1 overflow-auto krib-dashboard-background" style={{ marginLeft: '16rem' }}>
          <div className="sticky top-0 z-40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
            <div className="flex items-center justify-end h-16 px-6">
              <NotificationBell />
            </div>
          </div>
          <Routes>
            <Route path="/dashboard" element={<DashboardOverview />} />
            <Route path="/dashboard/overview" element={<DashboardOverview />} />
            <Route path="/dashboard/properties" element={<PropertyList />} />
            <Route path="/dashboard/add-property" element={<AddPropertyWizard />} />
            <Route path="/dashboard/analytics" element={<AnalyticsDashboard />} />
            <Route path="/dashboard/bookings" element={<BookingManagement />} />
            <Route path="/dashboard/financials" element={<FinancialDashboard />} />
            <Route path="/dashboard/superhost" element={<SuperhostVerification />} />
            <Route path="/dashboard/messages" element={<MessagingDashboard />} />
            <Route path="/dashboard/reviews" element={<ReviewsDashboard />} />
            <Route path="/dashboard/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </SidebarProvider>
  )
}

function KribApp() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default function App() {
  return (
    <AppProvider>
      <KribApp />
    </AppProvider>
  )
}