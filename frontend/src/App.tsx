import { useState } from "react"
import { SidebarProvider, SidebarInset } from "./components/ui/sidebar"
import { AppProvider, useApp } from "./contexts/AppContext"
import { AuthForm } from "./components/AuthForm"
import { DashboardSidebar } from "./components/DashboardSidebar"
import { DashboardOverview } from "./components/DashboardOverview"
import { PropertyList } from "./components/PropertyList"
import { AddPropertyWizard } from "./components/AddPropertyWizard"
import { AnalyticsDashboard } from "./components/AnalyticsDashboard"
import { BookingManagement } from "./components/BookingManagement"
import { SettingsPage } from "./components/SettingsPage"

export type NavigationItem = 'overview' | 'properties' | 'add-property' | 'analytics' | 'bookings' | 'settings'

function DashboardApp() {
  const { user, isLoading } = useApp()
  const [activeSection, setActiveSection] = useState<NavigationItem>('overview')

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

  if (!user) {
    return <AuthForm />
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'overview':
        return <DashboardOverview />
      case 'properties':
        return <PropertyList />
      case 'add-property':
        return <AddPropertyWizard />
      case 'analytics':
        return <AnalyticsDashboard />
      case 'bookings':
        return <BookingManagement />
      case 'settings':
        return <SettingsPage />
      default:
        return <DashboardOverview />
    }
  }

  return (
    <SidebarProvider>
      <DashboardSidebar 
        activeSection={activeSection} 
        onSectionChange={setActiveSection}
      />
      <SidebarInset>
        {renderContent()}
      </SidebarInset>
    </SidebarProvider>
  )
}

export default function App() {
  return (
    <AppProvider>
      <DashboardApp />
    </AppProvider>
  )
}