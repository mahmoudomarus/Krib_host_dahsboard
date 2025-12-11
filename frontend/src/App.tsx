import { useState, useEffect, lazy, Suspense } from "react"
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { SidebarProvider } from "./components/ui/sidebar"
import { AppProvider, useApp } from "./contexts/AppContext"
import { Homepage } from "./components/Homepage"
import { AuthForm } from "./components/AuthForm"
import { AuthCallback } from "./components/AuthCallback"
import { DashboardSidebar } from "./components/DashboardSidebar"
import { NotificationBell } from "./components/NotificationBell"

// Lazy load heavy dashboard components for better performance
const DashboardOverview = lazy(() => import("./components/DashboardOverview").then(m => ({ default: m.DashboardOverview })))
const PropertyList = lazy(() => import("./components/PropertyList").then(m => ({ default: m.PropertyList })))
const AddPropertyWizard = lazy(() => import("./components/AddPropertyWizard").then(m => ({ default: m.AddPropertyWizard })))
const AnalyticsDashboard = lazy(() => import("./components/AnalyticsDashboard").then(m => ({ default: m.AnalyticsDashboard })))
const BookingManagement = lazy(() => import("./components/BookingManagement").then(m => ({ default: m.BookingManagement })))
const FinancialDashboard = lazy(() => import("./components/FinancialDashboard").then(m => ({ default: m.FinancialDashboard })))
const SettingsPage = lazy(() => import("./components/SettingsPage").then(m => ({ default: m.SettingsPage })))
const SuperhostVerification = lazy(() => import("./components/SuperhostVerification").then(m => ({ default: m.SuperhostVerification })))
const MessagingDashboard = lazy(() => import("./components/MessagingDashboard").then(m => ({ default: m.MessagingDashboard })))
const ReviewsDashboard = lazy(() => import("./components/ReviewsDashboard").then(m => ({ default: m.ReviewsDashboard })))
const GuestPaymentPage = lazy(() => import("./components/GuestPaymentPage").then(m => ({ default: m.GuestPaymentPage })))

export type NavigationItem = 'overview' | 'properties' | 'add-property' | 'analytics' | 'bookings' | 'financials' | 'superhost' | 'messages' | 'reviews' | 'settings'

// Skeleton loader component for dashboard pages
function PageSkeleton() {
  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-300">
      <div className="space-y-2">
        <div className="h-8 bg-muted rounded-lg w-64 animate-pulse"></div>
        <div className="h-4 bg-muted rounded w-96 animate-pulse"></div>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-28 bg-muted rounded-xl animate-pulse" style={{ animationDelay: `${i * 100}ms` }}></div>
        ))}
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="h-80 bg-muted rounded-xl animate-pulse"></div>
        <div className="h-80 bg-muted rounded-xl animate-pulse" style={{ animationDelay: '100ms' }}></div>
      </div>
    </div>
  )
}

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
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="relative w-12 h-12 mx-auto mb-4">
            <div className="absolute inset-0 border-2 border-muted rounded-full"></div>
            <div className="absolute inset-0 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-muted-foreground text-sm">Loading your dashboard...</p>
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
      <Suspense fallback={
        <div className="min-h-screen flex items-center justify-center bg-background">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div>
        </div>
      }>
        <Routes>
          <Route path="/pay/:bookingId" element={<GuestPaymentPage />} />
          <Route path="/pay/:bookingId/success" element={<GuestPaymentPage />} />
        </Routes>
      </Suspense>
    )
  }

  // Show homepage for non-authenticated users or when on homepage route
  if (!user && !location.pathname.startsWith('/auth')) {
    return (
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/auth" element={<AuthForm />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/pay/:bookingId" element={
          <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div></div>}>
            <GuestPaymentPage />
          </Suspense>
        } />
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
        <main className="flex-1 overflow-auto bg-background" style={{ marginLeft: '16rem' }}>
          <div className="sticky top-0 z-40 bg-background/95 backdrop-blur-sm border-b">
            <div className="flex items-center justify-end h-14 px-8">
              <NotificationBell />
            </div>
          </div>
          <div className="px-8 py-6">
          <Suspense fallback={<PageSkeleton />}>
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
          </Suspense>
          </div>
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