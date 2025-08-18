import { useState } from "react"
import { Calendar, Search, Filter, MoreHorizontal, MapPin, User, Phone, Mail, CheckCircle, Clock, XCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"

interface Booking {
  id: string
  property: string
  propertyImage: string
  guest: {
    name: string
    email: string
    phone: string
    avatar?: string
  }
  checkIn: string
  checkOut: string
  nights: number
  guests: number
  amount: number
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed'
  bookingDate: string
  specialRequests?: string
}

const bookings: Booking[] = [
  {
    id: "BK001",
    property: "Modern Downtown Loft",
    propertyImage: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop",
    guest: {
      name: "Sarah Chen",
      email: "sarah.chen@email.com",
      phone: "+1 (555) 123-4567"
    },
    checkIn: "2024-12-15",
    checkOut: "2024-12-18",
    nights: 3,
    guests: 2,
    amount: 450,
    status: "confirmed",
    bookingDate: "2024-12-01",
    specialRequests: "Late check-in requested"
  },
  {
    id: "BK002",
    property: "Cozy Beach House",
    propertyImage: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300&fit=crop",
    guest: {
      name: "Mike Johnson",
      email: "mike.j@email.com",
      phone: "+1 (555) 987-6543"
    },
    checkIn: "2024-12-20",
    checkOut: "2024-12-27",
    nights: 7,
    guests: 4,
    amount: 1540,
    status: "pending",
    bookingDate: "2024-12-05"
  },
  {
    id: "BK003",
    property: "Mountain Cabin Retreat",
    propertyImage: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop",
    guest: {
      name: "Emma Davis",
      email: "emma.davis@email.com",
      phone: "+1 (555) 456-7890"
    },
    checkIn: "2024-12-22",
    checkOut: "2024-12-25",
    nights: 3,
    guests: 6,
    amount: 540,
    status: "confirmed",
    bookingDate: "2024-11-28"
  },
  {
    id: "BK004",
    property: "Urban Studio",
    propertyImage: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&h=300&fit=crop",
    guest: {
      name: "Alex Rodriguez",
      email: "alex.rodriguez@email.com",
      phone: "+1 (555) 321-0987"
    },
    checkIn: "2024-11-30",
    checkOut: "2024-12-03",
    nights: 3,
    guests: 1,
    amount: 360,
    status: "completed",
    bookingDate: "2024-11-15"
  },
  {
    id: "BK005",
    property: "Modern Downtown Loft",
    propertyImage: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop",
    guest: {
      name: "Lisa Thompson",
      email: "lisa.t@email.com",
      phone: "+1 (555) 654-3210"
    },
    checkIn: "2024-12-10",
    checkOut: "2024-12-12",
    nights: 2,
    guests: 2,
    amount: 300,
    status: "cancelled",
    bookingDate: "2024-11-20"
  }
]

const getStatusColor = (status: string) => {
  switch (status) {
    case 'confirmed': return 'default'
    case 'pending': return 'secondary'
    case 'cancelled': return 'destructive'
    case 'completed': return 'outline'
    default: return 'secondary'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'confirmed': return CheckCircle
    case 'pending': return Clock
    case 'cancelled': return XCircle
    case 'completed': return CheckCircle
    default: return Clock
  }
}

export function BookingManagement() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [activeTab, setActiveTab] = useState("all")

  const filteredBookings = bookings.filter(booking => {
    const matchesSearch = booking.guest.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         booking.property.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         booking.id.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === "all" || booking.status === statusFilter
    const matchesTab = activeTab === "all" || booking.status === activeTab
    
    return matchesSearch && matchesStatus && matchesTab
  })

  const upcomingBookings = bookings.filter(booking => 
    booking.status === 'confirmed' && new Date(booking.checkIn) > new Date()
  )

  const todayCheckIns = bookings.filter(booking => {
    const today = new Date().toISOString().split('T')[0]
    return booking.checkIn === today && booking.status === 'confirmed'
  })

  const todayCheckOuts = bookings.filter(booking => {
    const today = new Date().toISOString().split('T')[0]
    return booking.checkOut === today && booking.status === 'confirmed'
  })

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="mb-2">Booking Management</h1>
        <p className="text-muted-foreground">
          Manage reservations and guest communications for all your properties.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Upcoming Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{upcomingBookings.length}</div>
            <p className="text-xs text-muted-foreground">Next 30 days</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Check-ins Today</CardTitle>
            <User className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayCheckIns.length}</div>
            <p className="text-xs text-muted-foreground">Guests arriving</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Check-outs Today</CardTitle>
            <User className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayCheckOuts.length}</div>
            <p className="text-xs text-muted-foreground">Guests departing</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input 
            placeholder="Search bookings..." 
            className="pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="confirmed">Confirmed</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          More Filters
        </Button>
      </div>

      {/* Bookings Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All Bookings</TabsTrigger>
          <TabsTrigger value="confirmed">Confirmed</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-4">
          {filteredBookings.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No bookings found</h3>
                <p className="text-muted-foreground">
                  Try adjusting your search or filter criteria.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredBookings.map((booking) => {
                const StatusIcon = getStatusIcon(booking.status)
                
                return (
                  <Card key={booking.id}>
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <img 
                          src={booking.propertyImage} 
                          alt={booking.property}
                          className="w-20 h-20 rounded-lg object-cover"
                        />
                        
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="font-medium">{booking.property}</h3>
                              <p className="text-sm text-muted-foreground">Booking #{booking.id}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant={getStatusColor(booking.status)}>
                                <StatusIcon className="h-3 w-3 mr-1" />
                                {booking.status}
                              </Badge>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="sm">
                                    <MoreHorizontal className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem>View Details</DropdownMenuItem>
                                  <DropdownMenuItem>Contact Guest</DropdownMenuItem>
                                  <DropdownMenuItem>Modify Booking</DropdownMenuItem>
                                  <DropdownMenuItem className="text-destructive">
                                    Cancel Booking
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                            <div>
                              <h4 className="font-medium mb-1">Guest Information</h4>
                              <div className="space-y-1 text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  <User className="h-4 w-4" />
                                  <span>{booking.guest.name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Mail className="h-4 w-4" />
                                  <span>{booking.guest.email}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Phone className="h-4 w-4" />
                                  <span>{booking.guest.phone}</span>
                                </div>
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-medium mb-1">Stay Details</h4>
                              <div className="space-y-1 text-muted-foreground">
                                <div>Check-in: {new Date(booking.checkIn).toLocaleDateString()}</div>
                                <div>Check-out: {new Date(booking.checkOut).toLocaleDateString()}</div>
                                <div>{booking.nights} nights • {booking.guests} guests</div>
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-medium mb-1">Booking Summary</h4>
                              <div className="space-y-1 text-muted-foreground">
                                <div>Total: ${booking.amount}</div>
                                <div>Booked: {new Date(booking.bookingDate).toLocaleDateString()}</div>
                                {booking.specialRequests && (
                                  <div className="text-xs">Special: {booking.specialRequests}</div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex gap-2 pt-2 border-t">
                            <Button variant="outline" size="sm">
                              <Mail className="h-4 w-4 mr-2" />
                              Message Guest
                            </Button>
                            <Button variant="outline" size="sm">
                              View Property
                            </Button>
                            {booking.status === 'pending' && (
                              <>
                                <Button size="sm">Confirm</Button>
                                <Button variant="outline" size="sm">Decline</Button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}