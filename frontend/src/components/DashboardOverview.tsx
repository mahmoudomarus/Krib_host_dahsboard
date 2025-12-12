import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Building2, TrendingUp, Calendar, DollarSign, Star, Plus, BarChart3, BookOpen, CreditCard, Settings } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Progress } from "./ui/progress"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { useApp } from "../contexts/AppContext"

export function DashboardOverview() {
  const { properties, bookings, analytics, getAnalytics, loadProperties, loadBookings } = useApp()
  const navigate = useNavigate()

  useEffect(() => {
    // Load all necessary data for the dashboard
    const loadDashboardData = async () => {
      await Promise.all([
        loadProperties(),
        loadBookings(),
        getAnalytics()
      ])
    }
    
    loadDashboardData()
  }, [])

  const totalRevenue = bookings
    .filter(b => b.payment_status === 'succeeded' || b.payment_status === 'paid')
    .reduce((sum, booking) => sum + (booking.total_amount || 0), 0)
  const totalBookings = bookings.length
  const averageRating = properties.length > 0 
    ? properties.reduce((sum, property) => sum + (property.rating || 0), 0) / properties.length 
    : 0

  // Calculate actual occupancy rate based on bookings
  const calculateOccupancyRate = () => {
    if (properties.length === 0) return 0
    
    const today = new Date()
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000))
    
    const recentBookings = bookings.filter(booking => 
      new Date(booking.created_at) >= thirtyDaysAgo && 
      booking.status === 'confirmed'
    )
    
    if (recentBookings.length === 0) return 0
    
    // Simple calculation: (total booked nights / (properties * 30 days)) * 100
    const totalBookedNights = recentBookings.reduce((sum, booking) => sum + booking.nights, 0)
    const totalPossibleNights = properties.length * 30
    
    return totalPossibleNights > 0 ? Math.round((totalBookedNights / totalPossibleNights) * 100) : 0
  }

  const occupancyRate = calculateOccupancyRate()

  const stats = [
    {
      title: "Total Properties",
      value: properties.length.toString(),
      change: properties.length > 0 ? `${properties.length} active` : "No properties yet",
      icon: Building2,
      color: "text-emerald-600"
    },
    {
      title: "Total Revenue",
      value: `AED ${totalRevenue.toLocaleString()}`,
      change: totalRevenue > 0 ? "From confirmed bookings" : "No revenue yet",
      icon: DollarSign,
      color: "text-green-600"
    },
    {
      title: "Total Bookings",
      value: totalBookings.toString(),
      change: totalBookings > 0 ? `${totalBookings} confirmed` : "No bookings yet",
      icon: Calendar,
      color: "text-purple-600"
    },
    {
      title: "Occupancy Rate",
      value: `${occupancyRate}%`,
      change: occupancyRate > 0 ? "Last 30 days" : "No bookings to calculate",
      icon: TrendingUp,
      color: "text-orange-600"
    }
  ]

  const recentBookings = bookings
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)

  const topProperties = properties
    .sort((a, b) => (b.total_revenue || 0) - (a.total_revenue || 0))
    .slice(0, 3)

  return (
    <div className=" space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard Overview</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's what's happening with your rental properties.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title} className="shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm">{stat.title}</CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Bookings */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Recent Bookings</CardTitle>
            <CardDescription>Latest reservations for your properties</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentBookings.length > 0 ? (
                recentBookings.map((booking) => (
                  <div key={booking.id} className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="font-medium">{booking.property_title || 'Property'}</p>
                      <p className="text-sm text-muted-foreground">
                        {booking.guest_name} • {new Date(booking.check_in).toLocaleDateString()} - {new Date(booking.check_out).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">AED {booking.total_amount}</p>
                      <Badge 
                        variant={booking.status === 'confirmed' ? 'default' : 'secondary'}
                      >
                        {booking.status}
                      </Badge>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-center py-4">No bookings yet</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Top Performing Properties */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Top Performing Properties</CardTitle>
            <CardDescription>Your best properties by revenue</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProperties.length > 0 ? (
                topProperties.map((property) => {
                  const propertyOccupancy = property.booking_count > 0 ? 
                    Math.min(Math.round((property.booking_count / 30) * 100), 100) : 0
                  
                  return (
                    <div key={property.id} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{property.title}</p>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <span>{property.booking_count || 0} bookings</span>
                            <span>•</span>
                            <div className="flex items-center gap-1">
                              <Star className="h-3 w-3 fill-current text-yellow-500" />
                              <span>{property.rating || 0}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">AED {property.total_revenue || 0}</p>
                          <p className="text-sm text-muted-foreground">{propertyOccupancy}% occupied</p>
                        </div>
                      </div>
                      <Progress value={propertyOccupancy} className="h-2" />
                    </div>
                  )
                })
              ) : (
                <p className="text-muted-foreground text-center py-4">No properties yet</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions - Consistent button styling */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks to manage your properties</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <button 
              className="w-full flex items-center p-3 rounded-lg border border-emerald-200 bg-emerald-50 hover:bg-emerald-100 transition-colors group"
              onClick={() => navigate('/dashboard/add-property')}
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500 mr-3">
                <Plus className="h-4 w-4 text-white" />
                </div>
                <div className="text-left">
                <div className="font-medium text-sm text-emerald-900">Add New Property</div>
                <div className="text-xs text-emerald-700">List a new rental property</div>
              </div>
            </button>
            
            <button 
              className="w-full flex items-center p-3 rounded-lg border hover:bg-muted/50 transition-colors group"
              onClick={() => navigate('/dashboard/analytics')}
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted mr-3">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="text-left">
                <div className="font-medium text-sm">View Analytics</div>
                <div className="text-xs text-muted-foreground">Performance insights</div>
              </div>
            </button>
            
            <button 
              className="w-full flex items-center p-3 rounded-lg border hover:bg-muted/50 transition-colors group"
              onClick={() => navigate('/dashboard/bookings')}
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted mr-3">
                <BookOpen className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="text-left">
                <div className="font-medium text-sm">Manage Bookings</div>
                <div className="text-xs text-muted-foreground">Reservations & guests</div>
              </div>
            </button>
            
            <button 
              className="w-full flex items-center p-3 rounded-lg border hover:bg-muted/50 transition-colors group"
              onClick={() => navigate('/dashboard/financials')}
            >
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted mr-3">
                <CreditCard className="h-4 w-4 text-muted-foreground" />
                </div>
                <div className="text-left">
                <div className="font-medium text-sm">Financial Dashboard</div>
                <div className="text-xs text-muted-foreground">Earnings & payouts</div>
              </div>
            </button>
            
            <button 
              className="w-full flex items-center p-3 rounded-lg border hover:bg-muted/50 transition-colors group"
              onClick={() => navigate('/dashboard/settings')}
            >
                <div className="text-left">
                <div className="font-medium text-sm">Account Settings</div>
                <div className="text-xs text-muted-foreground">Profile & preferences</div>
              </div>
            </button>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>Property Performance</CardTitle>
            <CardDescription>Overall portfolio metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Portfolio Occupancy</span>
                <span className="text-muted-foreground/30">·····</span>
                <span className="font-medium">{occupancyRate}%</span>
              </div>
              <Progress value={occupancyRate} className="h-1.5" />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Active Properties</span>
                <span className="text-muted-foreground/30">·····</span>
                <span className="font-medium">{properties.filter(p => p.status === 'active').length}</span>
              </div>
              <Progress value={properties.length > 0 ? (properties.filter(p => p.status === 'active').length / properties.length) * 100 : 0} className="h-1.5" />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Average Rating</span>
                <span className="text-muted-foreground/30">·····</span>
                <span className="font-medium">{averageRating.toFixed(1)}/5.0</span>
              </div>
              <Progress value={(averageRating / 5) * 100} className="h-1.5" />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}