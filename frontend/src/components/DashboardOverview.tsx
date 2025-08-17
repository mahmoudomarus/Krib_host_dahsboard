import { Building2, TrendingUp, Calendar, DollarSign, Users, Star } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Progress } from "./ui/progress"
import { Badge } from "./ui/badge"

const stats = [
  {
    title: "Total Properties",
    value: "12",
    change: "+2 this month",
    icon: Building2,
    color: "text-blue-600"
  },
  {
    title: "Monthly Revenue",
    value: "$8,450",
    change: "+12% from last month",
    icon: DollarSign,
    color: "text-green-600"
  },
  {
    title: "Bookings This Month",
    value: "34",
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

const recentBookings = [
  {
    id: "1",
    property: "Modern Downtown Loft",
    guest: "Sarah Chen",
    dates: "Dec 15-18, 2024",
    amount: "$420",
    status: "confirmed"
  },
  {
    id: "2",
    property: "Cozy Beach House",
    guest: "Mike Johnson",
    dates: "Dec 20-27, 2024",
    amount: "$980",
    status: "pending"
  },
  {
    id: "3",
    property: "Mountain Cabin Retreat",
    guest: "Emma Davis",
    dates: "Dec 22-25, 2024",
    amount: "$540",
    status: "confirmed"
  }
]

const topProperties = [
  {
    name: "Modern Downtown Loft",
    revenue: "$2,340",
    bookings: 8,
    rating: 4.9,
    occupancy: 92
  },
  {
    name: "Cozy Beach House",
    revenue: "$1,890",
    bookings: 6,
    rating: 4.8,
    occupancy: 85
  },
  {
    name: "Mountain Cabin Retreat",
    revenue: "$1,650",
    bookings: 5,
    rating: 4.7,
    occupancy: 78
  }
]

export function DashboardOverview() {
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
              {recentBookings.map((booking) => (
                <div key={booking.id} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="font-medium">{booking.property}</p>
                    <p className="text-sm text-muted-foreground">
                      {booking.guest} • {booking.dates}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{booking.amount}</p>
                    <Badge 
                      variant={booking.status === 'confirmed' ? 'default' : 'secondary'}
                    >
                      {booking.status}
                    </Badge>
                  </div>
                </div>
              ))}
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
              {topProperties.map((property, index) => (
                <div key={property.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{property.name}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span>{property.bookings} bookings</span>
                        <span>•</span>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 fill-current text-yellow-500" />
                          <span>{property.rating}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{property.revenue}</p>
                      <p className="text-sm text-muted-foreground">{property.occupancy}% occupied</p>
                    </div>
                  </div>
                  <Progress value={property.occupancy} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}