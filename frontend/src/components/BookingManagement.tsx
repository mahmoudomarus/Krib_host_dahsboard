import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Calendar, Search, Filter, MoreHorizontal, MapPin, User, Phone, Mail, CheckCircle, Clock, XCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { useApp } from "../contexts/AppContext"

interface Booking {
  id: string
  property_id: string
  property_title?: string
  guest_name: string
  guest_email: string
  guest_phone?: string
  check_in: string
  check_out: string
  nights: number
  guests: number
  total_amount: number
  status: 'confirmed' | 'pending' | 'cancelled' | 'completed' | 'no_show'
  payment_status?: string
  created_at: string
  special_requests?: string
  internal_notes?: string
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'confirmed': return 'default'
    case 'pending': return 'secondary'
    case 'cancelled': return 'destructive'
    case 'completed': return 'outline'
    case 'no_show': return 'destructive'
    default: return 'secondary'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'confirmed': return CheckCircle
    case 'pending': return Clock
    case 'cancelled': return XCircle
    case 'completed': return CheckCircle
    case 'no_show': return XCircle
    default: return Clock
  }
}

export function BookingManagement() {
  const { bookings, loadBookings, properties, loadProperties } = useApp()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [activeTab, setActiveTab] = useState("all")
  const [loading, setLoading] = useState(true)
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        await Promise.all([loadBookings(), loadProperties()])
      } catch (error) {
        console.error('Failed to load booking data:', error)
      } finally {
        setLoading(false)
      }
    }
    
    loadData()
  }, [])

  // Enrich bookings with property information
  const enrichedBookings = bookings.map(booking => ({
    ...booking,
    property_title: properties.find(p => p.id === booking.property_id)?.title || 'Unknown Property'
  }))

  const filteredBookings = enrichedBookings.filter(booking => {
    const matchesSearch = booking.guest_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (booking.property_title?.toLowerCase().includes(searchTerm.toLowerCase())) ||
                         booking.id.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === "all" || booking.status === statusFilter
    const matchesTab = activeTab === "all" || booking.status === activeTab
    
    return matchesSearch && matchesStatus && matchesTab
  })

  const upcomingBookings = enrichedBookings.filter(booking => 
    booking.status === 'confirmed' && new Date(booking.check_in) > new Date()
  )

  const todayCheckIns = enrichedBookings.filter(booking => {
    const today = new Date().toISOString().split('T')[0]
    return booking.check_in === today && booking.status === 'confirmed'
  })

  const todayCheckOuts = enrichedBookings.filter(booking => {
    const today = new Date().toISOString().split('T')[0]
    return booking.check_out === today && booking.status === 'confirmed'
  })

  async function updateBookingStatus(bookingId: string, newStatus: string) {
    try {
      // This would call your backend API to update booking status
      console.log('Updating booking', bookingId, 'to status', newStatus)
      // await makeAPIRequest(`/bookings/${bookingId}`, {
      //   method: 'PUT',
      //   body: JSON.stringify({ status: newStatus })
      // })
      // await loadBookings() // Reload bookings after update
    } catch (error) {
      console.error('Failed to update booking:', error)
    }
  }

  if (loading) {
    return (
      <div className=" space-y-6">
        <div className="space-y-2">
          <div className="h-8 bg-muted rounded-lg w-64 animate-pulse"></div>
          <div className="h-4 bg-muted rounded w-96 animate-pulse"></div>
        </div>
          <div className="grid gap-4 md:grid-cols-3">
            {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 bg-muted rounded-xl animate-pulse"></div>
            ))}
          </div>
        <div className="h-12 bg-muted rounded-xl w-full max-w-lg animate-pulse"></div>
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-xl animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className=" space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Booking Management</h1>
        <p className="text-muted-foreground">
          Manage reservations and guest communications for all your properties.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Upcoming Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-krib-lime" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{upcomingBookings.length}</div>
            <p className="text-xs text-muted-foreground">Next 30 days</p>
          </CardContent>
        </Card>
        
        <Card className="shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm">Check-ins Today</CardTitle>
            <User className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{todayCheckIns.length}</div>
            <p className="text-xs text-muted-foreground">Guests arriving</p>
          </CardContent>
        </Card>
        
        <Card className="shadow-sm">
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
            <SelectItem value="no_show">No Show</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          More Filters
        </Button>
      </div>

      {/* Bookings Tabs - Using buttons for reliable click handling */}
      <div className="flex gap-2 p-1 bg-muted/40 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab("all")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
            activeTab === "all" 
              ? "bg-white shadow-sm text-foreground" 
              : "text-muted-foreground hover:text-foreground hover:bg-white/50"
          }`}
        >
          All Bookings
          <span className={`px-1.5 py-0.5 rounded text-xs ${activeTab === "all" ? "bg-muted" : "bg-white/60"}`}>
            {enrichedBookings.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab("confirmed")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
            activeTab === "confirmed" 
              ? "bg-white shadow-sm text-foreground" 
              : "text-muted-foreground hover:text-foreground hover:bg-white/50"
          }`}
        >
          Confirmed
          <span className={`px-1.5 py-0.5 rounded text-xs ${
            activeTab === "confirmed" 
              ? "bg-emerald-100 text-emerald-700" 
              : "bg-emerald-50 text-emerald-600"
          }`}>
            {enrichedBookings.filter(b => b.status === 'confirmed').length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab("pending")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
            activeTab === "pending" 
              ? "bg-white shadow-sm text-foreground" 
              : "text-muted-foreground hover:text-foreground hover:bg-white/50"
          }`}
        >
          Pending
          {enrichedBookings.filter(b => b.status === 'pending').length > 0 && (
            <span className="px-1.5 py-0.5 rounded text-xs bg-amber-100 text-amber-700">
              {enrichedBookings.filter(b => b.status === 'pending').length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab("completed")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
            activeTab === "completed" 
              ? "bg-white shadow-sm text-foreground" 
              : "text-muted-foreground hover:text-foreground hover:bg-white/50"
          }`}
        >
          Completed
          <span className={`px-1.5 py-0.5 rounded text-xs ${activeTab === "completed" ? "bg-muted" : "bg-white/60"}`}>
            {enrichedBookings.filter(b => b.status === 'completed').length}
          </span>
        </button>
      </div>

      {/* Booking content */}
      <div className="space-y-4">
          {filteredBookings.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No bookings found</h3>
                <p className="text-muted-foreground">
                  {bookings.length === 0 
                    ? "You don't have any bookings yet. Create some properties to start receiving bookings!"
                    : "Try adjusting your search or filter criteria."
                  }
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredBookings.map((booking) => {
                const StatusIcon = getStatusIcon(booking.status)
                
                return (
                  <Card key={booking.id}>
                    <CardContent className="">
                      <div className="flex items-start gap-4">
                        <div className="w-20 h-20 rounded-lg bg-gray-200 flex items-center justify-center">
                          <MapPin className="h-8 w-8 text-gray-400" />
                        </div>
                        
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="font-medium">{booking.property_title}</h3>
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
                                  <DropdownMenuItem onClick={() => {
                                    setSelectedBooking(booking)
                                    setShowDetailsModal(true)
                                  }}>
                                    View Details
                                  </DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => navigate('/dashboard/messages')}>
                                    Contact Guest
                                  </DropdownMenuItem>
                                  {booking.status === 'pending' && (
                                    <>
                                      <DropdownMenuItem onClick={() => updateBookingStatus(booking.id, 'confirmed')}>
                                        Confirm Booking
                                      </DropdownMenuItem>
                                      <DropdownMenuItem onClick={() => updateBookingStatus(booking.id, 'cancelled')}>
                                        Decline Booking
                                      </DropdownMenuItem>
                                    </>
                                  )}
                                  {booking.status === 'confirmed' && (
                                    <DropdownMenuItem onClick={() => updateBookingStatus(booking.id, 'cancelled')} className="text-destructive">
                                      Cancel Booking
                                    </DropdownMenuItem>
                                  )}
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
                                  <span>{booking.guest_name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Mail className="h-4 w-4" />
                                  <span>{booking.guest_email}</span>
                                </div>
                                {booking.guest_phone && (
                                  <div className="flex items-center gap-2">
                                    <Phone className="h-4 w-4" />
                                    <span>{booking.guest_phone}</span>
                                  </div>
                                )}
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-medium mb-1">Stay Details</h4>
                              <div className="space-y-1 text-muted-foreground">
                                <div>Check-in: {new Date(booking.check_in).toLocaleDateString()}</div>
                                <div>Check-out: {new Date(booking.check_out).toLocaleDateString()}</div>
                                <div>{booking.nights} nights • {booking.guests} guests</div>
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-medium mb-1">Booking Summary</h4>
                              <div className="space-y-1 text-muted-foreground">
                                <div>Total: AED {booking.total_amount}</div>
                                <div>Booked: {new Date(booking.created_at).toLocaleDateString()}</div>
                                {booking.special_requests && (
                                  <div className="text-xs">Special: {booking.special_requests}</div>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between pt-3 border-t">
                            {/* Communication Buttons */}
                            <div className="flex gap-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => navigate('/dashboard/messages')}
                            >
                              <Mail className="h-4 w-4 mr-2" />
                              Message Guest
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => navigate('/dashboard/properties')}
                            >
                              View Property
                            </Button>
                            </div>
                            
                            {/* Action Buttons */}
                            {booking.status === 'pending' && (
                              <div className="flex gap-2">
                                <Button 
                                  variant="destructive" 
                                  size="sm" 
                                  onClick={() => updateBookingStatus(booking.id, 'cancelled')}
                                >
                                  Decline
                                </Button>
                                <Button 
                                  size="sm" 
                                  className="bg-green-600 hover:bg-green-700"
                                  onClick={() => updateBookingStatus(booking.id, 'confirmed')}
                                >
                                  Confirm
                                </Button>
                              </div>
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
      </div>

      {/* Booking Details Modal */}
      <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Booking Details</DialogTitle>
          </DialogHeader>
          {selectedBooking && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Property</p>
                  <p className="font-medium">{selectedBooking.property_title}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <Badge variant={getStatusColor(selectedBooking.status)}>
                    {selectedBooking.status}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Guest Name</p>
                  <p className="font-medium">{selectedBooking.guest_name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Email</p>
                  <p className="font-medium">{selectedBooking.guest_email}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Phone</p>
                  <p className="font-medium">{selectedBooking.guest_phone || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Guests</p>
                  <p className="font-medium">{selectedBooking.guests}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Check-in</p>
                  <p className="font-medium">{new Date(selectedBooking.check_in).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Check-out</p>
                  <p className="font-medium">{new Date(selectedBooking.check_out).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Nights</p>
                  <p className="font-medium">{selectedBooking.nights}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Total</p>
                  <p className="font-medium text-green-600">AED {selectedBooking.total_amount}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Booked On</p>
                  <p className="font-medium">{new Date(selectedBooking.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Payment Status</p>
                  <p className="font-medium">{selectedBooking.payment_status || 'Pending'}</p>
                </div>
              </div>
              {selectedBooking.special_requests && (
                <div>
                  <p className="text-muted-foreground text-sm">Special Requests</p>
                  <p className="text-sm mt-1 p-2 bg-muted rounded">{selectedBooking.special_requests}</p>
                </div>
              )}
              <div className="flex gap-2 pt-4 border-t">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => navigate('/dashboard/messages')}
                >
                  <Mail className="h-4 w-4 mr-2" />
                  Message Guest
                </Button>
                {selectedBooking.status === 'pending' && (
                  <Button 
                    className="flex-1 bg-green-600 hover:bg-green-700"
                    onClick={() => {
                      updateBookingStatus(selectedBooking.id, 'confirmed')
                      setShowDetailsModal(false)
                    }}
                  >
                    Confirm Booking
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}