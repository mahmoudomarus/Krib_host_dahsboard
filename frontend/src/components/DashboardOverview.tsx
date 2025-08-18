import { useEffect } from "react"
import { Building2, TrendingUp, Calendar, DollarSign, Star } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Progress } from "./ui/progress"
import { Badge } from "./ui/badge"
import { useApp } from "../contexts/AppContext"

export function DashboardOverview() {
  const { properties, bookings, analytics, getAnalytics } = useApp()

  useEffect(() => {
    getAnalytics()
  }, [])

  const totalRevenue = properties.reduce((sum, property) => sum + (property.total_revenue || 0), 0)
  const totalBookings = properties.reduce((sum, property) => sum + (property.booking_count || 0), 0)
  const averageRating = properties.length > 0 
    ? properties.reduce((sum, property) => sum + (property.rating || 0), 0) / properties.length 
    : 0

  const stats = [
    {
      title: "Total Properties",
      value: properties.length.toString(),
      change: "+2 this month",
      icon: Building2,
      color: "text-blue-600"
    },
    {
      title: "Monthly Revenue",
      value: `$${totalRevenue.toLocaleString()}`,
      change: "+12% from last month",
      icon: DollarSign,
      color: "text-green-600"
    },
    {
      title: "Bookings This Month",
      value: totalBookings.toString(),
      change: "+8% from last month",
      icon: Calendar,
      color: "text-purple-600"
    },
    {
      title: "Occupancy Rate",
      value: "87%",
      change: "+5% from last month",
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
    <div className="p-6 space-y-6">
      <div>
        <h1 className="mb-2">Dashboard Overview</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's what's happening with your rental properties.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
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
        <Card>
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
                      <p className="font-medium">{booking.property_title}</p>
                      <p className="text-sm text-muted-foreground">
                        {booking.guest_name} • {new Date(booking.check_in).toLocaleDateString()} - {new Date(booking.check_out).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">${booking.total_amount}</p>
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
        <Card>
          <CardHeader>
            <CardTitle>Top Performing Properties</CardTitle>
            <CardDescription>Your best properties this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProperties.length > 0 ? (
                topProperties.map((property) => (
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
                        <p className="font-medium">${property.total_revenue || 0}</p>
                        <p className="text-sm text-muted-foreground">75% occupied</p>
                      </div>
                    </div>
                    <Progress value={75} className="h-2" />
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-center py-4">No properties yet</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}