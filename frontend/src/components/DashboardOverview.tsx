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
      change: "+1 this month",
      icon: Building2,
      color: "text-blue-600"
    },
    {
      title: "Total Revenue",
      value: `$${totalRevenue.toLocaleString()}`,
      change: "+12% from last month",
      icon: DollarSign,
      color: "text-green-600"
    },
    {
      title: "Total Bookings",
      value: totalBookings.toString(),
      change: "+8% from last month",
      icon: Calendar,
      color: "text-purple-600"
    },
    {
      title: "Average Rating",
      value: averageRating > 0 ? averageRating.toFixed(1) : "0.0",
      change: "Based on all reviews",
      icon: Star,
      color: "text-yellow-600"
    }
  ]

  const recentBookings = bookings
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)

  const topProperties = properties
    .sort((a, b) => (b.total_revenue || 0) - (a.total_revenue || 0))
    .slice(0, 5)

  return (
    <div className="space-y-4 p-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard Overview</h2>
        <p className="text-muted-foreground">
          Welcome back! Here's what's happening with your properties.
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                {stat.change}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Recent Bookings</CardTitle>
            <CardDescription>
              Latest booking requests and confirmations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentBookings.length > 0 ? (
                recentBookings.map((booking) => (
                  <div key={booking.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">{booking.guest_name}</p>
                      <p className="text-xs text-muted-foreground">{booking.property_title}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(booking.check_in).toLocaleDateString()} - {new Date(booking.check_out).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge variant={booking.status === 'confirmed' ? 'default' : 'secondary'}>
                        {booking.status}
                      </Badge>
                      <p className="text-sm font-medium mt-1">${booking.total_amount}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-center py-4">No bookings yet</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Top Performing Properties</CardTitle>
            <CardDescription>
              Properties with highest revenue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProperties.length > 0 ? (
                topProperties.map((property) => (
                  <div key={property.id} className="flex items-center justify-between">
                    <div className="space-y-1">
                      <p className="text-sm font-medium leading-none">{property.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {property.city}, {property.state}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">${property.total_revenue || 0}</p>
                      <p className="text-xs text-muted-foreground">
                        {property.booking_count || 0} bookings
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground text-center py-4">No properties yet</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks to manage your properties
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <button className="w-full text-left p-2 rounded hover:bg-muted">
              📝 Add New Property
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-muted">
              📊 View Analytics
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-muted">
              📅 Manage Bookings
            </button>
            <button className="w-full text-left p-2 rounded hover:bg-muted">
              ⚙️ Settings
            </button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Property Performance</CardTitle>
            <CardDescription>
              Overall portfolio metrics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Occupancy Rate</span>
                <span>75%</span>
              </div>
              <Progress value={75} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Response Rate</span>
                <span>92%</span>
              </div>
              <Progress value={92} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Guest Satisfaction</span>
                <span>{averageRating.toFixed(1)}/5.0</span>
              </div>
              <Progress value={(averageRating / 5) * 100} />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}